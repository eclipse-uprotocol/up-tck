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

def serialize_protobuf_to_base64(obj: Any):
    return base64.b64encode(obj.SerializeToString()).decode('ASCII')

class SocketTestManager(TestManager):
    def __init__(self, ip_addr: str, port: int, utransport: UTransport) -> None:
        """
        The test server that the Test Agent will connect to
        Idea: acts as validator to validate data sent in up-client-socket-xxx

        """

        self.utransport: SocketUTransport = utransport
        self.sdk_to_port: Dict[str, int] = defaultdict(int)
        self.sdk_to_socket: Dict[str, socket.socket] = defaultdict(None)
        self.possible_received_protobufs = [UMessage(), UStatus()]

        # Creates test manager socket object.
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Binds to socket server.
        self.server.bind((ip_addr, port))  

        # Puts the socket into listening mode.
        self.server.listen(5)  
    
    def listen_for_client_connections(self):
        while True:
            print("waiting on client connection ...")
            clientsocket, (client_ip, client_port) = self.server.accept()

            thread = threading.Thread(target=self.initialize_new_client_connection, args=(clientsocket, client_port))
            thread.start()

    def initialize_new_client_connection(self, clientsocket: socket.socket, client_port: int):
        recv_data: bytes = clientsocket.recv(32767)

        json_str: str = recv_data.decode() # decode bytes -> str like JSON 
        json_msg: Dict[str, str] = json.loads(json_str)  # conver JSON Str -> JSON/Dictionary/Map

        # during init, should receive a SDK_name json msg immediately after connection
        if "SDK_name" in json_msg:
            sdk: str = json_msg["SDK_name"]
 
            self.sdk_to_port[sdk] = client_port
            self.sdk_to_socket[sdk] = clientsocket
        else:
            raise Exception("new client connection didn't initally send sdk name")
        
        print("Initialized new client socket!")
        print(self.sdk_to_socket)
    
    def send_to_client(self, client: socket.socket, json_message: Dict[str, str]):
        # convert a dictionary/map -> JSON string
        json_message_str: str = json.dumps(json_message)

        print("sending", json_message)

         # to send data over a socket, we have to send in bytes --> convert JSON STRING into bytes
        message: bytes = str.encode(json_message_str)   # send this to socket in bytes
        
        client.send(message)

    def __parse_socket_received_data(self, recv_data: bytes) -> bytes:
        json_str: str = recv_data.decode() # decode bytes -> str like JSON 
        json_msg: Dict[str, str] = json.loads(json_str)  # conver JSON Str -> JSON/Dictionary/Map

        umsg_base64: str = json_msg["message"]
        protobuf_serialized_data: bytes = base64.b64decode(umsg_base64)  # decode base64 encoding --> serialized protobuf 

        return protobuf_serialized_data
    
    def send_msg_to_test_agent(self, sdk_name:str, command: str, umsg: UMessage):
        # Send to Test Agent
        print("yo")
        json_message = {
            "action": command,
            "message": serialize_protobuf_to_base64(umsg)
        }

        print("SENDING...")
        clientsocket: socket.socket = self.sdk_to_socket[sdk_name]
        self.send_to_client(clientsocket, json_message)
        print("SENT...")

        response_data: bytes = clientsocket.recv(32767)

        protobuf_serialized_data: bytes = self.__parse_socket_received_data(response_data)

        status = UStatus()
        status.ParseFromString(protobuf_serialized_data)

        return status

    def send_command(self, sdk_name: str, command: str,  topic: UUri, payload: UPayload, attributes: UAttributes) -> UStatus:
        """
        sends data to TA params (action/command and complete Umessage)
        BLOCKING/SYNCHRONOUS call!!! So wait after send for a UStatus b/c theres no msg id to map it to after its done

        SCenarios (TRUTH):
        SDKS are always unique
        get socket thru the sdk then send
        """
        if sdk_name.lower() == "python":
            # send thru Socket UTransport
            status: UStatus = self.utransport.send(topic, payload, attributes)
        else:
            # Send to Test Agent
            umsg: UMessage = UMessage(source=topic, attributes=attributes, payload=payload)
            status: UStatus = self.send_msg_to_test_agent(sdk_name, command, umsg)
        
        return status

    def register_listener_command(self, sdk_name: str, command: str, topic: UUri, listener: UListener):
        """
        sends data to TA params (action/command and UURi Umessage)

        Before registering listener​...
        Create entry in table for given SDK, 
        uURI and register a callback which 
        will be invoked when onReceive event received. For given SDK.​

        (sdk, uuri) --> UListener
        """
        sdk_name = sdk_name.lower().strip()
        if sdk_name == "python":
            # send thru Socket UTransport
            status: UStatus = self.utransport.register_listener(topic, listener)
            print("registered in uTransport python")
        else:
            print("register in uTransport else")

            # Send to Test Agent
            umsg: UMessage = UMessage(source=topic)
            print("HI")
            status: UStatus = self.send_msg_to_test_agent(sdk_name, command, umsg)

        return status