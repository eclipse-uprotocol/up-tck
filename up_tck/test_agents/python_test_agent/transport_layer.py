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

import sys
from concurrent.futures import Future

from uprotocol.proto.uattributes_pb2 import UAttributes
from uprotocol.proto.upayload_pb2 import UPayload
from uprotocol.proto.uri_pb2 import UEntity
from uprotocol.proto.uri_pb2 import UUri
from uprotocol.proto.ustatus_pb2 import UStatus
from uprotocol.proto.umessage_pb2 import UMessage
from uprotocol.transport.ulistener import UListener
from uprotocol.rpc.calloptions import CallOptions


from up_tck.up_client_socket_python.socket_utransport import SocketUTransport

from up_tck.python_utils.logger import logger


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

            self.__utransport = "SOCKET"
            self._update_instance()

    def set_transport(self, transport: str):
        if self.__utransport != transport:
            logger.info(f'set transport, previous is {self.__utransport} current is {transport}')
            self.__utransport = transport
            self._update_instance()

    def get_transport(self):
        return self.__utransport

    def _update_instance(self):
        '''
        if self.__utransport == "ZENOH" and self.__ZENOH_IP is not None and self.__ZENOH_PORT is not None:
            self.__instance = Zenoh(self.__ZENOH_IP, self.__ZENOH_PORT)
        elif self.__utransport == "BINDER":
            self.__instance = AndroidBinder()
        '''
        if self.__utransport == "SOCKET":
            self.__instance = SocketUTransport()

    def send(self, umsg: UMessage) -> UStatus:
        return self.__instance.send(umsg)

    def register_listener(self, topic: UUri, listener: UListener) -> UStatus:
        return self.__instance.register_listener(topic, listener)

    def unregister_listener(self, topic: UUri, listener: UListener) -> UStatus:
        return self.__instance.unregister_listener(topic, listener)
    
    def invoke_method(self, topic: UUri, payload: UPayload, options: CallOptions) -> Future:
        return self.__instance.invoke_method(topic, payload, options)
