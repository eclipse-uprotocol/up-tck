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
from collections import defaultdict
from typing import Dict
import json
import base64
from multipledispatch import dispatch
from google.protobuf.any_pb2 import Any

from uprotocol.proto.uattributes_pb2 import UAttributes
from uprotocol.proto.uri_pb2 import UUri
from uprotocol.proto.umessage_pb2 import UMessage
from uprotocol.proto.ustatus_pb2 import UStatus, UCode
from uprotocol.proto.upayload_pb2 import UPayload

from uprotocol.transport.utransport import UTransport
from up_tck_python.up_client_socket_python.socket_utransport import SocketUTransport

from uprotocol.transport.ulistener import UListener

# on_receive_items = []
# evt = threading.Event()
    

def serialize_protobuf_to_base64(obj: Any):
    return base64.b64encode(obj.SerializeToString()).decode('ASCII')

class SocketTestAgent:
    def __init__(self, test_clientsocket: socket.socket, utransport: UTransport, listener: UListener) -> None:
        """
        The test server that the Test Agent will connect to
        Idea: acts as validator to validate data sent in up-client-socket-xxx

        """
        # Socket Connection to Dispatcher
        self.utransport: SocketUTransport = utransport

        self.possible_received_protobufs = [UMessage()]

        # Client Socket connection to Test Manager
        self.clientsocket: socket.socket = test_clientsocket

        # Listening thread to receive messages from Test Manager
        thread = threading.Thread(target=self.receive_from_tm, args=(listener,))
        thread.start()

    def receive_from_tm(self, listener):
        """
        Will always be receiving for clientsocket TA connected to current TM 
        """
        msg_len: int = 32767
        while True:
            recv_data: bytes = self.clientsocket.recv(msg_len)
            
            if recv_data == b"":
                continue

            json_str: str = recv_data.decode()

            json_msg: Dict[str, str] = json.loads(json_str)
            print("json_msg", json_msg)

            action: str = json_msg["action"]
            umsg_base64: str = json_msg["message"]
            protobuf_serialized_data: bytes = base64.b64decode(umsg_base64)
            
            # unpack protobuf
            response_proto: Any = None
            
            for proto in self.possible_received_protobufs:
                try:
                    proto.ParseFromString(protobuf_serialized_data)
                    response_proto = proto
                    print("here:", proto)
                except Exception as err:
                    pass
            print("response_proto:", response_proto)

            if action == "send":
                self.utransport.send(response_proto.source, response_proto.payload, response_proto.attributes)
            elif action == "registerlistener":
                self.utransport.register_listener(response_proto.source, listener)

            # NEED TO HANDLE the message
            if isinstance(response_proto, UMessage):
                print(response_proto)
                response = UStatus(code=UCode.OK, message="OK") 
                self.send(response)
            elif isinstance(response_proto, UStatus):
                print(f"Received UStatus Message: {response_proto}")
            else:
                raise Exception("ERROR: Received message type that's not UMessage nor UStatus.")  
            
    def __send_to_server(self, message: bytes):
        self.clientsocket.send(message)

    @dispatch(UUri, UPayload, UAttributes)
    def send(self, topic: UUri, payload: UPayload, attributes: UAttributes):
        """
        Sends data to Test Agent parameters (action/command and complete Umessage)
        """
        umsg: UMessage = UMessage(source=topic, attributes=attributes, payload=payload)

        #Creates the JSON message
        json_message = {
            "action": "send",
            "message": serialize_protobuf_to_base64(umsg)
        }

        # Converts a dictionary/map -> JSON string
        json_message_str: str = json.dumps(json_message)

         # Sends data over socket in bytes --> Converts JSON string to bytes
        message: bytes = str.encode(json_message_str)
        
        self.__send_to_server(message)

    @dispatch(UStatus)
    def send(self, status: UStatus):
        """
        Sends data to Test Agent parameters (action/command and complete Umessage)
        """

        print(f"UStatus: {status}")
        # create the Json message
        json_message = {
            "action": "uStatus",
            "message": serialize_protobuf_to_base64(status)
        }

        # Converts a dictionary/map -> JSON string
        json_message_str: str = json.dumps(json_message)

        print("sending", json_message)

        # Sends data over socket in bytes --> Converts JSON string to bytes
        message: bytes = str.encode(json_message_str)
        
        self.__send_to_server(message)

    def send_to_TM(self, json_message_str: str):
        message: bytes = str.encode(json_message_str)   # send this to socket in bytes
        
        self.__send_to_server(message)

    def send_to_client(self, client: socket.socket, json_message: Dict[str, str]):
        json_message_str: str = json.dumps(json_message)
        message: bytes = str.encode(json_message_str)   # send this to socket in bytes
        client.send(message)

    def __send_json_msg_to_TM(self, command: str, umsg: UMessage):
        # Sends to Test Agent
        json_message = {
            "action": command,
            "message": serialize_protobuf_to_base64(umsg)
        }

        self.send_to_client(self.clientsocket, json_message)

       
    def on_receive_command_TA_to_TM(self, command: str,  topic: UUri, payload: UPayload, attributes: UAttributes):
        # Sends to Test Manager
        umsg: UMessage = UMessage(source=topic, attributes=attributes, payload=payload)
        self.__send_json_msg_to_TM(command, umsg)