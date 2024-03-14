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
import time

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
from uprotocol.rpc.calloptions import CallOptions

from up_tck.test_agents.python_test_agent.transport_layer import TransportLayer
from up_tck.python_utils.socket_message_processing_utils import (send_socket_data,
                                                                                  receive_socket_data, \
    convert_bytes_to_string, convert_json_to_jsonstring, convert_jsonstring_to_json, convert_str_to_bytes, \
    protobuf_to_base64, base64_to_protobuf_bytes, is_json_message, create_json_message)
from up_tck.python_utils.constants import SEND_COMMAND, REGISTER_LISTENER_COMMAND, \
    UNREGISTER_LISTENER_COMMAND, INVOKE_METHOD_COMMAND, COMMANDS, SERIALIZERS
from up_tck.python_utils.logger import logger


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
        # self.json_msg_serializer_selector: JsonMessageSerializerSelector = JsonMessageSerializerSelector()

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

            if is_json_message(recv_data): 
                self._handle_json_message(recv_data, listener)
                
            
    def _handle_json_message(self, recv_data: bytes, listener: UListener):
        json_str: str = convert_bytes_to_string(recv_data) 
        json_msg: Dict[str, str] = convert_jsonstring_to_json(json_str) 

        if json_msg["action"] in COMMANDS:
            self._handle_command_json(json_msg, listener)
    
        
    def _handle_command_json(self, json_msg: Dict[str, str], listener: UListener):
        action: str = json_msg["action"]
        umsg_base64: str = json_msg["message"]
        protobuf_serialized_data: bytes = base64_to_protobuf_bytes(umsg_base64)  
        
        received_proto: UMessage = RpcMapper.unpack_payload(Any(value=protobuf_serialized_data), UMessage)
        logger.info('action: ' + action)
        logger.info("received_proto: ")
        logger.info(received_proto)
        
        source: UUri = received_proto.attributes.source
        payload: UPayload = received_proto.payload
        status: UStatus = None
        if action == SEND_COMMAND:
            status = self.utransport.send(received_proto)
        elif action == REGISTER_LISTENER_COMMAND:
            status = self.utransport.register_listener(source, listener)
        elif action == UNREGISTER_LISTENER_COMMAND:
            status = self.utransport.unregister_listener(received_proto.attributes.source, listener)
        elif action == INVOKE_METHOD_COMMAND:
            future_umsg: Future = self.utransport.invoke_method(source, payload, CallOptions())
            
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

        json_message = create_json_message("send", protobuf_to_base64(umsg) )

        self.send_to_TM(json_message)

    @dispatch(UStatus)
    def send(self, status: UStatus):
        """
        Sends UStatus to Test Manager 
        @param status: the reply after receiving a message
        """
        json_message = create_json_message("uStatus", protobuf_to_base64(status) )

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
