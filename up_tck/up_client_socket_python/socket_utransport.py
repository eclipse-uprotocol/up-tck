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


from typing import Dict, List
import socket
from threading import Thread
import sys

from google.protobuf.any_pb2 import Any
from concurrent.futures import Future

from uprotocol.proto.uattributes_pb2 import UAttributes, UPriority, UMessageType
from uprotocol.proto.upayload_pb2 import UPayload
from uprotocol.proto.uri_pb2 import UEntity, UUri
from uprotocol.proto.uuid_pb2 import UUID
from uprotocol.proto.ustatus_pb2 import UStatus, UCode
from uprotocol.transport.ulistener import UListener
from uprotocol.transport.utransport import UTransport
from uprotocol.proto.umessage_pb2 import UMessage
from uprotocol.rpc.rpcmapper import RpcMapper
from uprotocol.rpc.rpcclient import RpcClient
from uprotocol.rpc.calloptions import CallOptions
from uprotocol.transport.builder.uattributesbuilder import UAttributesBuilder
from uprotocol.uri.factory.uresource_builder import UResourceBuilder


from up_tck.python_utils.constants import DISPATCHER_ADDR, BYTES_MSG_LENGTH
from up_tck.python_utils.logger import logger


class SocketUTransport(UTransport, RpcClient):
    def __init__(self) -> None:
        """
        Creates a uEntity with Socket Connection, as well as a map of registered topics.
        @param dipatcher_ip: IP address of Dispatcher.
        @param dipatcher_port: Port of Dispatcher.
        """
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        self.socket.connect(DISPATCHER_ADDR)  

        self.reqid_to_future: Dict[bytes, Future] = {}

        self.topic_to_listener: Dict[bytes, List[UListener]] = {} 
        thread = Thread(target = self.__listen)  
        thread.start()

    def __listen(self):
        """
        Listens to responses after sending UMessage Data to the Dispatcher.
        Will handle incoming data if the Socket_UTransporter registers to a UUri topic.
        @return: None.
        """

        while True:
            try: 
                recv_data: bytes = self.socket.recv(BYTES_MSG_LENGTH) 

                if recv_data == b"":
                    continue
                
                umsg: UMessage = RpcMapper.unpack_payload(Any(value=recv_data), UMessage ) # unpack(recv_data , UMessage())
                logger.info(f"{self.__class__.__name__} Received uMessage")
                
                attributes: UAttributes = umsg.attributes
                
                if attributes.type == UMessageType.UMESSAGE_TYPE_PUBLISH:
                    self._handle_publish_message(umsg)
                
                elif attributes.type == UMessageType.UMESSAGE_TYPE_REQUEST:
                    self._handle_request_message(umsg)

                elif attributes.type == UMessageType.UMESSAGE_TYPE_RESPONSE:
                    self._handle_response_message(umsg)

            except socket.error:
                self.socket.close()
                break
    
    def _handle_response_message(self, umsg: UMessage):
        request_id: UUID = umsg.attributes.reqid
        request_id_b: bytes = request_id.SerializeToString()
        
        if request_id_b in self.reqid_to_future:
            respose_future: Future = self.reqid_to_future[request_id_b]
            respose_future.set_result(umsg)

            del self.reqid_to_future[request_id_b]
                    
    def _handle_publish_message(self, umsg: UMessage):
        # Publish messages' attribute.source is the recevied publish topic
        topic_b: bytes = umsg.attributes.source.SerializeToString()
        if topic_b in self.topic_to_listener:
            logger.info(f"{self.__class__.__name__} Handle Topic")

            for listener in self.topic_to_listener[topic_b]:
                listener.on_receive(umsg)
        else:
            logger.info(f"{self.__class__.__name__} Topic not found in Listener Map, discarding...")

    def _handle_request_message(self, umsg: UMessage):
        # Request messages' attribute.sink is for subscribed/registered Destination UUri
        topic_b: bytes = umsg.attributes.sink.SerializeToString()
        if topic_b in self.topic_to_listener:
            logger.info(f"{self.__class__.__name__} Handle Topic")

            for listener in self.topic_to_listener[topic_b]:
                listener.on_receive(umsg)
        else:
            logger.info(f"{self.__class__.__name__} Topic not found in Listener Map, discarding...")
            
    def send(self, umsg: UMessage) -> UStatus:
        """
        Transmits UPayload to the topic using the attributes defined in UTransportAttributes.<br><br>
        @param topic:Resolved UUri topic to send the payload to.
        @param payload:Actual payload.
        @param attributes:Additional transport attributes.
        @return:Returns OKSTATUS if the payload has been successfully sent (ACK'ed), otherwise it returns FAILSTATUS
        with the appropriate failure.
        """

        umsg_serialized: bytes = umsg.SerializeToString()

        try:
            num_bytes_sent: int = self.socket.sendall(umsg_serialized)
            if num_bytes_sent == 0:
                return UStatus(code=UCode.INTERNAL, message="INTERNAL ERROR: Socket Connection Broken")
            logger.info(f"{self.__class__.__name__} uMessage Sent")
        except OSError:
            return UStatus(code=UCode.INTERNAL, message="INTERNAL ERROR: OSError sending UMessage")

        return UStatus(code=UCode.OK, message="OK")           

    def register_listener(self, topic: UUri, listener: UListener) -> UStatus:
        """
        Register listener to be called when UPayload is received for the specific topic.<br><br>
        @param topic:Resolved UUri for where the message arrived via the underlying transport technology.
        @param listener:The method to execute to process the date for the topic.
        @return:Returns OKSTATUS if the listener is unregistered correctly, otherwise it returns FAILSTATUS with the
        appropriate failure.
        """

        topic_serialized: bytes = topic.SerializeToString()
        if topic_serialized in self.topic_to_listener:
            self.topic_to_listener[topic_serialized].append(listener)
        else:
            self.topic_to_listener[topic_serialized] = [listener]

        return UStatus(code=UCode.OK, message="OK") 
    
    def authenticate(self, u_entity: UEntity) -> UStatus:
        pass

    def unregister_listener(self, topic: UUri, listener: UListener) -> UStatus:
        
        topic_serialized: bytes = topic.SerializeToString()

        if topic_serialized in self.topic_to_listener:
            if len(self.topic_to_listener[topic_serialized]) > 1:
                self.topic_to_listener[topic_serialized].remove(listener)
            else:
                del self.topic_to_listener[topic_serialized]
        else:
            return UStatus(code=UCode.NOT_FOUND, message="UUri topic was not registered initially")

        return UStatus(code=UCode.OK, message="OK")
    
    def invoke_method(self, methodUri: UUri, request_payload: UPayload, options: CallOptions) -> Future:
        source = UUri(entity=UEntity(name="name1", version_major=1), resource=UResourceBuilder.for_rpc_response())
        
        # Have to create own uAttribute UUID to 
        attributes = UAttributesBuilder.request(source, methodUri, UPriority.UPRIORITY_CS4, options.get_timeout()).build()

        # Get UAttributes's request id
        request_id: UUID = attributes.id
        response = Future()
        self.reqid_to_future[request_id.SerializeToString()] = response
        
        umsg = UMessage(payload=request_payload, attributes=attributes)
        self.send(umsg)
        return response
    