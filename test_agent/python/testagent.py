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
import json
import logging
import socket
import sys
import time
from threading import Thread

from google.protobuf import any_pb2
from google.protobuf.json_format import MessageToDict
from google.protobuf.wrappers_pb2 import StringValue
from uprotocol.proto.uattributes_pb2 import UPriority, UMessageType, UAttributes
from uprotocol.proto.umessage_pb2 import UMessage
from uprotocol.proto.upayload_pb2 import UPayload, UPayloadFormat
from uprotocol.proto.uri_pb2 import UUri, UAuthority, UEntity, UResource
from uprotocol.proto.ustatus_pb2 import UStatus, UCode
from uprotocol.rpc.calloptions import CallOptions
from uprotocol.uuid.factory.uuidfactory import Factories
from uprotocol.transport.builder.uattributesbuilder import UAttributesBuilder
from uprotocol.transport.ulistener import UListener
from uprotocol.uri.serializer.longuriserializer import LongUriSerializer

import constants as CONSTANTS

sys.path.append("../")
from up_client_socket.python.socket_transport import SocketUTransport

logging.basicConfig(format='%(levelname)s| %(filename)s:%(lineno)s %(message)s')
logger = logging.getLogger('File:Line# Debugger')
logger.setLevel(logging.DEBUG)


class SocketUListener(UListener):

    def on_receive(self, umsg: UMessage) -> None:
        logger.info("Listener received")
        if umsg.attributes.type == UMessageType.UMESSAGE_TYPE_REQUEST:
            logger.info("REQUEST RECEIVED")
            # send hardcoded response
            attributes = UAttributesBuilder.response(umsg.attributes.sink, umsg.attributes.source,
                                                     UPriority.UPRIORITY_CS4, umsg.attributes.id).build()
            any_obj = any_pb2.Any()
            any_obj.Pack(StringValue(value="SuccessRPCResponse"))
            res_msg = UMessage(attributes=attributes, payload=UPayload(value=any_obj.SerializeToString(),
                                                                       format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF_WRAPPED_IN_ANY))
            transport.send(res_msg)
        else:
            send_to_test_manager(umsg, CONSTANTS.RESPONSE_ON_RECEIVE)

class PerformanceUListener(UListener):

    def on_receive(self, umsg: UMessage) -> None:
        logger.info("Published Message received")
        send_to_test_manager({"id": str(umsg.attributes.id.msb), "received_timestamp": str(int(time.time() * 1000))}, CONSTANTS.SUB_ON_RECEIVE)

def send_to_test_manager(response, action):
    if not isinstance(response, (dict, str)):
        response = MessageToDict(response, including_default_value_fields=True, preserving_proto_field_name=True)
    # Create a new dictionary
    response_dict = {'data': response, 'action': action, 'ue': 'python'}
    response_dict = json.dumps(response_dict).encode('utf-8')
    ta_socket.sendall(response_dict)
    logger.info(f"Sent to TM {response_dict}")


def dict_to_proto(parent_json_obj, parent_proto_obj):
    def populate_fields(json_obj, proto_obj):
        for key, value in json_obj.items():
            if 'BYTES:' in value:
                value = value.replace('BYTES:', '')
                value = value.encode('utf-8')
            if hasattr(proto_obj, key):
                if isinstance(value, dict):
                    # Recursively update the nested message object
                    populate_fields(value, getattr(proto_obj, key))
                else:
                    field_type = type(getattr(proto_obj, key))
                    try:
                        if field_type == int:
                            value = int(value)
                        elif field_type == float:
                            value = float(value)
                    except:
                        pass
                    setattr(proto_obj, key, value)
        return proto_obj

    populate_fields(parent_json_obj, parent_proto_obj)

    return parent_proto_obj


def handle_send_command(json_msg):
    umsg = dict_to_proto(json_msg["data"], UMessage())
    return transport.send(umsg)


def handle_register_listener_command(json_msg):
    uri = dict_to_proto(json_msg["data"], UUri())
    return transport.register_listener(uri, listener)


def handle_unregister_listener_command(json_msg):
    uri = dict_to_proto(json_msg["data"], UUri())
    return transport.unregister_listener(uri, listener)


def handle_invoke_method_command(json_msg):
    uri = dict_to_proto(json_msg["data"], UUri())
    payload = dict_to_proto(json_msg["data"]["payload"], UPayload())
    res_future = transport.invoke_method(uri, payload, CallOptions())

    def handle_response(message):
        message = message.result()
        send_to_test_manager(message, CONSTANTS.RESPONSE_RPC)

    res_future.add_done_callback(handle_response)


def handle_uri_serialize_command(json_msg):
    uri = dict_to_proto(json_msg["data"], UUri())
    send_to_test_manager(LongUriSerializer().serialize(uri), CONSTANTS.SERIALIZE_URI)


def handle_uri_deserialize_command(json_msg):
    send_to_test_manager(LongUriSerializer().deserialize(json_msg["data"]), CONSTANTS.DESERIALIZE_URI)

def handle_performance_publish_command(json_msg):
    for i in range(int(json_msg["data"]["topics"])):
        uuri = UUri(authority=UAuthority(name="vcu.someVin.veh.ultifi.gm.com"),
            entity=UEntity(name="performance.test", version_major=1, id=1234),
            resource=UResource(name = "dummy_" + str(i)))
        for j in range(int(json_msg["data"]["events"])):
            id = Factories.UUIDV6.create()
            attributes = UAttributes(source=uuri, id=id, type=UMessageType.UMESSAGE_TYPE_PUBLISH, priority=UPriority.UPRIORITY_CS4)
            umsg = UMessage(attributes=attributes,)
            transport.send(umsg)
            dict_obj = {"id": str(id.msb), "published_timestamp": str(int(time.time() * 1000))}
            send_to_test_manager(dict_obj, CONSTANTS.PUB_ON_RECEIVE)
            time.sleep(int(json_msg["data"]["interval"]) / 1000)
    
    time.sleep(int(json_msg["data"]["timeout"]))
    send_to_test_manager({}, CONSTANTS.PUB_COMPLETE)
    return UStatus(code=UCode.OK, message="OK")

def handle_performance_subscribe_command(json_msg):
    status_msgs = []
    for i in range(int(json_msg["data"]["topics"])):
        uuri = UUri(authority=UAuthority(name="vcu.someVin.veh.ultifi.gm.com"),
                entity=UEntity(name="performance.test", version_major=1, id=1234),
                resource=UResource(name = "dummy_" + str(i)))
        status_msgs.append(transport.register_listener(uuri, performance_listener))
    all_okay = True
    for msg in status_msgs:
        if msg != UStatus(code=UCode.OK, message="OK"):
            all_okay = False
            fail_msg = msg
    return UStatus(code=UCode.OK, message="OK") if all_okay else fail_msg

def handle_unregister_subscribers_command(json_msg):
    status_msgs = []
    for i in range(int(json_msg["data"]["topics"])):
        uuri = UUri(authority=UAuthority(name="vcu.someVin.veh.ultifi.gm.com"),
                entity=UEntity(name="performance.test", version_major=1, id=1234),
                resource=UResource(name = "dummy_" + str(i)))
        status_msgs.append(transport.unregister_listener(uuri, performance_listener))
    all_okay = True
    for msg in status_msgs:
        if msg != UStatus(code=UCode.OK, message="OK"):
            all_okay = False
            fail_msg = msg
    return UStatus(code=UCode.OK, message="OK") if all_okay else fail_msg    


action_handlers = {CONSTANTS.SEND_COMMAND: handle_send_command,
                   CONSTANTS.REGISTER_LISTENER_COMMAND: handle_register_listener_command,
                   CONSTANTS.UNREGISTER_LISTENER_COMMAND: handle_unregister_listener_command,
                   CONSTANTS.INVOKE_METHOD_COMMAND: handle_invoke_method_command,
                   CONSTANTS.SERIALIZE_URI: handle_uri_serialize_command,
                   CONSTANTS.DESERIALIZE_URI: handle_uri_deserialize_command,
                   CONSTANTS.PERFORMANCE_PUBLISHER: handle_performance_publish_command,
                   CONSTANTS.PERFORMANCE_SUBSCRIBER: handle_performance_subscribe_command,
                   CONSTANTS.UNREGISTER_SUBSCRIBERS: handle_unregister_subscribers_command}


def process_message(json_data):
    action = json_data["action"]
    status = None
    if action in action_handlers:
        status = action_handlers[action](json_data)

    if status is not None:
        send_to_test_manager(status, action)


def receive_from_tm():
    while True:
        recv_data = ta_socket.recv(CONSTANTS.BYTES_MSG_LENGTH)
        if not recv_data or recv_data == b"":
            return
        # Deserialize the JSON data
        json_data = json.loads(recv_data.decode('utf-8'))
        logger.info('Received data from test manager: %s', json_data)
        process_message(json_data)


if __name__ == '__main__':
    listener = SocketUListener()
    performance_listener = PerformanceUListener()
    transport = SocketUTransport()
    ta_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ta_socket.connect(CONSTANTS.TEST_MANAGER_ADDR)
    thread = Thread(target=receive_from_tm)
    thread.start()
    send_to_test_manager({'SDK_name': "python"}, "initialize")
