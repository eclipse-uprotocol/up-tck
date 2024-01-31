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

from up_tck_python.up_client_socket_python.transport_layer import TransportLayer
from up_tck_python.utils.socket_message_processing_utils import receive_socket_data, convert_bytes_to_string, convert_json_to_jsonstring, convert_jsonstring_to_json, convert_str_to_bytes, protobuf_to_base64, base64_to_protobuf_bytes, send_socket_data

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

        self.possible_received_protobufs = [UMessage(), UStatus()]

        # Creates test manager socket server so it can accept connections from Test Agents.
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Binds to socket server.
        self.server.bind((ip_addr, port))  
        # Puts the socket into listening mode.
        self.server.listen(5)  
    
    def listen_for_client_connections(self):
        """
        Listens for Test Agent Connections and creates a thread to start the init process
        """
        while True:
            print("Waiting on Test Agent connection ...")
            clientsocket, _ = self.server.accept()

            thread = threading.Thread(target=self.__initialize_new_client_connection, args=(clientsocket, ))
            print(clientsocket)
            thread.start()

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

        print("SENDING...")
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
        json_str: str = convert_bytes_to_string(response_data)
        json_msg: Dict[str, str] = convert_jsonstring_to_json(json_str) 
        
        print("-----------------------json_msg----------------------")
        print(json_msg)
        print("-----------------------------------------")

        umsg_base64: str = json_msg["message"]
        
        protobuf_serialized_data: bytes = base64_to_protobuf_bytes(umsg_base64)  

        filled_protobuf_obj = RpcMapper.unpack_payload(Any(value=protobuf_serialized_data), message_protobuf_class)

        return filled_protobuf_obj

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

            test_agent_socket: socket.socket = self.sdk_to_test_agent_socket["java"]  ## NOTE: NEED fixings

            # response_data: bytes = receive_socket_data(test_agent_socket)

            # resp_umsg: UMessage = RpcMapper.unpack_payload(Any(value=response_data), UMessage)
            
            onreceive_umsg: UMessage = self.__receive_from_test_agent(test_agent_socket, UMessage)
            print("---------------------------------OnReceive response from Test Agent!---------------------------------")
            print(onreceive_umsg)
            print("-----------------------------------------------------------------------------------------------------")

        else:
            # Send message to Test Agent
            umsg: UMessage = UMessage(source=topic, attributes=attributes, payload=payload)
            # status: UStatus = self.send_msg_to_test_agent(sdk_name, command, umsg)
            test_agent_socket: socket.socket = self.sdk_to_test_agent_socket[sdk_name]

            self.__send_to_test_agent(test_agent_socket, command, umsg)
            status: UStatus = self.__receive_from_test_agent(test_agent_socket, UStatus)
        
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

            # status: UStatus = self.send_msg_to_test_agent(sdk_name, command, umsg)
            test_agent_socket: socket.socket = self.sdk_to_test_agent_socket[sdk_name]

            self.__send_to_test_agent(test_agent_socket, command, umsg)
            status: UStatus = self.__receive_from_test_agent(test_agent_socket, UStatus)

        return status