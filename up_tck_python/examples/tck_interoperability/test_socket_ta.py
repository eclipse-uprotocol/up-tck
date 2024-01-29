# -------------------------------------------------------------------------

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

# -------------------------------------------------------------------------

from typing import Dict
import json
from google.protobuf.any_pb2 import Any

from uprotocol.proto.uattributes_pb2 import UAttributes
from uprotocol.proto.uri_pb2 import UUri
from uprotocol.proto.ustatus_pb2 import UStatus, UCode
from uprotocol.proto.upayload_pb2 import UPayload

from up_tck_python.up_client_socket_python.socket_utransport import SocketUTransport
from up_tck_python.up_test_agent_socket_python.socket_test_agent import SocketTestAgent

from uprotocol.transport.ulistener import UListener

from uprotocol.proto.cloudevents_pb2 import CloudEvent
from uprotocol.proto.upayload_pb2 import UPayload, UPayloadFormat
from uprotocol.proto.uattributes_pb2 import UPriority
from uprotocol.transport.builder.uattributesbuilder import UAttributesBuilder
from uprotocol.uri.serializer.longuriserializer import LongUriSerializer

class SocketUListener(UListener):
    def __init__(self) -> None:
        pass

    def on_receive(self, topic: UUri, payload: UPayload, attributes: UAttributes) -> UStatus:
        """
        Method called to handle/process events.<br><br>
        @param topic: Topic the underlying source of the message.
        @param payload: Payload of the message.
        @param attributes: Transportation attributes.
        @return Returns an Ack every time a message is received and processed.
        """
        # global on_receive_items
        print("Listener onreceived")
        print("MATTHEW is awesome!!!")
        print(f"{payload}")

        # TODO: on_receive response
        # on_receive_items.append((topic, payload, attributes))
        # evt.set()
        # evt.clear()
        #self.tm_socket.send()

        return UStatus(code=UCode.OK, message="all good") 
    
listener: UListener = SocketUListener()

uri: str = "/body.access//door.front_left#Door"

def build_cloud_event():
    return CloudEvent(spec_version="1.0", source="https://example.com", id="HARTLEY IS THE BEST")

def build_upayload():
    any_obj = Any()
    any_obj.Pack(build_cloud_event())
    return UPayload(format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF, value=any_obj.SerializeToString())

def build_uattributes():
    return UAttributesBuilder.publish(UPriority.UPRIORITY_CS4).build()


# def process_on_receive(agent):
#     while True:
#         print("MADe it inside")
#         evt.wait()
#         if len(on_receive_items) > 0:
#             print("item to send...")
#             for on_rec_item in on_receive_items:
#                 agent.on_receive_command_TA_to_TM("on_receive", on_rec_item[0], on_rec_item[1], on_rec_item[2])



if __name__ == "__main__":
    socket_utransport = SocketUTransport("127.0.0.1", 44444)
    agent = SocketTestAgent("127.0.0.5", 12345, socket_utransport, listener)

    # thread = Thread(target = process_on_receive, args = (agent,))
    # thread.start()
    #thread.join()

    topic = LongUriSerializer().deserialize(uri)
    payload: UPayload = build_upayload()
    attributes: UAttributes = build_uattributes()


    agent.send_to_TM(json.dumps({'SDK_name': "java"}))