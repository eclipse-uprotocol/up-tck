# -------------------------------------------------------------------------
#
# Copyright (c) 2023 General Motors GTO LLC
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
# SPDX-FileCopyrightText: 2023 General Motors GTO LLC
# SPDX-License-Identifier: Apache-2.0
#
# -------------------------------------------------------------------------

import socket
import selectors
import threading
import logging
from collections import defaultdict
from typing import Dict
from google.protobuf.any_pb2 import Any

from uprotocol.proto.uattributes_pb2 import UAttributes
from uprotocol.proto.uri_pb2 import UUri
from uprotocol.proto.umessage_pb2 import UMessage
from uprotocol.proto.ustatus_pb2 import UStatus
from uprotocol.transport.ulistener import UListener
from uprotocol.proto.upayload_pb2 import UPayload
from uprotocol.rpc.rpcmapper import RpcMapper

from up_client_socket_python.transport_layer import TransportLayer
from up_client_socket_python.utils.socket_message_processing_utils import receive_socket_data, convert_bytes_to_string, convert_json_to_jsonstring, convert_jsonstring_to_json, convert_str_to_bytes, protobuf_to_base64, base64_to_protobuf_bytes, send_socket_data

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

    Assumption: For every connection between Test Agent (TA) and Test Manager (TM), 
    message passing is blocking/sychronous 

    """
    def __init__(self, ip_addr: str, port: int, utransport: TransportLayer) -> None:
        """
        @param ip_addr: Test Manager's ip address
        @param port: Test Manager's port number
        @param utransport: Real message passing medium (sockets)
        """
        
        # Real lowlevel implementation (ex: Ulink's UTransport, Zenoh, etc).
        self.utransport: TransportLayer = utransport

        # Bc every sdk connection is unqiue, map the socket connection.
        self.sdk_to_test_agent_socket: Dict[str, socket.socket] = defaultdict(None)
        self.sdk_to_received_ustatus: Dict[str, UStatus] = defaultdict(lambda: None)  # maybe thread safe
        self.sdk_to_received_ustatus_lock = threading.Lock()

        self.sock_addr_to_sdk: Dict[tuple[str, int], str] = defaultdict(str) 

        self.possible_received_protobufs = [UMessage(), UStatus()]

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
    
    def __accept(self, server, mask):
        print("Waiting on Test Agent connection ...")
        ta_socket, addr = server.accept() 
        print('accepted', ta_socket, 'from', addr)
        
        # Never wait for the operation to complete. 
        # So when call send(), it will put as much data in the buffer as possible and return.
        ta_socket.setblocking(False)
        # Register client socket so selector can monitor for incoming TA data and calls provided callback()
        self.selector.register(ta_socket, selectors.EVENT_READ, self.__receive)
    
    def __receive(self, ta_socket: socket.socket, mask):
        # 'mask' contains the events taht are ready
        
        # print(ta_socket.getsockname())  # server's ip and port
        # print(ta_socket.getpeername())  # client's ip and port

        print("__receive")
        recv_data: bytes = receive_socket_data(ta_socket)
        
        print("recv_data", recv_data)
        json_str: str = convert_bytes_to_string(recv_data) 
        json_msg: Dict[str, str] = convert_jsonstring_to_json(json_str) 

        if "SDK_name" in json_msg:
            sdk: str = json_msg["SDK_name"].lower().strip()
            
            ta_addr: tuple[str, int] = ta_socket.getpeername()
            self.sock_addr_to_sdk[ta_addr] = sdk
            # Store new SDK's socket connection
            self.sdk_to_test_agent_socket[sdk] = ta_socket
            
            print("Initialized new client socket!")
            print(self.sock_addr_to_sdk)

        elif "action" in json_msg and json_msg["action"] == "uStatus":
            ta_addr: tuple[str, int] = ta_socket.getpeername()
            sdk = self.sock_addr_to_sdk[ta_addr]
            
            # update status if received UStatus message
            umsg_base64: str = json_msg["message"]
            protobuf_serialized_data: bytes = base64_to_protobuf_bytes(umsg_base64)  
            status: UStatus = RpcMapper.unpack_payload(Any(value=protobuf_serialized_data), UStatus)
            print("action Ustatus")
            
            self.__save_status(sdk, status)
            print(self.sdk_to_received_ustatus)
        
        elif "action" in json_msg and json_msg["action"] == "onReceive":
            ta_addr: tuple[str, int] = ta_socket.getpeername()
            sdk = self.sock_addr_to_sdk[ta_addr]
            
            # update status if received UStatus message
            umsg_base64: str = json_msg["message"]
            protobuf_serialized_data: bytes = base64_to_protobuf_bytes(umsg_base64)  
            onreceive_umsg: UMessage = RpcMapper.unpack_payload(Any(value=protobuf_serialized_data), UMessage)
        
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
    
    def listen_for_client_connections(self):
        """
        Listens for Test Agent Connections and creates a thread to start the init process
        """
        '''
        while True:
            print("Waiting on Test Agent connection ...")
            clientsocket, _ = self.server.accept()

            thread = threading.Thread(target=self.__initialize_new_client_connection, args=(clientsocket, ))
            print(clientsocket)
            thread.start()
        '''
        
        while True:
            # Wait until some registered file objects or sockets become ready, or the timeout expires.
            events = self.selector.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)

    def __initialize_new_client_connection(self, test_agent_socket: socket.socket):
        """
        Once a new Test Agent (TA) connects to Test Manager (TM), TA should send immediately 
        an initalize message containing its SDK type.
        Keep that received and unqiue SDK, so TM can find the connection later

        @param test_agent_socket: Test Agent socket connection
        """
        recv_data: bytes = receive_socket_data(test_agent_socket)

        json_str: str = convert_bytes_to_string(recv_data) 
        json_msg: Dict[str, str] = convert_jsonstring_to_json(json_str) 

        if "SDK_name" in json_msg:
            sdk: str = json_msg["SDK_name"].lower().strip()

            # Store new SDK's socket connection
            self.sdk_to_test_agent_socket[sdk] = test_agent_socket
        else:
            raise Exception("new client connection didn't initally send sdk name")
        
        print("Initialized new client socket!")
        print(self.sdk_to_test_agent_socket)

    def __send_to_test_agent(self, test_agent_socket: socket.socket, command: str, umsg: UMessage):
        """
        Contains data preprocessing and sending UMessage steps to Test Agent
        @param test_agent_socket: Test Agent Socket
        @param command: message's action-type
        """
        json_message = {
            "action": command,
            "message": protobuf_to_base64(umsg) 
        }

        json_message_str: str = convert_json_to_jsonstring(json_message) 

        message: bytes = convert_str_to_bytes(json_message_str) 

        send_socket_data(test_agent_socket, message) 
        print("SENT!")

    def __receive_from_test_agent(self, test_agent_socket: socket.socket, message_protobuf_class):
        """
        Contains UStatus receiving data preprocessing and sending UMessage steps to Test Agent
        @param test_agent_socket: Test Agent Socket
        """
        response_data: bytes = receive_socket_data(test_agent_socket)
        
        if not response_data:
            print('closing', test_agent_socket)
            self.selector.unregister(test_agent_socket)
            test_agent_socket.close()
            return
            
        json_str: str = convert_bytes_to_string(response_data)
        json_msg: Dict[str, str] = convert_jsonstring_to_json(json_str) 
        
        print("-----------------------json_msg----------------------")
        print(json_msg)
        print("-----------------------------------------")

        umsg_base64: str = json_msg["message"]
        
        protobuf_serialized_data: bytes = base64_to_protobuf_bytes(umsg_base64)  

        filled_protobuf_obj = RpcMapper.unpack_payload(Any(value=protobuf_serialized_data), message_protobuf_class)

        return filled_protobuf_obj
    
    def listen_forever(self, test_agent_socket: socket.socket):
        """_summary_
        """
        while True:
            recv_data: bytes = receive_socket_data(test_agent_socket) 
            
            if recv_data == b"":
                continue

    def send_command(self, sdk_name: str, command: str,  topic: UUri, payload: UPayload, attributes: UAttributes) -> UStatus:
        """
        Sends "send" message to Test Agent
        @param sdk_name: Test Agent's SDK type
        @param command: type of message
        @param topic: part of UMessage
        @param payload: part of UMessage
        @param attributes: part of UMessage
        """
        sdk_name = sdk_name.lower().strip()

        if sdk_name == "python":
            # Send message thru real medium (ulink's UTransport)
            status: UStatus = self.utransport.send(topic, payload, attributes)

            # test_agent_socket: socket.socket = self.sdk_to_test_agent_socket["java"]  ## NOTE: NEED fixings

            # response_data: bytes = receive_socket_data(test_agent_socket)

            # resp_umsg: UMessage = RpcMapper.unpack_payload(Any(value=response_data), UMessage)
            
        else:
            
            # Send message to Test Agent
            umsg: UMessage = UMessage(source=topic, attributes=attributes, payload=payload)
            test_agent_socket: socket.socket = self.sdk_to_test_agent_socket[sdk_name]

            self.__send_to_test_agent(test_agent_socket, command, umsg)
            '''
            status: UStatus = self.__receive_from_test_agent(test_agent_socket, UStatus)
            '''
            
            status: UStatus = self.__pop_status(sdk_name)            
            
            
        return status

    def register_listener_command(self, sdk_name: str, command: str, topic: UUri, listener: UListener):
        """
        Sends "registerListener" message to Test Agent
        @param sdk_name: Test Agent's SDK type
        @param command: type of message
        @param topic: part of UMessage
        @param listener: handler when UTransport receives data from registered topic
        """
        sdk_name = sdk_name.lower().strip()
        if sdk_name == "python":
            # ulink registers to current topic
            status: UStatus = self.utransport.register_listener(topic, listener)

        else:
            # Send registerListener mesg to Test Agent
            umsg: UMessage = UMessage(source=topic)

            test_agent_socket: socket.socket = self.sdk_to_test_agent_socket[sdk_name]

            self.__send_to_test_agent(test_agent_socket, command, umsg)
            
            '''
            status: UStatus = self.__receive_from_test_agent(test_agent_socket, UStatus)
            '''
            
            status: UStatus = self.__pop_status(sdk_name)          

        return status