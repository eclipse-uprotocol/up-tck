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

from concurrent.futures import Future

from uprotocol.proto.uattributes_pb2 import UAttributes
from uprotocol.proto.upayload_pb2 import UPayload
from uprotocol.proto.uri_pb2 import UEntity
from uprotocol.proto.uri_pb2 import UUri
from uprotocol.proto.ustatus_pb2 import UStatus
from uprotocol.transport.ulistener import UListener

from up_tck_python.up_client_socket_python.socket_utransport import SocketUTransport



class TransportLayer:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            # Initialize the singleton instance
            self._initialized = True
            self.__instance = None
            self.__ZENOH_IP = '10.0.3.3'
            self.__ZENOH_PORT = 9090
            self.__utransport = "ZENOH"

            self.__SOCKET_IP: str = "127.0.0.1"
            self.__SOCKET_PORT: int = 44444
            self.__utransport = "SOCKET"
            self._update_instance()

    def set_transport(self, transport: str):
        if self.__utransport != transport:
            print('set transport, previous is', self.__utransport, 'current is', transport)
            self.__utransport = transport
            self._update_instance()

    def get_transport(self):
        return self.__utransport

    def set_zenoh_config(self, ip, port):
        if self.__ZENOH_PORT != port or self.__ZENOH_IP != ip:
            self.__ZENOH_PORT = port
            self.__ZENOH_IP = ip
            self._update_instance()

    def set_socket_config(self, ip: str, port: int):
        if self.__SOCKET_PORT != port or self.__SOCKET_IP != ip:
            self.__SOCKET_PORT = port
            self.__SOCKET_IP = ip
            self._update_instance()

    def _update_instance(self):
        '''
        if self.__utransport == "ZENOH" and self.__ZENOH_IP is not None and self.__ZENOH_PORT is not None:
            self.__instance = Zenoh(self.__ZENOH_IP, self.__ZENOH_PORT)
        elif self.__utransport == "BINDER":
            self.__instance = AndroidBinder()
        '''
        if self.__utransport == "SOCKET":
            self.__instance = SocketUTransport(self.__SOCKET_IP, self.__SOCKET_PORT)

    def invoke_method(self, topic: UUri, payload: UPayload, attributes: UAttributes) -> Future:
        return self.__instance.invoke_method(topic, payload, attributes)

    def authenticate(self, u_entity: UEntity) -> UStatus:
        return self.__instance.authenticate(u_entity)

    def send(self, topic: UUri, payload: UPayload, attributes: UAttributes) -> UStatus:
        return self.__instance.send(topic, payload, attributes)

    def register_listener(self, topic: UUri, listener: UListener) -> UStatus:
        return self.__instance.register_listener(topic, listener)

    def unregister_listener(self, topic: UUri, listener: UListener) -> UStatus:
        return self.__instance.unregister_listener(topic, listener)

    def start_service(self, entity) -> bool:
        if self.__utransport == "BINDER":
            return self.__instance.start_service(entity)
