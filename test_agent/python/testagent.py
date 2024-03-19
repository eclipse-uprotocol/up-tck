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
import os
import socket
import sys
from threading import Thread

from google.protobuf import any_pb2
from google.protobuf.json_format import MessageToDict
from google.protobuf.wrappers_pb2 import Int32Value
from uprotocol.proto.uattributes_pb2 import UPriority, UMessageType
from uprotocol.proto.umessage_pb2 import UMessage
from uprotocol.proto.upayload_pb2 import UPayload, UPayloadFormat
from uprotocol.proto.uri_pb2 import UUri
from uprotocol.rpc.calloptions import CallOptions
from uprotocol.transport.builder.uattributesbuilder import UAttributesBuilder
from uprotocol.transport.ulistener import UListener

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
            # send hardcoded response
            attributes = UAttributesBuilder.response(umsg.attributes.sink, umsg.attributes.source,
                                                     UPriority.UPRIORITY_CS4, umsg.id).build()
            any_obj = any_pb2.Any()
            any_obj.Pack(Int32Value(value=3))
            res_msg = UMessage(attributes=attributes, payload=UPayload(value=any_obj.SerializeToString(),
                                                                       format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF_WRAPPED_IN_ANY))
            transport.send(res_msg)
        else:
            send_to_test_manager(umsg, CONSTANTS.RESPONSE_ON_RECEIVE)


def send_to_test_manager(response, action):
    if not isinstance(response, dict):
        response = MessageToDict(response, including_default_value_fields=True, preserving_proto_field_name=True)

    # Create a new dictionary
    response_dict = {'data': response, 'action': action}
    response_dict = json.dumps(response_dict).encode()
    ta_socket.sendall(response_dict)
    logger.info(f"Sent to TM {response_dict}")


def dict_to_proto(parent_json_obj, parent_proto_obj):
    def populate_fields(json_obj, proto_obj):
        for key, value in json_obj.items():
            if 'BYTES:' in value:
                value = value.replace('BYTES:', '')
                value = value.encode()
            if hasattr(proto_obj, key):
                if isinstance(value, dict):
                    # Recursively update the nested message object
                    populate_fields(value, getattr(proto_obj, key))
                else:
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
    payload = dict_to_proto(json_msg["payload"], UPayload())
    transport.invoke_method(uri, payload, CallOptions())
    return None


action_handlers = {
    CONSTANTS.SEND_COMMAND: handle_send_command,
    CONSTANTS.REGISTER_LISTENER_COMMAND: handle_register_listener_command,
    CONSTANTS.UNREGISTER_LISTENER_COMMAND: handle_unregister_listener_command,
    CONSTANTS.INVOKE_METHOD_COMMAND: handle_invoke_method_command
}


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
        if recv_data == b"":
            logger.info("Closing TA Client Socket")
            ta_socket.close()
            return  # Deserialize the JSON data
        json_data = json.loads(recv_data.decode())
        logger.info('Received data from test manager: %s', json_data)
        process_message(json_data)


if __name__ == '__main__':
    listener = SocketUListener()
    transport = SocketUTransport()
    ta_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ta_socket.connect(CONSTANTS.TEST_MANAGER_ADDR)

    thread = Thread(target=receive_from_tm)
    thread.start()
    send_to_test_manager({'SDK_name': "python"}, "initialize")
