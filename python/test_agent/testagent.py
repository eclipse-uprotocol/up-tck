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
import threading
from concurrent.futures import Future
from typing import Dict

from google.protobuf.any_pb2 import Any
from multipledispatch import dispatch
from uprotocol.proto.uattributes_pb2 import UAttributes
from uprotocol.proto.umessage_pb2 import UMessage
from uprotocol.proto.upayload_pb2 import UPayload
from uprotocol.proto.uri_pb2 import UUri
from uprotocol.proto.ustatus_pb2 import UCode
from uprotocol.proto.ustatus_pb2 import UStatus
from uprotocol.rpc.rpcmapper import RpcMapper
from uprotocol.transport.ulistener import UListener

sys.path.append("../")

from python.test_agent.transport_layer import TransportLayer
from python.utils.socket_message_processing_utils import (send_socket_data,
                                                                                  receive_socket_data, \
    convert_bytes_to_string, convert_json_to_jsonstring, convert_jsonstring_to_json, convert_str_to_bytes, \
    protobuf_to_base64, base64_to_protobuf_bytes)
from python.utils.constants import SEND_COMMAND, REGISTER_LISTENER_COMMAND, \
    UNREGISTER_LISTENER_COMMAND, INVOKE_METHOD_COMMAND
from python.logger.logger import logger


class SocketTestAgent:
    def __init__(self, test_clientsocket: socket.socket, utransport: TransportLayer, listener: UListener) -> None:
        """
        The test server that the Test Agent will connect to
        Idea: acts as validator to validate data sent in up-client-socket-xxx
        @param test_clientsocket: socket connection to Test Manager
        @param utransport: actual implementation transportation medium (ex: Zenoh, UTransport, or Binder etc)
        @param listener: handler for a topic received 
        """
        # Socket Connection to Dispatcher
        self.utransport: TransportLayer = utransport

        self.possible_received_protobufs = [UMessage()]

        # Client Socket connection to Test Manager
        self.clientsocket: socket.socket = test_clientsocket

        # Listening thread to receive messages from Test Manager
        thread = threading.Thread(target=self.receive_from_tm, args=(listener,))
        thread.start()

    def receive_from_tm(self, listener: UListener):
        """
        Listening thread that receives UMessages from Test Manager 
        @param listener: UListener that reacts to a UMessage for a specific topic Uuri
        """
        while True:
            recv_data: bytes = receive_socket_data(self.clientsocket)

            if recv_data == b"":
                logger.info("Closing TA Client Socket")
                self.clientsocket.close()
                return

            json_str: str = convert_bytes_to_string(recv_data)
            json_msg: Dict[str, str] = convert_jsonstring_to_json(json_str)

            action: str = json_msg["action"]
            umsg_base64: str = json_msg["message"]
            protobuf_serialized_data: bytes = base64_to_protobuf_bytes(umsg_base64)

            umsg: UMessage = RpcMapper.unpack_payload(Any(value=protobuf_serialized_data), UMessage)

            status: UStatus = None
            if action == SEND_COMMAND:
                status = self.utransport.send(umsg)
            elif action == REGISTER_LISTENER_COMMAND:
                status = self.utransport.register_listener(umsg.attributes.source, listener)
            elif action == UNREGISTER_LISTENER_COMMAND:
                status = self.utransport.unregister_listener(umsg.attributes.source, listener)

                status = UStatus(code=UCode.OK, message="OK")
            self.send(status)

    @dispatch(UMessage)
    def send(self, umsg: UMessage):
        """
        Sends UMessage data to Test Manager
        @param umsg: UMessage to return to Test Manager
        """

        json_message = {"action": "send", "message": protobuf_to_base64(umsg)}

        self.send_to_tm(json_message)

    @dispatch(UStatus)
    def send(self, status: UStatus):
        """
        Sends UStatus to Test Manager 
        @param status: the reply after receiving a message
        """

        json_message = {"action": "uStatus", "message": protobuf_to_base64(status)}

        self.send_to_tm(json_message)

    def send_to_tm(self, json_message: Dict[str, str]):
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
