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
from uprotocol.uri.serializer.longuriserializer import LongUriSerializer
from uprotocol.proto.uattributes_pb2 import UAttributes
from uprotocol.proto.upayload_pb2 import UPayload
from uprotocol.proto.uri_pb2 import UEntity, UUri
from uprotocol.proto.ustatus_pb2 import UStatus
from uprotocol.transport.ulistener import UListener
from uprotocol.transport.utransport import UTransport
from uprotocol.proto.umessage_pb2 import UMessage
from uprotocol.proto.cloudevents_pb2 import CloudEvent
from uprotocol.proto.upayload_pb2 import UPayload, UPayloadFormat
from uprotocol.transport.builder.uattributesbuilder import UAttributesBuilder
from uprotocol.proto.uattributes_pb2 import UPriority

import socket
from threading import Thread
import logging

from uprotocol.transport.socket.listener import Listener
from constants import HEADER, PORT, SERVER, ADDR, FORMAT, DISCONNECT_MESSAGE 
from uprotocol.transport.socket.socket_utransport import SocketUTransport
from google.protobuf.any_pb2 import Any

logging.basicConfig(format='%(asctime)s %(message)s')
# create logger
logger = logging.getLogger('simple_example')
logger.setLevel(logging.INFO)


client = SocketUTransport(SERVER, PORT, HEADER)
uri: str = "/body.access//door.front_left#Door"
topic = LongUriSerializer().deserialize(uri)

# to_str = binary.decode()
# print(type(to_str))
# to_byte = to_str.encode()
# print(to_byte)

listener: UListener = Listener()
client.register_listener(topic, listener)

logger.info("registered to topic:")
logger.info(f"{topic}")
