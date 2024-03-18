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
import threading
import time
from concurrent.futures import Future
from typing import Dict

from google.protobuf.any_pb2 import Any
from multipledispatch import dispatch
from uprotocol.proto.uattributes_pb2 import UAttributes, UMessageType
from uprotocol.proto.umessage_pb2 import UMessage
from uprotocol.proto.upayload_pb2 import UPayload
from uprotocol.proto.uri_pb2 import UUri
from uprotocol.proto.ustatus_pb2 import UCode
from uprotocol.proto.ustatus_pb2 import UStatus
from uprotocol.rpc.calloptions import CallOptions
from uprotocol.rpc.rpcmapper import RpcMapper
from uprotocol.transport.builder.uattributesbuilder import UAttributesBuilder
from uprotocol.transport.ulistener import UListener

from up_client_socket.python.socket_utransport import SocketUTransport
from test_agents import TransportLayer
from utils.constants import (SEND_COMMAND, REGISTER_LISTENER_COMMAND, UNREGISTER_LISTENER_COMMAND,
                             INVOKE_METHOD_COMMAND, \
                             COMMANDS, TRANSPORT_COMMANDS)
from utils.logger import logger
from utils.socket_message_processing_utils import send_socket_data, receive_socket_data, convert_bytes_to_string, \
    convert_json_to_jsonstring, convert_jsonstring_to_json, convert_str_to_bytes, protobuf_to_base64, \
    base64_to_protobuf_bytes, is_json_message, create_json_message

TEST_MANAGER_ADDR: tuple = ("127.0.0.5", 12345)


class SocketUListener(UListener):

    def on_receive(self, umsg: UMessage) -> None:
        logger.info("Listener onreceived")
        json_message = create_json_message("onReceive", protobuf_to_base64(umsg))
        json_message_str: str = convert_json_to_jsonstring(json_message)

        message: bytes = convert_str_to_bytes(json_message_str)

        logger.info("Sending onReceive msg to Test Manager Directly!")
        send_socket_data(self.test_manager_conn, message)

        # when invoke method is called  w/ a type Request UMessage, send a response to the TM
        if umsg.attributes.type == UMessageType.UMESSAGE_TYPE_REQUEST:
            topic: UUri = umsg.attributes.source
            payload: UPayload = umsg.payload
            attributes: UAttributes = umsg.attributes

            attributes = UAttributesBuilder(topic, attributes.id, UMessageType.UMESSAGE_TYPE_RESPONSE,
                                            attributes.priority).withReqId(attributes.id).build()

            transport = TransportLayer()
            msg = UMessage(attributes=attributes, payload=payload)
            transport.send(msg)


# Creating an instance of UListener
listener = SocketUListener()
transport = SocketUTransport()
ta_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ta_socket.connect(TEST_MANAGER_ADDR)


class SocketTestAgent:
    def __init__(self):
        self.possible_received_protobufs = [UMessage()]
        # Listening thread to receive messages from Test Manager
        thread = threading.Thread(target=self.receive_from_tm,)
        thread.start()

    def receive_from_tm(self):
        """
        Listening thread that receives UMessages from Test Manager
        @param listener: UListener that reacts to a UMessage for a specific topic Uuri
        """
        while True:
            recv_data: bytes = receive_socket_data(ta_socket)

            if recv_data == b"":
                logger.info("Closing TA Client Socket")
                ta_socket.close()
                return

            if is_json_message(recv_data):
                self._handle_json_message(recv_data)

    def _handle_json_message(self, recv_data: bytes):
        json_str = convert_bytes_to_string(recv_data)
        json_msg = convert_jsonstring_to_json(json_str)

        if json_msg["action"] in TRANSPORT_COMMANDS:
            self.handle_transport_command_json(json_msg)

    def handle_transport_command_json(self, json_msg: Dict[str, str]):
        action = json_msg["action"]
        umsg_base64 = json_msg["message"]
        protobuf_serialized_data = base64_to_protobuf_bytes(umsg_base64)

        received_proto: UMessage = RpcMapper.unpack_payload(Any(value=protobuf_serialized_data), UMessage)
        logger.info(f'action: {action}, received_proto: {received_proto}')

        source = received_proto.attributes.source
        payload = received_proto.payload
        status = None
        if action == SEND_COMMAND:
            status = transport.send(received_proto)
        elif action == REGISTER_LISTENER_COMMAND:
            status = transport.register_listener(source, listener)
        elif action == UNREGISTER_LISTENER_COMMAND:
            status = transport.unregister_listener(received_proto.attributes.source, listener)
        elif action == INVOKE_METHOD_COMMAND:
            future_umsg = transport.invoke_method(source, payload, CallOptions())
            # Need to have service that sends data back above
            # Currently the Test Agent is the Client_door, and can act as service
            status = UStatus(code=UCode.OK, message="OK")
        self.send(status)

        if action == INVOKE_METHOD_COMMAND:
            # Wait for response, and if havent gotten response in 10 sec then continue

            # When got response, sub/reg waits until Future is completed/filled
            logger.info("Waiting for future UMessage")
            start_time = time.time()
            wait_time_secs = 10.0
            while not future_umsg.done() and time.time() - start_time < wait_time_secs:
                continue

            if future_umsg.done():
                umsg: UMessage = future_umsg.result()
                self.utransport.register_listener(umsg.attributes.source, listener)
                logger.info("----invoke_method registered----")
            else:
                logger.warn("----invoke_method Failed to register----")

    @dispatch(UUri, UPayload, UAttributes)
    def send(self, topic: UUri, payload: UPayload, attributes: UAttributes):
        """
        Sends UMessage data to Test Manager
        @param topic: part of UMessage
        @param payload: part of UMessage
        @param attributes: part of UMessage
        """

        if topic is not None:
            attributes.source.CopyFrom(topic)

        umsg: UMessage = UMessage(attributes=attributes, payload=payload)

        json_message = create_json_message("send", protobuf_to_base64(umsg))

        self.send_to_TM(json_message)

    @dispatch(UStatus)
    def send(self, status: UStatus):
        """
        Sends UStatus to Test Manager
        @param status: the reply after receiving a message
        """
        json_message = create_json_message("uStatus", protobuf_to_base64(status))

        self.send_to_TM(json_message)

    def send_to_TM(self, json_message: Dict[str, str]):
        """
        Sends json data to Test Manager
        @param json_message: json message
        """
        json_message_str: str = convert_json_to_jsonstring(json_message)

        message: bytes = convert_str_to_bytes(json_message_str)

        send_socket_data(self.clientsocket, message)
        logger.info(f"Sent to TM {message}")

    def close_connection(self):
        self.clientsocket.close()


agent = SocketTestAgent()
agent.send_to_TM({'SDK_name': "python"})
