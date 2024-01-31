# -------------------------------------------------------------------------

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

# -------------------------------------------------------------------------

from typing import Dict
import json
import socket
from google.protobuf.any_pb2 import Any

from uprotocol.proto.uattributes_pb2 import UAttributes
from uprotocol.proto.uri_pb2 import UUri
from uprotocol.proto.ustatus_pb2 import UStatus, UCode
from uprotocol.proto.upayload_pb2 import UPayload

from up_tck_python.up_client_socket_python.transport_layer import TransportLayer
from up_tck_python.test_agent.testagent import SocketTestAgent

from uprotocol.transport.ulistener import UListener

from uprotocol.proto.cloudevents_pb2 import CloudEvent
from uprotocol.proto.umessage_pb2 import UMessage
from uprotocol.proto.upayload_pb2 import UPayload, UPayloadFormat
from uprotocol.proto.uattributes_pb2 import UPriority
from uprotocol.transport.builder.uattributesbuilder import UAttributesBuilder
from uprotocol.uri.serializer.longuriserializer import LongUriSerializer

from up_tck_python.utils.socket_message_processing_utils import convert_json_to_jsonstring, convert_str_to_bytes, protobuf_to_base64, send_socket_data

class SocketUListener(UListener):
    def __init__(self, test_agent_conn: socket.socket) -> None:
        """
        @param test_agent_conn: Connection to Test Agent
        """
        # Connection to Test Manager
        self.test_agent_conn: socket.socket = test_agent_conn

    def on_receive(self, topic: UUri, payload: UPayload, attributes: UAttributes) -> UStatus:
        """
        Method called to handle/process events.<br><br>
        Sends UMessage data directly to Test Manager
        @param topic: Topic the underlying source of the message.
        @param payload: Payload of the message.
        @param attributes: Transportation attributes.
        @return Returns an Ack every time a message is received and processed.
        """
        # global on_receive_items
        print("Listener onreceived")
        print(f"{payload}")

        #NOTE: Need to send as JSON!!!
        umsg: UMessage = UMessage(source=topic, attributes=attributes, payload=payload)
        
        json_message = {
            "action": "onReceive",
            "message": protobuf_to_base64(umsg) 
        }

        print("SENDING onReceive...")
        json_message_str: str = convert_json_to_jsonstring(json_message) 

        message: bytes = convert_str_to_bytes(json_message_str) 

        print("Sending to Test Manager Directly!")
        send_socket_data(test_agent_socket, message) 

        return UStatus(code=UCode.OK, message="all good") 
    

uri: str = "/body.access//door.front_left#Door"

def build_cloud_event():
    return CloudEvent(spec_version="1.0", source="https://example.com", id="HARTLEY IS THE BEST")

def build_upayload():
    any_obj = Any()
    any_obj.Pack(build_cloud_event())
    return UPayload(format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF, value=any_obj.SerializeToString())

def build_uattributes():
    return UAttributesBuilder.publish(UPriority.UPRIORITY_CS4).build()


if __name__ == "__main__":
    dispatcher_IP: str = "127.0.0.1"
    dispatcher_PORT: int = 44444

    transport = TransportLayer()
    transport.set_socket_config(dispatcher_IP, dispatcher_PORT)
    
    test_manager_IP: str = "127.0.0.5"
    test_manager_PORT: int = 12345
    test_agent_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    test_agent_socket.connect((test_manager_IP, test_manager_PORT))  

    listener: UListener = SocketUListener(test_agent_socket)

    agent = SocketTestAgent(test_agent_socket, transport, listener)


    topic = LongUriSerializer().deserialize(uri)
    payload: UPayload = build_upayload()
    attributes: UAttributes = build_uattributes()


    agent.send_to_TM({'SDK_name': "java"})