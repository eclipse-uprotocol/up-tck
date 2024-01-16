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
from uprotocol.proto.uattributes_pb2 import UAttributes
from uprotocol.proto.upayload_pb2 import UPayload
from uprotocol.proto.umessage_pb2 import UMessage
from uprotocol.proto.cloudevents_pb2 import CloudEvent
from uprotocol.proto.upayload_pb2 import UPayload, UPayloadFormat
from uprotocol.transport.builder.uattributesbuilder import UAttributesBuilder
from uprotocol.proto.uattributes_pb2 import UPriority

from ulink_socket_python.socket_utransport import SocketUTransport
from google.protobuf.any_pb2 import Any


PORT = 44444
IP = "127.0.0.1" 
ADDR = (IP, PORT)

uri: str = "/body.access//door.front_left#Door"


logging.basicConfig(format='%(asctime)s %(message)s')
# Create logger
logger = logging.getLogger('simple_example')
logger.setLevel(logging.INFO)


def build_cloud_event():
    return CloudEvent(spec_version="1.0", source="https://example.com", id="HARTLEY IS THE BEST")

def build_upayload():
    any_obj = Any()
    any_obj.Pack(build_cloud_event())
    return UPayload(format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF, value=any_obj.SerializeToString())

def build_uattributes():
    return UAttributesBuilder.publish(UPriority.UPRIORITY_CS4).build()


if __name__ == "__main__":
    client = SocketUTransport(IP, PORT)
    topic = LongUriSerializer().deserialize(uri)
    payload: UPayload = build_upayload()

    attributes: UAttributes = build_uattributes()
    umsg = UMessage(source=topic, attributes=attributes, payload=payload)  # protobuf message
    logger.info("orig umsg:")
    logger.info(f"{umsg}")


    client.send(topic, payload, attributes)