# -------------------------------------------------------------------------

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

# -------------------------------------------------------------------------

from concurrent.futures import Future, ThreadPoolExecutor
import socket

from uprotocol.proto.uattributes_pb2 import UAttributes
from uprotocol.proto.uri_pb2 import UUri
from uprotocol.proto.upayload_pb2 import UPayload
from uprotocol.rpc.rpcclient import RpcClient
from uprotocol.proto.umessage_pb2 import UMessage
from uprotocol.proto.upayload_pb2 import UPayload
from uprotocol.proto.uuid_pb2 import UUID

import logging
logging.basicConfig(format='%(asctime)s %(message)s')
# Create logger
logger = logging.getLogger('simple_example')
logger.setLevel(logging.INFO)

class SocketRPCClient(RpcClient):
    """
    RpcClient is an interface used by code generators for uProtocol services defined in proto files such as the core
    uProtocol services found in <a href=https://github.com/eclipse-uprotocol/uprotocol-core-api>here</a>.<br> The
    interface provides a
    clean contract for all transports to implement to be able to support RPC on their platform.<br> Each platform MUST
    implement this interface.<br> For more details please refer to<br>
    <a href=https://github.com/eclipse-uprotocol/uprotocol-spec/blob/main/up-l2/README.adoc>[RpcClient
    Specifications]</a>
    """

    def __init__(self, host_ip: str, port: int) -> None:
        '''
        @param host_ip: the ip address for the socket to connect to
        @param port: the port for the socket to connect to
        '''

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        self.socket.connect((host_ip, port))  
    
    def __send_to_service_socket(self, topic: UUri, payload: UPayload, attributes: UAttributes):
        """
        Sends the using the provided UMessage data then waits until it gets a response message.
        @param topic: sending UUri protobuf.
        @param payload: sending UPayload protobuf.
        @param attributes: sending UAttributes protobuf.
        @return: a response message from the receiving client/service.
        """

        # Get UAttributes's request id
        request_id: UUID = attributes.id
        request_id_b: bytes = request_id.SerializeToString()

        # Protobuf message
        umsg = UMessage(source=topic, attributes=attributes, payload=payload) 

        # Now serialized, then send
        umsg_serialized: bytes = umsg.SerializeToString()

        self.socket.send(umsg_serialized)

        while True:
            # Wait and receive data from server
            msg_len: int = 32767
            recv_data: bytes = self.socket.recv(msg_len) 

            if recv_data == b'':
                continue

            response_umsg: UMessage = UMessage()

            try:
                # Unpack received data into UMessage
                response_umsg.ParseFromString(recv_data)
            except AttributeError as ae:
                logger.info("Data isn't type UMessage: \n" + str(ae))
                continue
            except Exception as err:
                raise Exception(err)   
            
            response_reqid: UUID = response_umsg.attributes.reqid

            if request_id_b == response_reqid.SerializeToString():
                # Got response
                logger.info('Got response: \n' + str(response_umsg))
                return response_umsg
            else:
                # If response wasn't meant for current client
                logger.info("Response wasn't meant for current client: \n" + str(response_umsg))
                continue
            

    def invoke_method(self, topic: UUri, payload: UPayload, attributes: UAttributes) -> Future:
        """
        Support for RPC method invocation.<br><br>

        @param topic: topic of the method to be invoked (i.e. the name of the API we are calling).
        @param payload:The request message to be sent to the server.
        @param attributes: metadata for the method invocation (i.e. priority, timeout, etc.)
        @return: Returns the CompletableFuture with the result or exception.
        """
        with ThreadPoolExecutor(max_workers=1) as executor:
            # Mark each future with its groups
            response: Future = executor.submit(self.__send_to_service_socket, topic, payload, attributes)

            return response
