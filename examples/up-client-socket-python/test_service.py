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

import time 
from uprotocol.proto.uri_pb2 import UUri, UAuthority 
from uprotocol.proto.uattributes_pb2 import UAttributes
from uprotocol.proto.upayload_pb2 import UPayload
from uprotocol.proto.umessage_pb2 import UMessage
from uprotocol.proto.cloudevents_pb2 import CloudEvent
from uprotocol.proto.upayload_pb2 import UPayload, UPayloadFormat
from uprotocol.transport.builder.uattributesbuilder import UAttributesBuilder
from uprotocol.proto.uattributes_pb2 import UPriority
from uprotocol.proto.uuid_pb2 import UUID

from google.protobuf.any_pb2 import Any

import socket
from multipledispatch import dispatch



def build_cloud_event():
    return CloudEvent(spec_version="1.0", source="https://example.com", id="HARTLEY IS THE BEST")

def build_upayload():
    any_obj = Any()
    any_obj.Pack(build_cloud_event())
    return UPayload(format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF, value=any_obj.SerializeToString())

@dispatch()
def build_uattributes():
    return UAttributesBuilder.publish(UPriority.UPRIORITY_CS4).build()

@dispatch(UUID)
def build_uattributes(req: UUID):
    return UAttributesBuilder.publish(UPriority.UPRIORITY_CS4).withReqId(req).build()

PORT = 44444
IP = "127.0.0.1" 
ADDR = (IP, PORT)

if __name__ == "__main__":
    ##SETUP
    auth = UAuthority(id=b"12345", ip=b'127.0.0.5')
    topic = UUri(authority=auth)
    payload: UPayload = build_upayload()
    attributes: UAttributes = build_uattributes()
    umsg_dummy2 = UMessage(source=topic, attributes=attributes, payload=payload) 
    umsg_dummy1 = UMessage(source=topic, payload=payload) 

    req: UUID = UUID(msb=1234, lsb=4321)
    req_dummy1: UUID = UUID(msb=4321, lsb=1234)
    req_dummy2: UUID = UUID(msb=4321, lsb=4321)

    attributes_dummy1: UAttributes = build_uattributes(req_dummy1)
    attributes_dummy2: UAttributes = build_uattributes(req_dummy2)

    umsg_dummy3 = UMessage(source=topic, payload=payload, attributes=attributes_dummy1) 
    umsg_dummy4 = UMessage(source=topic, payload=payload, attributes=attributes_dummy2) 

    # Create a socket object 
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         

    # Prerequisite for server to listen for incoming conn. requests
    server.bind(ADDR)  

    # Put the socket into listening mode 
    # NOTE: 5 connections are kept waiting 
    # if the server is busy and if a 6th socket tries to connect, then the connection is refused.
    server.listen(5)  

    clientsocket, addr = server.accept()   

    recv_data: bytes = clientsocket.recv(32767)

    # create dumby response
    print("sending dum1")
    clientsocket.send(umsg_dummy1.SerializeToString()) 

    time.sleep(3)

    # create dumby response
    print("sending dum2")
    clientsocket.send(umsg_dummy2.SerializeToString()) 

    time.sleep(3)

    # create dumby response
    print("sending dum3")
    clientsocket.send(umsg_dummy3.SerializeToString()) 

    time.sleep(3)

    # create dumby response
    print("sending dum4")
    clientsocket.send(umsg_dummy4.SerializeToString()) 
    time.sleep(3)

    #create correct response
    print("sending real")
    recv_msg = UMessage()
    recv_msg.ParseFromString(recv_data)

    attributes_real: UAttributes = build_uattributes(recv_msg.attributes.id)
    umsg_real = UMessage(source=topic, payload=payload, attributes=attributes_real) 

    clientsocket.send(umsg_real.SerializeToString()) 



