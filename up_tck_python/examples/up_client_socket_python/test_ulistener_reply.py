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


from typing import Set
from uprotocol.proto.uattributes_pb2 import UAttributes
from uprotocol.proto.upayload_pb2 import UPayload
from uprotocol.proto.uri_pb2 import UUri
from uprotocol.proto.ustatus_pb2 import UStatus, UCode
from uprotocol.proto.uuid_pb2 import UUID
from uprotocol.transport.ulistener import UListener
from uprotocol.transport.utransport import UTransport
from uprotocol.transport.builder.uattributesbuilder import UAttributesBuilder
from uprotocol.proto.uattributes_pb2 import UPriority

import logging 

logging.basicConfig(format='%(asctime)s %(message)s')
# Create logger
logger = logging.getLogger('simple_example')
logger.setLevel(logging.INFO)


class SocketUListenerReply(UListener):
    def __init__(self, socket_utransport: UTransport) -> None:
        self.socket_utransport: UTransport = socket_utransport
        self.seen_msgs: Set[tuple[bytes, bytes, bytes]] = set()

    def __build_uattributes(self, req: UUID):
        return UAttributesBuilder.publish(UPriority.UPRIORITY_CS4).withReqId(req).build()

    def on_receive(self, topic: UUri, payload: UPayload, attributes: UAttributes) -> UStatus:
        """
        Method called to handle/process events.<br><br>
        @param topic: Topic the underlying source of the message.
        @param payload: Payload of the message.
        @param attributes: Transportation attributes.
        @return Returns an Ack every time a message is received and processed.
        """
        topic_b: bytes = topic.SerializeToString()
        payload_b: bytes = payload.SerializeToString()
        attributes_b: bytes = attributes.SerializeToString()
        
        recv_msg: tuple[bytes, bytes, bytes] = (topic_b, payload_b, attributes_b)
        # if seen before, then dont send
        if recv_msg in self.seen_msgs:
            return UStatus(code=UCode.OK, message="all good") 
        self.seen_msgs.add(recv_msg)

        try:
            response_reqid: UUID = attributes.id
        except AttributeError as ae:
            logger.error("attributes.reqid doesnt exist")
            raise Exception(ae)   
        except Exception as err:
            raise Exception(err)   
        
        response_attr: UAttributes = self.__build_uattributes(response_reqid)

        self.seen_msgs.add((topic_b, payload_b, response_attr.SerializeToString() ))
        self.socket_utransport.send(topic, payload, response_attr)
        logger.info(f"Sending data back to server!")

        return UStatus(code=UCode.OK, message="all good") 