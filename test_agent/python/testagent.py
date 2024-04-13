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
import base64
from concurrent.futures import Future
import json
import logging
import socket
import sys
from threading import Thread
from typing import Any, Dict, List, Set, Union

from google.protobuf import any_pb2
from google.protobuf.message import Message
from google.protobuf.json_format import MessageToDict
from google.protobuf.descriptor import FieldDescriptor
from google.protobuf.wrappers_pb2 import StringValue
from uprotocol.proto.uattributes_pb2 import UPriority, UMessageType
from uprotocol.proto.umessage_pb2 import UMessage
from uprotocol.proto.upayload_pb2 import UPayload, UPayloadFormat
from uprotocol.proto.ustatus_pb2 import UStatus, UCode
from uprotocol.proto.uri_pb2 import UUri
from uprotocol.proto.uuid_pb2 import UUID
from uprotocol.rpc.calloptions import CallOptions
from uprotocol.transport.builder.uattributesbuilder import UAttributesBuilder
from uprotocol.transport.ulistener import UListener
from uprotocol.uri.serializer.longuriserializer import LongUriSerializer
from uprotocol.uri.serializer.microuriserializer import MicroUriSerializer
from uprotocol.uuid.serializer.longuuidserializer import LongUuidSerializer

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

def message_to_dict(message: Message) -> Dict[str, Any]:
    """Converts protobuf Message to Dict and keeping respective data types

    Args:
        message (Message): protobuf Message

    Returns:
        Dict[str, Any]: Dict/JSON version of the Message
    """
    result: Dict[str, Any] = {}
    
    all_fields: List[FieldDescriptor] = message.DESCRIPTOR.fields
    for field in all_fields:
        
        value = getattr(message, field.name, field.default_value)
        if isinstance(value, bytes):
            value: str = value.decode()
        
        # if a protobuf Message object
        if hasattr(value, 'DESCRIPTOR'):
            result[field.name] = message_to_dict(value)
        elif field.label == FieldDescriptor.LABEL_REPEATED:
            repeated = []
            for sub_msg in value:
                if hasattr(sub_msg, 'DESCRIPTOR'):
                    # add Message type protobuf
                    repeated.append(message_to_dict(sub_msg))
                else:
                    # add primitive type (str, bool, bytes, int)
                    repeated.append(value)
            result[field.name] = repeated
        
        # if the field is not a protobuf object (aka, primitive type)
        elif field.label == FieldDescriptor.LABEL_REQUIRED or field.label == FieldDescriptor.LABEL_OPTIONAL:
            result[field.name] = value

    return result


def send_to_test_manager(response: Union[Message, str, dict], action: str, received_test_id: str = ""):
    if not isinstance(response, (dict, str)):
        # converts protobuf to dict
        response = message_to_dict(response)

    # Create response as json/dict
    response_dict = {'data': response, 'action': action, 'ue': 'python', 'test_id': received_test_id}
    response_dict = json.dumps(response_dict).encode('utf-8')
    ta_socket.sendall(response_dict)
    logger.info(f"Sent to TM {response_dict}")


def dict_to_proto(parent_json_obj, parent_proto_obj):
    def populate_fields(json_obj, proto_obj):
        for field_name, value in json_obj.items():
            if 'BYTES:' in value:
                value = value.replace('BYTES:', '')
                value = value.encode('utf-8')
            if hasattr(proto_obj, field_name):
                if isinstance(value, dict):
                    # Recursively update the nested message object
                    populate_fields(value, getattr(proto_obj, field_name))
                else:
                    field_type = type(getattr(proto_obj, field_name))
                    try:
                        if field_type == int:
                            value = int(value)
                        elif field_type == float:
                            value = float(value)
                    except:
                        pass
                    setattr(proto_obj, field_name, value)
        return proto_obj

    populate_fields(parent_json_obj, parent_proto_obj)

    return parent_proto_obj


def handle_send_command(json_msg):
    umsg = dict_to_proto(json_msg["data"], UMessage())
    return transport.send(umsg)


def handle_register_listener_command(json_msg) -> UStatus:
    uri = dict_to_proto(json_msg["data"], UUri())
    status: UStatus = transport.register_listener(uri, listener)
    return status


def handle_unregister_listener_command(json_msg):
    uri = dict_to_proto(json_msg["data"], UUri())
    return transport.unregister_listener(uri, listener)


def handle_invoke_method_command(json_msg):
    uri = dict_to_proto(json_msg["data"], UUri())
    payload = dict_to_proto(json_msg["data"]["payload"], UPayload())
    res_future: Future = transport.invoke_method(uri, payload, CallOptions())

    def handle_response(message):
        message: Message = message.result()
        send_to_test_manager(message, CONSTANTS.INVOKE_METHOD_COMMAND, received_test_id=json_msg["test_id"])

    res_future.add_done_callback(handle_response)


def send_longserialize_uuri(json_msg: Dict[str, Any]):
    uri: UUri = dict_to_proto(json_msg["data"], UUri())
    serialized_uuri: str = LongUriSerializer().serialize(uri)
    send_to_test_manager(serialized_uuri, CONSTANTS.SERIALIZE_URI, received_test_id=json_msg["test_id"])


def send_longdeserialize_uri(json_msg: Dict[str, Any]):
    uuri: UUri = LongUriSerializer().deserialize(json_msg["data"])
    send_to_test_manager(uuri, CONSTANTS.DESERIALIZE_URI, received_test_id=json_msg["test_id"])


def send_longdeserialize_uuid(json_msg: Dict[str, Any]):
    uuid: UUID = LongUuidSerializer().deserialize(json_msg["data"])
    send_to_test_manager(uuid, CONSTANTS.DESERIALIZE_UUID, received_test_id=json_msg["test_id"])


def send_longserialize_uuid(json_msg: Dict[str, Any]):
    uuid: UUID = dict_to_proto(json_msg["data"], UUID())
    serialized_uuid: str = LongUuidSerializer().serialize(uuid)
    send_to_test_manager(serialized_uuid, CONSTANTS.SERIALIZE_UUID, received_test_id=json_msg["test_id"])

def send_microserialize_uri(json_msg: Dict[str, Any]):
    uri: UUri = dict_to_proto(json_msg["data"], UUri())
    serialized_uuri: bytes = MicroUriSerializer().serialize(uri)
    serialized_uuri_json_packed: str = serialized_uuri.decode("ansi")  # use "ansi" so no UnicodeDecodeError if use "utf-8"
    send_to_test_manager(serialized_uuri_json_packed, CONSTANTS.MICRO_SERIALIZE_URI, received_test_id=json_msg["test_id"])

def send_microdeserialize_uri(json_msg: Dict[str, Any]):
    sent_micro_serialized_uuri: str = json_msg["data"]
    micro_serialized_uuri: bytes = sent_micro_serialized_uuri.encode("ansi")
    uuri: UUri = MicroUriSerializer().deserialize(micro_serialized_uuri)
    send_to_test_manager(uuri, CONSTANTS.MICRO_DESERIALIZE_URI, received_test_id=json_msg["test_id"])


action_handlers = {CONSTANTS.SEND_COMMAND: handle_send_command,
                   CONSTANTS.REGISTER_LISTENER_COMMAND: handle_register_listener_command,
                   CONSTANTS.UNREGISTER_LISTENER_COMMAND: handle_unregister_listener_command,
                   CONSTANTS.INVOKE_METHOD_COMMAND: handle_invoke_method_command,
                   CONSTANTS.SERIALIZE_URI: send_longserialize_uuri,
                   CONSTANTS.DESERIALIZE_URI: send_longdeserialize_uri,
                   CONSTANTS.SERIALIZE_UUID: send_longserialize_uuid,
                   CONSTANTS.DESERIALIZE_UUID: send_longdeserialize_uuid,
                   CONSTANTS.MICRO_SERIALIZE_URI: send_microserialize_uri,
                   CONSTANTS.MICRO_DESERIALIZE_URI: send_microdeserialize_uri
                   }


def process_message(json_data):
    action: str = json_data["action"]
    status = None
    if action in action_handlers:
        status: UStatus = action_handlers[action](json_data)

    # For UTransport interface methods
    if status is not None:
        send_to_test_manager(status, action, received_test_id=json_data["test_id"])


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
    transport = SocketUTransport()
    ta_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ta_socket.connect(CONSTANTS.TEST_MANAGER_ADDR)
    thread = Thread(target=receive_from_tm)
    thread.start()
    send_to_test_manager({'SDK_name': "python"}, "initialize")
