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
import socket
from typing import Set, Tuple
from uprotocol.uri.serializer.longuriserializer import LongUriSerializer
from uprotocol.transport.ulistener import UListener
from up_client_socket_python.socket_utransport import SocketUTransport
from uprotocol.proto.uattributes_pb2 import UAttributes
from uprotocol.proto.uri_pb2 import UUri
from uprotocol.proto.uuid_pb2 import UUID
from uprotocol.proto.upayload_pb2 import UPayload
from uprotocol.transport.utransport import UTransport
from uprotocol.proto.ustatus_pb2 import UStatus, UCode
from uprotocol.proto.uattributes_pb2 import UPriority
from uprotocol.proto.umessage_pb2 import UMessage
from test_ulistener import SocketUListener
from test_ulistener_reply import SocketUListenerReply
from uprotocol.transport.builder.uattributesbuilder import UAttributesBuilder
from multipledispatch import dispatch
from uprotocol.proto.cloudevents_pb2 import CloudEvent
from google.protobuf.any_pb2 import Any
from uprotocol.proto.upayload_pb2 import UPayload, UPayloadFormat


def build_cloud_event():
    return CloudEvent(spec_version="1.0", source="helloworld.response.come idk", id="HELLO WORLD RESPONSE!!!")

def build_upayload():
    any_obj = Any()
    any_obj.Pack(build_cloud_event())
    return UPayload(format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF, value=any_obj.SerializeToString())


class SenderToServer:
    def __init__(self, server_ip: str, server_port: int) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        self.socket.connect((server_ip, server_port))  
    
    @dispatch(UUri)
    def send(self, topic: UUri):
        umsg = UMessage(source=topic) 
        umsg_serialized: bytes = umsg.SerializeToString()

        self.socket.send(umsg_serialized)
        
    @dispatch(UUri, UPayload, UAttributes)
    def send(self, topic: UUri, payload: UPayload, attributes: UAttributes):
        umsg = UMessage(source=topic, attributes=attributes, payload=payload) 
        umsg_serialized: bytes = umsg.SerializeToString()

        self.socket.send(umsg_serialized)
    
    
    @dispatch(UMessage)
    def send(self, umsg: UMessage):
        umsg_serialized: bytes = umsg.SerializeToString()

        self.socket.send(umsg_serialized)

class MessageCache:
    def __init__(self) -> None:
        self.seen_msgs: Set[tuple[bytes, bytes, bytes]] = set()
        
    def __convert_to_bytes(self, topic: UUri, payload: UPayload, attributes: UAttributes) -> Tuple[bytes, bytes, bytes]:
        topic_b: bytes = topic.SerializeToString()
        payload_b: bytes = payload.SerializeToString()
        attributes_b: bytes = attributes.SerializeToString()
        
        return (topic_b, payload_b, attributes_b)
    
    def has_seen(self, topic: UUri, payload: UPayload, attributes: UAttributes):
        recv_msg: tuple[bytes, bytes, bytes] = self.__convert_to_bytes(topic, payload, attributes)
        
        return recv_msg in self.seen_msgs
    
    def add_message(self, topic: UUri, payload: UPayload, attributes: UAttributes):
        recv_msg: tuple[bytes, bytes, bytes] = self.__convert_to_bytes(topic, payload, attributes)

        self.seen_msgs.add(recv_msg)


        
class RequestResponder(UListener):
    
    def __init__(self, sender: SenderToServer) -> None:
        self.sender = sender
        self.seen_msgs_cache: MessageCache = MessageCache()
        
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
        # topic_b: bytes = topic.SerializeToString()
        # payload_b: bytes = payload.SerializeToString()
        # attributes_b: bytes = attributes.SerializeToString()
        
        # recv_msg: tuple[bytes, bytes, bytes] = (topic_b, payload_b, attributes_b)
        
        # if seen before, then dont send
        if self.seen_msgs_cache.has_seen(topic, payload, attributes):
            
        # if recv_msg in self.seen_msgs:
            return UStatus(code=UCode.OK, message="all good") 
        # self.seen_msgs.add(recv_msg)
        self.seen_msgs_cache.add_message(topic, payload, attributes)
        
        try:
            response_reqid: UUID = attributes.id
        except AttributeError as ae:
            raise Exception(ae)   
        except Exception as err:
            raise Exception(err)   
        print("##### HANDLE DATA #######")
        
        response_topic = topic
        response_payload = build_upayload() 
        response_attr = self.__build_uattributes(response_reqid)
        
        self.seen_msgs_cache.add_message(response_topic, response_payload, response_attr)

        umsg = UMessage(source=response_topic, attributes=response_attr, payload=response_payload) 

        self.sender.send(umsg)

        return UStatus(code=UCode.OK, message="all good") 


DISPATCHER_PORT = 44444
DISPATCHER_IP = "127.0.0.1" 

uURI: str = "/body.access//door.front_left#Door"

if __name__ == "__main__":
    service = SocketUTransport(DISPATCHER_IP, DISPATCHER_PORT)
    hello_request_topic: UUri = LongUriSerializer().deserialize(uURI)

    
    sender_to_dispatcher = SenderToServer(DISPATCHER_IP, DISPATCHER_PORT)
    helloworld_request_responder: UListener = RequestResponder(sender_to_dispatcher)

    service.register_listener(hello_request_topic, helloworld_request_responder)

