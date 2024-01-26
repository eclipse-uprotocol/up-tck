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


import logging

from uprotocol.uri.serializer.longuriserializer import LongUriSerializer
from uprotocol.transport.ulistener import UListener
from ulink_socket_python.socket_utransport import SocketUTransport

from test_ulistener import SocketUListener
from test_ulistener_reply import SocketUListenerReply

PORT = 44444
IP = "127.0.0.1" 
ADDR = (IP, PORT)

uURI: str = "/body.access//door.front_left#Door"


logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger('simple_example')
logger.setLevel(logging.INFO)


if __name__ == "__main__":
    client = SocketUTransport(IP, PORT)
    topic = LongUriSerializer().deserialize(uURI)

    listener: UListener = SocketUListener()
    listener_reply: UListener = SocketUListenerReply(client)

    # client.register_listener(topic, listener)
    client.register_listener(topic, listener_reply)

    logger.info(f"Registered to topic: {topic}")
