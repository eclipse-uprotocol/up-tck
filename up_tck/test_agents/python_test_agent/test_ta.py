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
import sys

from uprotocol.proto.umessage_pb2 import UMessage
from uprotocol.proto.ustatus_pb2 import UStatus, UCode
from uprotocol.proto.upayload_pb2 import UPayload
from uprotocol.proto.uattributes_pb2 import UAttributes, UMessageType
from uprotocol.proto.uri_pb2 import UUri
from uprotocol.transport.ulistener import UListener
from uprotocol.transport.builder.uattributesbuilder import  UAttributesBuilder


from up_tck.test_agents.python_test_agent.transport_layer import TransportLayer
from up_tck.test_agents.python_test_agent.testagent import SocketTestAgent
from up_tck.python_utils.socket_message_processing_utils import convert_json_to_jsonstring, \
    convert_str_to_bytes, protobuf_to_base64, send_socket_data, create_json_message
from up_tck.python_utils.constants import TEST_MANAGER_ADDR
from up_tck.python_utils.logger import logger


class SocketUListener(UListener):
    def __init__(self, test_manager_conn: socket.socket) -> None:
        """
        @param test_agent_conn: Connection to Test Agent
        """
        # Connection to Test Manager
        self.test_manager_conn: socket.socket = test_manager_conn

    def on_receive(self, umsg: UMessage) -> None:
        """
        Method called to handle/process events.<br><br>
        Sends UMessage data directly to Test Manager
        @param topic: Topic the underlying source of the message.
        @param payload: Payload of the message.
        @param attributes: Transportation attributes.
        @return Returns an Ack every time a message is received and processed.
        """
        #  send JSON OnReceive to Test Manager
        logger.info("Listener onreceived")

        json_message = create_json_message("onReceive", protobuf_to_base64(umsg))

        json_message_str: str = convert_json_to_jsonstring(json_message)

        message: bytes = convert_str_to_bytes(json_message_str)

        logger.info("Sending onReceive msg to Test Manager Directly!")
        send_socket_data(self.test_manager_conn, message)
        
        # when invoke method is called  w/ a type Request UMessage, we handle and respond w a UMsg directly in SocketUTransport
        if umsg.attributes.type == UMessageType.UMESSAGE_TYPE_REQUEST:
            topic: UUri = umsg.attributes.source 
            payload: UPayload = umsg.payload
            attributes: UAttributes = umsg.attributes
            
            attributes = UAttributesBuilder(topic, attributes.id, UMessageType.UMESSAGE_TYPE_RESPONSE, attributes.priority).withReqId(attributes.id).build()
            
            transport = TransportLayer()
            msg = UMessage(attributes=attributes, payload=payload)
            transport.send(msg)


if __name__ == "__main__":

    transport = TransportLayer()

    test_agent_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    test_agent_socket.connect(TEST_MANAGER_ADDR)

    listener: UListener = SocketUListener(test_agent_socket)

    agent = SocketTestAgent(test_agent_socket, transport, listener)

    agent.send_to_TM({'SDK_name': "python"})
