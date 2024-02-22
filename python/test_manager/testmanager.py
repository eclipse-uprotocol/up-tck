# -------------------------------------------------------------------------
#
# Copyright (c) 2024 General Motors GTO LLC
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
# SPDX-FileType: SOURCE
# SPDX-FileCopyrightText: 2024 General Motors GTO LLC
# SPDX-License-Identifier: Apache-2.0
#
# -------------------------------------------------------------------------

import socket
import selectors
import threading
import logging
import re
from collections import defaultdict
from typing import Dict, List
from google.protobuf.any_pb2 import Any

from uprotocol.proto.uattributes_pb2 import UAttributes, UPriority, UMessageType
from uprotocol.proto.uri_pb2 import UUri, UAuthority, UEntity, UResource
from uprotocol.proto.umessage_pb2 import UMessage
from uprotocol.proto.ustatus_pb2 import UStatus
from uprotocol.transport.ulistener import UListener
from uprotocol.proto.cloudevents_pb2 import CloudEvent
from uprotocol.proto.uuid_pb2 import UUID
from uprotocol.proto.upayload_pb2 import UPayload, UPayloadFormat
from uprotocol.transport.builder.uattributesbuilder import UAttributesBuilder
from uprotocol.rpc.rpcmapper import RpcMapper

from up_client_socket_python.transport_layer import TransportLayer
from up_client_socket_python.utils.socket_message_processing_utils import receive_socket_data, convert_bytes_to_string, convert_json_to_jsonstring, convert_jsonstring_to_json, convert_str_to_bytes, protobuf_to_base64, base64_to_protobuf_bytes, send_socket_data

from up_client_socket_python.utils.grammar_parsing_utils import get_priority, get_umessage_type

logging.basicConfig(format='%(asctime)s %(message)s')
# Create logger
logger = logging.getLogger('simple_example')
logger.setLevel(logging.DEBUG)


class SocketTestManager():
    """
    Validates data received from Test Agent 
    Example: can validate different message-passing mediums (ex: up-client-socket-xxx, zenoh, ...) 
    from different devices.

    Test Manager acts as a server that interoperable (ex: Java, C++, Rust, etc.) Test Agents will connect to.
    These connections will later do be used for stress testing, testing the latencies in sending messages in a high
    message passing sending rates, the size of messages, and the implementation of the core SDK

    Assumption: For every connection between Test Agent (TA) and Test Manager (TM), 
    message passing is blocking/sychronous 

    """
    def __init__(self, ip_addr: str, port: int, utransport: TransportLayer) -> None:
        """Starts Test Manager by creating the server and accepting Test Agent client socket connections

        Args:
            ip_addr (str): Test Manager's ip address
            port (int): Test Manager's port number
            utransport (TransportLayer): Real message passing medium (sockets)
        """

        self.received_umessage: UMessage = None

        # Lowlevel transport implementation (ex: Ulink's UTransport, Zenoh, etc).
        self.utransport: TransportLayer = utransport

        # Bc every sdk connection is unqiue, map the socket connection.
        self.sdk_to_test_agent_socket: Dict[str, socket.socket] = defaultdict(socket.socket)
        self.sdk_to_received_ustatus: Dict[str, UStatus] = defaultdict(lambda: None)  # maybe thread safe
        self.sdk_to_received_ustatus_lock = threading.Lock()

        self.sdk_to_test_agent_socket_lock = threading.Lock()

        self.sock_addr_to_sdk: Dict[tuple[str, int], str] = defaultdict(str) 

        # Creates test manager socket server so it can accept connections from Test Agents.
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Binds to socket server.
        self.server.bind((ip_addr, port))  
        # Puts the socket into listening mode.
        self.server.listen(100)  
        
        self.server.setblocking(False)
        
        # Selector allows high-level and efficient I/O multiplexing, built upon the select module primitives.
        self.selector = selectors.DefaultSelector()
        # Register server socket so selector can monitor for incoming client conn. and calls provided callback()
        self.selector.register(self.server, selectors.EVENT_READ, self.__accept)
    
    def __accept(self, server: socket.socket):
        """Accepts Test Agent client socket connect requests and listens for incoming data from the new TA conn.

        Args:
            server (socket.socket): Test Manager server
        """
        ta_socket, addr = server.accept() 
        print('accepted', ta_socket, 'from', addr)
        
        # Never wait for the operation to complete. 
        # So when call send(), it will put as much data in the buffer as possible and return.
        ta_socket.setblocking(False)
        # Register client socket so selector can monitor for incoming TA data and calls provided callback()
        self.selector.register(ta_socket, selectors.EVENT_READ, self.__receive_from_test_agent)
    
    def __receive_from_test_agent(self, ta_socket):
        """handles incoming json data from Test Agent

        Args:
            ta_socket (socket.socket): <SDK> Test Agent 
        """

            
        recv_data: bytes = receive_socket_data(ta_socket)
        
        # if client socket closed connection, then close on server endpoint too
        if recv_data == b'':
            try: 
                ta_addr: tuple[str, int] = ta_socket.getpeername()
                sdk: str = self.sock_addr_to_sdk[ta_addr] 
                
                self.close_ta(sdk)
                
                del self.sock_addr_to_sdk[ta_addr]
            except OSError as oserr:
                print(oserr)
            return

        json_str: str = convert_bytes_to_string(recv_data) 

        # in case if json messages are concatenated, we are splitting the json data and handling it separately
        data_within_json : List[str]= re.findall('{(.+?)}', json_str)  # {json, action: ..., messge: "...."}{json, action: status messge: "...."}
        for recv_json_data in data_within_json:
            json_msg: Dict[str, str] = convert_jsonstring_to_json("{" + recv_json_data + "}")
            self.__handle_recv_json_message(json_msg, ta_socket)

    def __handle_recv_json_message(self, json_msg: Dict[str, str], ta_socket: socket.socket):
        """Runtime Handler for different type of incoming json messages

        Args:
            json_msg (Dict[str, str]): received json data
            ta_socket (socket.socket): Test Agent socket connection

        Raises:
            Exception: if dont recognize certain received json messages
        """
        if "SDK_name" in json_msg:
            sdk: str = json_msg["SDK_name"].lower().strip()
            
            ta_addr: tuple[str, int] = ta_socket.getpeername()
            self.sock_addr_to_sdk[ta_addr] = sdk
            
            # Store new SDK's socket connection
            self.sdk_to_test_agent_socket_lock.acquire()
            self.sdk_to_test_agent_socket[sdk] = ta_socket
            self.sdk_to_test_agent_socket_lock.release()
            
            print("Initialized new client socket!",sdk, ta_addr )
            return

        ta_addr: tuple[str, int] = ta_socket.getpeername()
        sdk: str = self.sock_addr_to_sdk[ta_addr]

        if "action" in json_msg and json_msg["action"] == "uStatus":
            # update status if received UStatus message
            umsg_base64: str = json_msg["message"]
            protobuf_serialized_data: bytes = base64_to_protobuf_bytes(umsg_base64)  
            status: UStatus = RpcMapper.unpack_payload(Any(value=protobuf_serialized_data), UStatus)
            
            self.__save_status(sdk, status)
        
        elif "action" in json_msg and json_msg["action"] == "onReceive":
            # update status if received UStatus message
            umsg_base64: str = json_msg["message"]
            protobuf_serialized_data: bytes = base64_to_protobuf_bytes(umsg_base64)  
            onreceive_umsg: UMessage = RpcMapper.unpack_payload(Any(value=protobuf_serialized_data), UMessage)

            self.received_umessage = onreceive_umsg

            print("---------------------------------OnReceive response from Test Agent!---------------------------------")
            print(onreceive_umsg)
            print("-----------------------------------------------------------------------------------------------------")


        else:
            raise Exception("new client connection didn't initally send sdk name")
        
    def __save_status(self, sdk_name: str, status: UStatus):
        self.sdk_to_received_ustatus_lock.acquire()
        self.sdk_to_received_ustatus[sdk_name] = status 
        self.sdk_to_received_ustatus_lock.release()
    
    def __pop_status(self, sdk_name: str) -> UStatus:
        # blocking: wait till received ustatus
        while self.sdk_to_received_ustatus[sdk_name] is None:
            continue
            
        self.sdk_to_received_ustatus_lock.acquire()
        status: UStatus = self.sdk_to_received_ustatus.pop(sdk_name)
        self.sdk_to_received_ustatus_lock.release()
        
        return status
    
    def has_sdk_connection(self, sdk_name: str) -> bool:
        if sdk_name == "self":
            return True
        return sdk_name in self.sdk_to_test_agent_socket
        
    def listen_for_client_connections(self):
        """
        Listens for Test Agent Connections and creates a thread to start the init process
        """
        
        while True:
            # Wait until some registered file objects or sockets become ready, or the timeout expires.
            events = self.selector.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj)

    def __send_to_test_agent(self, test_agent_socket: socket.socket, command: str, umsg: UMessage):
        """ Contains data preprocessing and sending UMessage steps to Test Agent

        Args:
            test_agent_socket (socket.socket): Test Agent Socket
            command (str): message's action-type
            umsg (UMessage): the raw protobuf message 
        """
        json_message = {
            "action": command,
            "message": protobuf_to_base64(umsg) 
        }

        json_message_str: str = convert_json_to_jsonstring(json_message) 

        message: bytes = convert_str_to_bytes(json_message_str) 

        send_socket_data(test_agent_socket, message) 
        
    def request(self, sdk_ta_destination: str, command: str, message: UMessage) -> UStatus:
        """Sends different requests to a specific SDK Test Agent

        Args:
            sdk_ta_destination (str): SDK Test Agent
            command (str): send, registerlistener, unregisterlistener, invokemethod
            message (UMessage): message data to send to the SDK Test Agent

        Returns:
            UStatus: response Status
        """
        sdk_ta_destination = sdk_ta_destination.lower().strip()

        test_agent_socket: socket.socket = self.sdk_to_test_agent_socket[sdk_ta_destination]

        self.__send_to_test_agent(test_agent_socket, command, message)
        
        status: UStatus = self.__pop_status(sdk_ta_destination) 
        return status

    def receive_action_request(self, json_request: Dict) -> UStatus:
        """Runtime command to send to Test Agent based on request json

        Args:
            json_request (Dict): the command that needs to run but formatted in a json
            listener (UListener): required listener if need to run registerListener()

        Returns:
            UStatus: the status after doing a command
        """
    
        sdk_name: str = json_request["ue"][0]
        command: str = json_request["action"][0].lower()
        
        name: str = json_request['uri.entity.name'][0]
        entity = UEntity(name=name)
        
        name: str = json_request['uri.resource.name'][0]
        instance: str = json_request['uri.resource.instance'][0]
        message: str = json_request['uri.resource.message'][0]
        resource: UResource = UResource(name=name, instance=instance, message=message)
        
        topic: UUri = UUri(entity=entity, resource=resource )
        
        if command == "send":
            format: str = json_request['payload.format'][0]
            format = format.lower()
            if format == "cloudevent":
                values: Dict = json_request["payload.value"]
                id: str = values["id"][0]
                source: str = values["source"][0]

                cloudevent = CloudEvent(spec_version="1.0", source=source, id=id)
                any_obj = Any()
                any_obj.Pack(cloudevent)
                proto: bytes = any_obj.SerializeToString()

            elif format == "protobuf":
                proto: str = json_request["payload.value"][0]
                proto: bytes = proto.encode()
            else:
                raise Exception("payload.format's provided value not handleable")

            upayload: UPayload = UPayload(format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF, value=proto)


            priority: str = json_request['attributes.priority'][0]
            priority: UPriority = get_priority(priority)

            umsg_type: str = json_request['attributes.type'][0]
            umsg_type: UMessageType = get_umessage_type(umsg_type)

            if 'attributes.id' in json_request:
                id_num: int = int(json_request['attributes.id'][0])
                id: UUID = UUID(msb=id_num)

            sink: UUri = UUri()
            if "attributes.sink" in json_request:
                sink: str = json_request['attributes.sink'][0]
                sink_bytes: bytes = sink.encode()
                #sink.ParseFromString(sink_bytes)

            attributes: UAttributes = UAttributesBuilder(id, umsg_type, priority).withSink(sink).build()
            # return self.send_command(sdk_name, command, topic, upayload, attributes)
            umsg: UMessage = UMessage(source=topic, attributes=attributes, payload=upayload)
            return self.request(sdk_name, command, umsg)

        elif command == "registerlistener":
            umsg: UMessage = UMessage(source=topic)
            # return self.register_listener_command(sdk_name, command, topic, listener)
            return self.request(sdk_name, command, umsg)
        
        else:
            raise Exception("action value not handled!")   
        
    def close(self):
        """Close the selector / test manager's server, 
        BUT need to free its individual SDK TA connections using self.close_ta(sdk) first
        """
        self.selector.close()
    
    def close_ta(self, sdk_name: str):
        print(f"Closing {sdk_name} connection")
        
        # if havent deleted and closed socket client already...
        if sdk_name in self.sdk_to_test_agent_socket:
        
            self.sdk_to_test_agent_socket_lock.acquire()
            ta_socket: socket.socket = self.sdk_to_test_agent_socket[sdk_name]
            
            del self.sdk_to_test_agent_socket[sdk_name]
            self.sdk_to_test_agent_socket_lock.release()

            # Stop monitoring socket/fileobj. A file object shall be unregistered prior to being closed.
            self.selector.unregister(ta_socket)
            ta_socket.close()