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
import json
import base64
from google.protobuf.any_pb2 import Any

from uprotocol.proto.uattributes_pb2 import UAttributes
from uprotocol.proto.uri_pb2 import UUri
from uprotocol.proto.umessage_pb2 import UMessage
from uprotocol.proto.ustatus_pb2 import UStatus
from uprotocol.transport.ulistener import UListener
from uprotocol.proto.upayload_pb2 import UPayload
from uprotocol.transport.utransport import UTransport

from up_tck_python.test_manager.testmanager import TestManager
from up_tck_python.up_client_socket_python.socket_utransport import SocketUTransport

logging.basicConfig(format='%(asctime)s %(message)s')
# Create logger
logger = logging.getLogger('simple_example')
logger.setLevel(logging.DEBUG)


def send_socket_data(s: socket.socket , msg: bytes):
    s.send(msg)

def receive_socket_data(s: socket.socket) -> bytes:
    bytes_mesg_len: int = 32767
    return s.recv(bytes_mesg_len)

def serialize_protobuf_to_base64(obj: Any):
    return base64.b64encode(obj.SerializeToString()).decode('ASCII')

def convert_bytes_to_string(data: bytes) -> str:
    return data.decode()

def convert_jsonstring_to_json(jsonstring: str) -> Dict[str, str]:
    return json.loads(jsonstring) 

def convert_json_to_jsonstring(j: Dict[str, str]) -> str:
    return json.dumps(j)

def convert_str_to_bytes(string: str) -> bytes:
    return str.encode(string) 

class SocketTestManager(TestManager):
    """
    Validates data received from Test Agent 
    Example: can validate different message-passing mediums (ex: up-client-socket-xxx, zenoh, ...) 
    from different devices.

    Test Manager acts as a server that interoperable (ex: Java, C++, Rust, etc.) Test Agents will connect to.

    Assumption: For every connection between Test Agent (TA) and Test Manager (TM), 
    message passing is blocking/sychronous 

    """
    def __init__(self, ip_addr: str, port: int, utransport: UTransport) -> None:
        """
        @param ip_addr: Test Manager's ip address
        @param port: Test Manager's port number
        @param utransport: Real message passing medium (sockets)
        """
        
        # Real lowlevel implementation (ex: Ulink's UTransport, Zenoh, etc).
        self.utransport: SocketUTransport = utransport

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
        while True:
            print("Waiting on Test Agent connection ...")
            clientsocket, _ = self.server.accept()

            thread = threading.Thread(target=self.__initialize_new_client_connection, args=(clientsocket, ))
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
    '''
    def send_to_client(self, test_agent_socket: socket.socket, json_message: Dict[str, str]):
        # convert a dictionary/map -> JSON string
        json_message_str: str = convert_json_to_jsonstring(json_message) # json.dumps(json_message)

        print("sending", json_message)

        # to send data over a socket, we have to send in bytes --> convert JSON STRING into bytes
        message: bytes = convert_str_to_bytes(json_message_str)  #str.encode(json_message_str)   # send this to socket in bytes
        
        send_socket_data(test_agent_socket, message)  # client.send(message)
    '''

    '''
    def __parse_socket_received_data(self, recv_data: bytes) -> bytes:
        json_str: str = recv_data.decode() # decode bytes -> str like JSON 
        json_msg: Dict[str, str] = convert_jsonstring_to_json(json_str)  ##json.loads(json_str)  # conver JSON Str -> JSON/Dictionary/Map

        umsg_base64: str = json_msg["message"]
        protobuf_serialized_data: bytes = base64.b64decode(umsg_base64)  # decode base64 encoding --> serialized protobuf 

        return protobuf_serialized_data
    '''

    def __send_to_test_agent(self, test_agent_socket: socket.socket, command: str, umsg: UMessage):
        """
        Contains data preprocessing and sending UMessage steps to Test Agent
        ## NOTE: refrain from writing your own logic for serialization or deserialization instead you should use sdk methods to do these tasks.
        @param test_agent_socket: Test Agent Socket
        @param command: message's action-type
        """
        json_message = {
            "action": command,
            "message": serialize_protobuf_to_base64(umsg)  # NOTE NEEDs fixing
        }

        print("SENDING...")
        json_message_str: str = convert_json_to_jsonstring(json_message) 

        message: bytes = convert_str_to_bytes(json_message_str) 

        send_socket_data(test_agent_socket, message) 
        print("SENT!")

    def __receive_from_test_agent(self, test_agent_socket: socket.socket):
        """
        Contains UStatus receiving data preprocessing and sending UMessage steps to Test Agent
        @param test_agent_socket: Test Agent Socket
        """
        response_data: bytes = receive_socket_data(test_agent_socket)

        json_str: str = convert_bytes_to_string(response_data)

        json_msg: Dict[str, str] = convert_jsonstring_to_json(json_str) 

        umsg_base64: str = json_msg["message"]
        protobuf_serialized_data: bytes = base64.b64decode(umsg_base64)  # decode base64 encoding --> serialized protobuf 

        status = UStatus()
        status.ParseFromString(protobuf_serialized_data)
        return status
    
    '''
    def send_msg_to_test_agent(self, sdk_name:str, command: str, umsg: UMessage):
        # Send to Test Agent
        ## NOTE: refrain from writing your own logic for serialization or deserialization instead you should use sdk methods to do these tasks.
        json_message = {
            "action": command,
            "message": serialize_protobuf_to_base64(umsg)
        }

        print("SENDING...")
        clientsocket: socket.socket = self.sdk_to_test_agent_socket[sdk_name]
        self.send_to_client(clientsocket, json_message)
        print("SENT...")

        response_data: bytes = clientsocket.recv(32767)

        protobuf_serialized_data: bytes = self.__parse_socket_received_data(response_data)

        status = UStatus()
        status.ParseFromString(protobuf_serialized_data)

        return status
    '''

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

            response_data: bytes = receive_socket_data(test_agent_socket)

            #unpack
            resp_umsg: UMessage = UMessage()
            resp_umsg.ParseFromString(response_data)
            print("---------------------------------OnReceive response from Test Agent!---------------------------------")
            print(resp_umsg)
            print("-----------------------------------------------------------------------------------------------------")
        else:
            # Send message to Test Agent
            umsg: UMessage = UMessage(source=topic, attributes=attributes, payload=payload)
            # status: UStatus = self.send_msg_to_test_agent(sdk_name, command, umsg)
            test_agent_socket: socket.socket = self.sdk_to_test_agent_socket[sdk_name]

            self.__send_to_test_agent(test_agent_socket, command, umsg)
            status: UStatus = self.__receive_from_test_agent(test_agent_socket)
        
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
            status: UStatus = self.__receive_from_test_agent(test_agent_socket)

        return status