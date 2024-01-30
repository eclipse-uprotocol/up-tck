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


from typing import Dict
import socket
import logging
from google.protobuf.any_pb2 import Any
from concurrent.futures import Future

from threading import Thread
from uprotocol.proto.uattributes_pb2 import UAttributes
from uprotocol.proto.upayload_pb2 import UPayload
from uprotocol.proto.uri_pb2 import UEntity, UUri
from uprotocol.proto.ustatus_pb2 import UStatus, UCode
from uprotocol.transport.ulistener import UListener
from uprotocol.transport.utransport import UTransport
from uprotocol.proto.umessage_pb2 import UMessage
from uprotocol.rpc.rpcmapper import RpcMapper
from uprotocol.rpc.rpcclient import RpcClient

from up_tck_python.up_client_socket_python.socket_rpcclient import SocketRPCClient

logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger('simple_example')
logger.setLevel(logging.INFO)


class SocketUTransport(UTransport):
    def __init__(self, host_ip: str, port: int) -> None:
        """
        Creates a uEntity with Socket Connection, as well as a map of registered topics.
        @param host_ip: IP address of Dispatcher.
        @param port: Port of Dispatcher.
        """
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        self.socket.connect((host_ip, port))  

        self.rpcclient: RpcClient = SocketRPCClient(None, None, socket=socket)

        self.topic_to_listener: Dict[bytes, UListener] = {} 
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
                msg_len: int = 32767
                recv_data: bytes = self.socket.recv(msg_len) 

                if recv_data == b"":
                    continue
                
                logger.info(f"Received Data: {recv_data}")

                logger.info(f"!!!USING RpcMapper unpack_payload!!!")

                umsg: UMessage = RpcMapper.unpack_payload(Any(value=recv_data), UMessage ) # unpack(recv_data , UMessage())
                logger.info(f"Received uMessage: {umsg}")

                uuri: UUri = umsg.source
                payload: UPayload = umsg.payload
                attributes: UAttributes = umsg.attributes

                topic: bytes = uuri.SerializeToString()
                if topic in self.topic_to_listener:
                    logger.info("Handle Topic")

                    listener: UListener = self.topic_to_listener[topic]
                    listener.on_receive(uuri, payload, attributes)
                else:
                    logger.info("Topic not found in Listener Map, discarding...")

            except socket.error:
                self.socket.close()
                break
        


    def send(self, topic: UUri, payload: UPayload, attributes: UAttributes) -> UStatus:
        """
        Transmits UPayload to the topic using the attributes defined in UTransportAttributes.<br><br>
        @param topic:Resolved UUri topic to send the payload to.
        @param payload:Actual payload.
        @param attributes:Additional transport attributes.
        @return:Returns OKSTATUS if the payload has been successfully sent (ACK'ed), otherwise it returns FAILSTATUS
        with the appropriate failure.
        """
        
        umsg = UMessage(source=topic, attributes=attributes, payload=payload) 
        umsg_serialized: bytes = umsg.SerializeToString()

        try:
            num_bytes_sent: int = self.socket.send(umsg_serialized)
            if num_bytes_sent == 0:
                return UStatus(code=UCode.INTERNAL, message="INTERNAL ERROR: Socket Connection Broken")
            logger.info("uMessage Sent")
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
        self.topic_to_listener[topic_serialized] = listener

        return UStatus(code=UCode.OK, message="OK") 
    
    def authenticate(self, u_entity: UEntity) -> UStatus:
        pass

    def unregister_listener(self, topic: UUri, listener: UListener) -> UStatus:
        
        del self.topic_to_listener[topic.SerializeToString()]

        return UStatus(code=UCode.OK, message="OK")  
    

    def invoke_method(self, topic: UUri, payload: UPayload, attributes: UAttributes) -> Future:
        """
        Support for RPC method invocation.<br><br>

        @param topic: topic of the method to be invoked (i.e. the name of the API we are calling).
        @param payload:The request message to be sent to the server.
        @param attributes: metadata for the method invocation (i.e. priority, timeout, etc.)
        @return: Returns the CompletableFuture with the result or exception.
        """
        return self.rpcclient.invoke_method(topic, payload, attributes)
    

