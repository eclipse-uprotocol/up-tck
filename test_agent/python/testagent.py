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
from concurrent.futures import Future
import json
import logging
import socket
import sys
import git
from threading import Thread
from typing import Any, Dict, List, Union
import time
from datetime import datetime, timezone

from google.protobuf import any_pb2
from google.protobuf.message import Message
from google.protobuf.descriptor import FieldDescriptor
from google.protobuf.wrappers_pb2 import StringValue
from uprotocol.proto.uattributes_pb2 import (
    UPriority,
    UMessageType,
    CallOptions,
    UAttributes
)
from uprotocol.transport.validate import uattributesvalidator
from uprotocol.transport.validate.uattributesvalidator import (
    UAttributesValidator,
)
from uprotocol.proto.umessage_pb2 import UMessage
from uprotocol.proto.upayload_pb2 import UPayload, UPayloadFormat
from uprotocol.proto.ustatus_pb2 import UStatus
from uprotocol.proto.uri_pb2 import UUri
from uprotocol.proto.uuid_pb2 import UUID
from uprotocol.transport.builder.uattributesbuilder import UAttributesBuilder
from uprotocol.transport.ulistener import UListener
from uprotocol.uri.serializer.longuriserializer import LongUriSerializer
from uprotocol.uri.serializer.microuriserializer import MicroUriSerializer
from uprotocol.uuid.serializer.longuuidserializer import LongUuidSerializer
from uprotocol.uuid.factory.uuidfactory import Factories
from uprotocol.uri.validator.urivalidator import UriValidator
from uprotocol.validation.validationresult import ValidationResult
from uprotocol.uuid.validate.uuidvalidator import UuidValidator, Validators
from uprotocol.uuid.factory.uuidutils import UUIDUtils
from uprotocol.proto.ustatus_pb2 import UCode

import constants as CONSTANTS

repo = git.Repo(".", search_parent_directories=True)
sys.path.insert(0, repo.working_tree_dir)
from up_client_socket.python.socket_transport import SocketUTransport

logging.basicConfig(
    format="%(levelname)s| %(filename)s:%(lineno)s %(message)s"
)
logger = logging.getLogger("File:Line# Debugger")
logger.setLevel(logging.DEBUG)


class SocketUListener(UListener):

    def on_receive(self, umsg: UMessage) -> None:
        logger.info("Listener received")
        if umsg.attributes.type == UMessageType.UMESSAGE_TYPE_REQUEST:
            attributes = UAttributesBuilder.response(
                umsg.attributes.sink,
                umsg.attributes.source,
                UPriority.UPRIORITY_CS4,
                umsg.attributes.id,
            ).build()
            any_obj = any_pb2.Any()
            any_obj.Pack(StringValue(value="SuccessRPCResponse"))
            res_msg = UMessage(
                attributes=attributes,
                payload=UPayload(
                    value=any_obj.SerializeToString(),
                    format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF_WRAPPED_IN_ANY,
                ),
            )
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

        # If a protobuf Message object
        if hasattr(value, "DESCRIPTOR"):
            result[field.name] = message_to_dict(value)
        elif field.label == FieldDescriptor.LABEL_REPEATED:
            repeated = []
            for sub_msg in value:
                if hasattr(sub_msg, "DESCRIPTOR"):
                    # Add Message type protobuf
                    repeated.append(message_to_dict(sub_msg))
                else:
                    # Add primitive type (str, bool, bytes, int)
                    repeated.append(value)
            result[field.name] = repeated

        # If the field is not a protobuf object (e.g. primitive type)
        elif (
            field.label == FieldDescriptor.LABEL_REQUIRED
            or field.label == FieldDescriptor.LABEL_OPTIONAL
        ):
            result[field.name] = value

    return result


def send_to_test_manager(
    response: Union[Message, str, dict],
    action: str,
    received_test_id: str = "",
):
    if not isinstance(response, (dict, str)):
        # Converts protobuf to dict
        response = message_to_dict(response)

    # Create response as json/dict
    response_dict = {
        "data": response,
        "action": action,
        "ue": "python",
        "test_id": received_test_id,
    }
    response_dict = json.dumps(response_dict).encode("utf-8")
    ta_socket.sendall(response_dict)
    logger.info(f"Sent to TM {response_dict}")


def dict_to_proto(parent_json_obj, parent_proto_obj):
    def populate_fields(json_obj, proto_obj):
        for field_name, value in json_obj.items():
            if "BYTES:" in value:
                value = value.replace("BYTES:", "")
                value = value.encode("utf-8")
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
                    except Exception:
                        pass
                    setattr(proto_obj, field_name, value)
        return proto_obj

    populate_fields(parent_json_obj, parent_proto_obj)

    return parent_proto_obj


def handle_send_command(json_msg):
    umsg = dict_to_proto(json_msg["data"], UMessage())
    umsg.attributes.id.CopyFrom(Factories.UPROTOCOL.create())
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
    res_future: Future = transport.invoke_method(
        uri, payload, CallOptions(ttl=10000)
    )

    def handle_response(message):
        message: Message = message.result()
        send_to_test_manager(
            message,
            CONSTANTS.INVOKE_METHOD_COMMAND,
            received_test_id=json_msg["test_id"],
        )

    res_future.add_done_callback(handle_response)


def handle_long_serialize_uuri(json_msg: Dict[str, Any]):
    uri: UUri = dict_to_proto(json_msg["data"], UUri())
    serialized_uuri: str = LongUriSerializer().serialize(uri)
    send_to_test_manager(
        serialized_uuri,
        CONSTANTS.SERIALIZE_URI,
        received_test_id=json_msg["test_id"],
    )


def handle_long_deserialize_uri(json_msg: Dict[str, Any]):
    uuri: UUri = LongUriSerializer().deserialize(json_msg["data"])
    send_to_test_manager(
        uuri, CONSTANTS.DESERIALIZE_URI, received_test_id=json_msg["test_id"]
    )


def handle_long_deserialize_uuid(json_msg: Dict[str, Any]):
    uuid: UUID = LongUuidSerializer().deserialize(json_msg["data"])
    send_to_test_manager(
        uuid, CONSTANTS.DESERIALIZE_UUID, received_test_id=json_msg["test_id"]
    )


def handle_long_serialize_uuid(json_msg: Dict[str, Any]):
    uuid: UUID = dict_to_proto(json_msg["data"], UUID())
    serialized_uuid: str = LongUuidSerializer().serialize(uuid)
    send_to_test_manager(
        serialized_uuid,
        CONSTANTS.SERIALIZE_UUID,
        received_test_id=json_msg["test_id"],
    )


def handle_uri_validate_command(json_msg):
    val_type = json_msg["data"]["type"]
    uri = LongUriSerializer().deserialize(json_msg["data"].get("uri"))

    validator_func = {
        "uri": UriValidator.validate,
        "rpc_response": UriValidator.validate_rpc_response,
        "rpc_method": UriValidator.validate_rpc_method,
        "is_empty": UriValidator.is_empty,
        "is_resolved": UriValidator.is_resolved,
        "is_micro_form": UriValidator.is_micro_form,
        "is_long_form_uuri": UriValidator.is_long_form,
        "is_long_form_uauthority": UriValidator.is_long_form,
        "is_local": UriValidator.is_local,
    }.get(val_type)

    if validator_func:
        status = validator_func(uri)
        if isinstance(status, bool):
            result = str(status)
            message = ""
        else:
            result = str(status.is_success())
            message = status.get_message()
        send_to_test_manager(
            {"result": result, "message": message},
            CONSTANTS.VALIDATE_URI,
            received_test_id=json_msg["test_id"],
        )

def handle_micro_serialize_uri_command(json_msg: Dict[str, Any]):
    uri: UUri = dict_to_proto(json_msg["data"], UUri())
    serialized_uuri: bytes = MicroUriSerializer().serialize(uri)
    # Use "iso-8859-1" to decode bytes -> str, so no UnicodeDecodeError if "utf-8" decode
    serialized_uuri_json_packed: str = serialized_uuri.decode("iso-8859-1")
    send_to_test_manager(
        serialized_uuri_json_packed, 
        CONSTANTS.MICRO_SERIALIZE_URI, 
        received_test_id=json_msg["test_id"]
    )

def handle_micro_deserialize_uri_command(json_msg: Dict[str, Any]):
    sent_micro_serialized_uuri: str = json_msg["data"]
    # Incoming micro serialized uuri is sent as an "iso-8859-1" str
    micro_serialized_uuri: bytes = sent_micro_serialized_uuri.encode("iso-8859-1")
    uuri: UUri = MicroUriSerializer().deserialize(micro_serialized_uuri)
    send_to_test_manager(
        uuri, 
        CONSTANTS.MICRO_DESERIALIZE_URI, 
        received_test_id=json_msg["test_id"]
    )

def handle_uuid_validate_command(json_msg):
    uuid_type = json_msg["data"].get("uuid_type")
    validator_type = json_msg["data"]["validator_type"]

    uuid = {
        "uprotocol": Factories.UPROTOCOL.create(),
        "invalid": UUID(msb=0, lsb=0),
        "uprotocol_time": Factories.UPROTOCOL.create(
            datetime.utcfromtimestamp(0).replace(tzinfo=timezone.utc)
        ),
        "uuidv6": Factories.UUIDV6.create(),
        "uuidv4": LongUuidSerializer().deserialize(
            "195f9bd1-526d-4c28-91b1-ff34c8e3632d"
        ),
    }.get(uuid_type)

    status = {
        "get_validator": UuidValidator.get_validator(uuid).validate(uuid),
        "uprotocol": Validators.UPROTOCOL.validator().validate(uuid),
        "uuidv6": Validators.UUIDV6.validator().validate(uuid),
        "get_validator_is_uuidv6": UUIDUtils.is_uuidv6(uuid),
    }.get(validator_type)

    if isinstance(status, bool):
        result = str(status)
        message = ""
    else:
        result = "True" if status.code == UCode.OK else "False"
        message = status.message

    send_to_test_manager(
        {"result": result, "message": message},
        CONSTANTS.VALIDATE_UUID,
        received_test_id=json_msg["test_id"],
    )


def handle_uattributes_validate_command(json_msg: Dict[str, Any]):
    data = json_msg["data"]
    val_method = data.get("validation_method")
    val_type = data.get("validation_type")
    if data.get("attributes"):
        attributes = dict_to_proto(data["attributes"], UAttributes())
        if attributes.sink.authority.name == "default":
            attributes.sink.CopyFrom(UUri())
    else:
        attributes = UAttributes()

    if data.get("id") == "uprotocol":
        attributes.id.CopyFrom(Factories.UPROTOCOL.create())
    elif data.get("id") == "uuid":
        attributes.id.CopyFrom(Factories.UUIDV6.create())

    if data.get("reqid") == "uprotocol":
        attributes.reqid.CopyFrom(Factories.UPROTOCOL.create())
    elif data.get("reqid") == "uuid":
        attributes.reqid.CopyFrom(Factories.UUIDV6.create())

    validator_type = {
        "get_validator": UAttributesValidator.get_validator,
    }.get(val_type)

    pub_val = uattributesvalidator.Validators.PUBLISH.validator()
    req_val = uattributesvalidator.Validators.REQUEST.validator()
    res_val = uattributesvalidator.Validators.RESPONSE.validator()
    not_val = uattributesvalidator.Validators.NOTIFICATION.validator()

    validator_method = {
        "publish_validator": {
            "is_expired": pub_val.is_expired,
            "validate_ttl": pub_val.validate_ttl,
            "validate_sink": pub_val.validate_sink,
            "validate_req_id": pub_val.validate_req_id,
            "validate_id": pub_val.validate_id,
            "validate_permission_level": pub_val.validate_permission_level
        }.get(val_type, pub_val.validate),
        "request_validator": {
            "is_expired": req_val.is_expired,
            "validate_ttl": req_val.validate_ttl,
            "validate_sink": req_val.validate_sink,
            "validate_req_id": req_val.validate_req_id,
            "validate_id": req_val.validate_id,
        }.get(val_type, req_val.validate),
        "response_validator": {
            "is_expired": res_val.is_expired,
            "validate_ttl": res_val.validate_ttl,
            "validate_sink": res_val.validate_sink,
            "validate_req_id": res_val.validate_req_id,
            "validate_id": res_val.validate_id,
        }.get(val_type, res_val.validate),
        "notification_validator": {
            "is_expired": not_val.is_expired,
            "validate_ttl": not_val.validate_ttl,
            "validate_sink": not_val.validate_sink,
            "validate_req_id": not_val.validate_req_id,
            "validate_id": not_val.validate_id,
            "validate_type": not_val.validate_type
        }.get(val_type, not_val.validate),
    }.get(val_method)

    if attributes.ttl == 1:
        time.sleep(0.8)

    if val_type == "get_validator":
        status = validator_type(attributes)
    if validator_method is not None:
        status = validator_method(attributes)

    if isinstance(status, ValidationResult):
        result = str(status.is_success())
        message = status.get_message()
    elif isinstance(status, bool):
        result = str(status)
        message = ""
    else:
        result = ""
        message = str(status)

    send_to_test_manager(
        {"result": result, "message": message},
        CONSTANTS.VALIDATE_UATTRIBUTES,
        received_test_id=json_msg["test_id"],
    )

action_handlers = {
    CONSTANTS.SEND_COMMAND: handle_send_command,
    CONSTANTS.REGISTER_LISTENER_COMMAND: handle_register_listener_command,
    CONSTANTS.UNREGISTER_LISTENER_COMMAND: handle_unregister_listener_command,
    CONSTANTS.INVOKE_METHOD_COMMAND: handle_invoke_method_command,
    CONSTANTS.SERIALIZE_URI: handle_long_serialize_uuri,
    CONSTANTS.DESERIALIZE_URI: handle_long_deserialize_uri,
    CONSTANTS.SERIALIZE_UUID: handle_long_serialize_uuid,
    CONSTANTS.DESERIALIZE_UUID: handle_long_deserialize_uuid,
    CONSTANTS.VALIDATE_URI: handle_uri_validate_command,
    CONSTANTS.VALIDATE_UATTRIBUTES: handle_uattributes_validate_command,
    CONSTANTS.MICRO_SERIALIZE_URI: handle_micro_serialize_uri_command,
    CONSTANTS.MICRO_DESERIALIZE_URI: handle_micro_deserialize_uri_command,
    CONSTANTS.VALIDATE_UUID: handle_uuid_validate_command
}


def process_message(json_data):
    action: str = json_data["action"]
    status = None
    if action in action_handlers:
        status: UStatus = action_handlers[action](json_data)

    # For UTransport interface methods
    if status is not None:
        send_to_test_manager(
            status, action, received_test_id=json_data["test_id"]
        )


def receive_from_tm():
    while True:
        recv_data = ta_socket.recv(CONSTANTS.BYTES_MSG_LENGTH)
        if not recv_data or recv_data == b"":
            return
        # Deserialize the JSON data
        json_data = json.loads(recv_data.decode("utf-8"))
        logger.info("Received data from test manager: %s", json_data)
        process_message(json_data)


if __name__ == "__main__":
    listener = SocketUListener()
    transport = SocketUTransport()
    ta_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ta_socket.connect(CONSTANTS.TEST_MANAGER_ADDR)
    thread = Thread(target=receive_from_tm)
    thread.start()
    send_to_test_manager({"SDK_name": "python"}, "initialize")
