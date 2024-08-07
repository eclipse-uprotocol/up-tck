"""
SPDX-FileCopyrightText: Copyright (c) 2024 Contributors to the Eclipse Foundation
See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
SPDX-FileType: SOURCE
SPDX-License-Identifier: Apache-2.0
"""

import asyncio
import json
import logging
import random
import socket
import sys
import time
from argparse import ArgumentParser
from datetime import datetime, timezone
from threading import Thread
from typing import Any, Dict, List, Union

import git
from constants import actioncommands, constants
from google.protobuf import any_pb2
from google.protobuf.descriptor import FieldDescriptor
from google.protobuf.message import Message
from google.protobuf.wrappers_pb2 import StringValue
from uprotocol.communication.upayload import UPayload
from uprotocol.transport.builder.umessagebuilder import UMessageBuilder
from uprotocol.transport.ulistener import UListener
from uprotocol.transport.validator import uattributesvalidator
from uprotocol.transport.validator.uattributesvalidator import (
    UAttributesValidator,
)
from uprotocol.uri.serializer.uriserializer import UriSerializer
from uprotocol.uri.validator.urivalidator import UriValidator
from uprotocol.uuid.factory.uuidfactory import Factories
from uprotocol.uuid.factory.uuidutils import UUIDUtils
from uprotocol.uuid.serializer.uuidserializer import UuidSerializer
from uprotocol.uuid.validator.uuidvalidator import UuidValidator, Validators
from uprotocol.v1.uattributes_pb2 import UAttributes, UMessageType, UPayloadFormat
from uprotocol.v1.ucode_pb2 import UCode
from uprotocol.v1.umessage_pb2 import UMessage
from uprotocol.v1.uri_pb2 import UUri
from uprotocol.v1.ustatus_pb2 import UStatus
from uprotocol.v1.uuid_pb2 import UUID
from uprotocol.validation.validationresult import ValidationResult

repo = git.Repo(".", search_parent_directories=True)
sys.path.insert(0, repo.working_tree_dir)
from up_client_socket.python.socket_transport import SocketUTransport

logging.basicConfig(format="%(levelname)s| %(filename)s:%(lineno)s %(message)s")
logger = logging.getLogger("File:Line# Debugger")
logger.setLevel(logging.DEBUG)

RESPONSE_URI = UUri(ue_id=random.randrange(0, 0x7FFF), ue_version_major=1, resource_id=0)

sdkname = "python"
transport_name = "socket"  # Not used right now, will be when more transports are added to python


class SocketUListener(UListener):
    def on_receive(self, umsg: UMessage) -> None:
        logger.info("Listener received")
        if umsg is None:
            raise ValueError("UMessage is None")
        elif not isinstance(umsg, UMessage):
            raise TypeError("umsg is not of type UMessage")
        elif umsg.attributes is None:
            raise ValueError("UMessage attributes is None")
        if umsg.attributes.type == UMessageType.UMESSAGE_TYPE_REQUEST:
            any_obj = any_pb2.Any()
            any_obj.Pack(StringValue(value="SuccessRPCResponse"))
            payload = UPayload(
                data=any_obj.SerializeToString(),
                format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF_WRAPPED_IN_ANY,
            )
            res_msg = UMessageBuilder.response(
                umsg.attributes.sink,
                umsg.attributes.source,
                umsg.attributes.id,
            ).build_from_upayload(payload)
            transport.send(res_msg)
        else:
            send_to_test_manager(umsg, actioncommands.RESPONSE_ON_RECEIVE)


transport = SocketUTransport(RESPONSE_URI)
listener = SocketUListener()


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
        elif field.label == FieldDescriptor.LABEL_REQUIRED or field.label == FieldDescriptor.LABEL_OPTIONAL:
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
        "ue": sdkname,
        "test_id": received_test_id,
    }
    response_dict = json.dumps(response_dict).encode("utf-8")
    ta_socket.sendall(response_dict)
    logger.info(f"Sent to TM {response_dict}")


def dict_to_proto(parent_json_obj: Dict[str, Any], parent_proto_obj: Message):
    def populate_fields(json_obj: Dict[str, Any], proto_obj):
        for field_name, value in json_obj.items():
            # check if incoming json request is a "bytes" type with prepended prefix
            if isinstance(value, str) and "BYTES:" in value:
                value = value.replace("BYTES:", "")
                value = value.encode("utf-8")

            if hasattr(proto_obj, field_name):
                if isinstance(value, dict):
                    # Recursively update the nested message object
                    populate_fields(value, getattr(proto_obj, field_name))
                else:
                    field_type = type(getattr(proto_obj, field_name))
                    try:
                        if field_type is int:
                            value = int(value)
                        elif field_type is float:
                            value = float(value)
                        elif field_type is bytes:
                            if isinstance(value, str):
                                value = value.encode("utf-8")

                    except Exception:
                        pass

                    logger.info(f"setting {field_name} to {value}")
                    setattr(proto_obj, field_name, value)
        return proto_obj

    if isinstance(parent_json_obj, dict):
        populate_fields(parent_json_obj, parent_proto_obj)
    else:
        raise TypeError("variable parent_json_obj is not a Dict type")

    return parent_proto_obj


async def handle_send_command(json_msg):
    umsg = dict_to_proto(json_msg["data"], UMessage())
    umsg.attributes.id.CopyFrom(Factories.UPROTOCOL.create())
    return await transport.send(umsg)


async def handle_register_listener_command(json_msg) -> UStatus:
    uri = dict_to_proto(json_msg["data"], UUri())
    status: UStatus = await transport.register_listener(uri, listener)
    return status


async def handle_unregister_listener_command(json_msg):
    uri = dict_to_proto(json_msg["data"], UUri())
    return await transport.unregister_listener(uri, listener)


async def handle_serialize_uuri(json_msg: Dict[str, Any]):
    uri: UUri = dict_to_proto(json_msg["data"], UUri())
    serialized_uuri: str = UriSerializer.serialize(uri).lower()
    send_to_test_manager(
        serialized_uuri,
        actioncommands.SERIALIZE_URI,
        received_test_id=json_msg["test_id"],
    )


async def handle_deserialize_uri(json_msg: Dict[str, Any]):
    uuri: UUri = UriSerializer.deserialize(json_msg["data"])
    send_to_test_manager(
        uuri,
        actioncommands.DESERIALIZE_URI,
        received_test_id=json_msg["test_id"],
    )


async def handle_deserialize_uuid(json_msg: Dict[str, Any]):
    uuid: UUID = UuidSerializer.deserialize(json_msg["data"])
    send_to_test_manager(
        uuid,
        actioncommands.DESERIALIZE_UUID,
        received_test_id=json_msg["test_id"],
    )


def handle_serialize_uuid(json_msg: Dict[str, Any]):
    uuid: UUID = dict_to_proto(json_msg["data"], UUID())
    serialized_uuid: str = UuidSerializer.serialize(uuid)
    send_to_test_manager(
        serialized_uuid,
        actioncommands.SERIALIZE_UUID,
        received_test_id=json_msg["test_id"],
    )


async def handle_uri_validate_command(json_msg: Dict[str, Any]):
    val_type: str = json_msg["data"]["validation_type"]
    uuri_data: Dict[str, Any] = json_msg["data"]["uuri"]

    uuri: UUri = dict_to_proto(uuri_data, UUri())

    validator_func = {
        "is_empty": UriValidator.is_empty,
        "is_rpc_method": UriValidator.is_rpc_method,
        "is_rpc_response": UriValidator.is_rpc_response,
        "is_default_resource_id": UriValidator.is_default_resource_id,
        "is_topic": UriValidator.is_topic,
        "matches": UriValidator.matches,
    }.get(val_type)

    if validator_func:
        if val_type == "matches":
            uri_to_match = UriSerializer.deserialize(json_msg["data"]["uuri_2"])
            status: Union[bool, ValidationResult] = validator_func(uuri, uri_to_match)
        else:
            status: Union[bool, ValidationResult] = validator_func(uuri)
        if isinstance(status, bool):
            result = str(status)
            message = ""
        else:
            result = str(status.is_success())
            message = status.get_message()
        send_to_test_manager(
            {"result": result, "message": message},
            actioncommands.VALIDATE_URI,
            received_test_id=json_msg["test_id"],
        )
    else:
        send_to_test_manager(
            {
                "result": "False",
                "message": "Nonexistent UriValidator function",
            },
            actioncommands.VALIDATE_URI,
            received_test_id=json_msg["test_id"],
        )


async def handle_uuid_validate_command(json_msg):
    uuid_type = json_msg["data"].get("uuid_type")
    validator_type = json_msg["data"]["validator_type"]

    uuid = {
        "uprotocol": Factories.UPROTOCOL.create(),
        "invalid": UUID(msb=0, lsb=0),
        "uprotocol_time": Factories.UPROTOCOL.create(datetime.utcfromtimestamp(0).replace(tzinfo=timezone.utc)),
        "uuidv6": Factories.UUIDV6.create(),
        "uuidv4": UuidSerializer.deserialize("195f9bd1-526d-4c28-91b1-ff34c8e3632d"),
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
        actioncommands.VALIDATE_UUID,
        received_test_id=json_msg["test_id"],
    )


async def handle_uattributes_validate_command(json_msg: Dict[str, Any]):
    data = json_msg["data"]
    val_method = data.get("validation_method")
    val_type = data.get("validation_type")
    if data.get("attributes"):
        attributes = dict_to_proto(data["attributes"], UAttributes())
        if attributes.sink.authority_name == "default":
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
            "validate_permission_level": pub_val.validate_permission_level,
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
            "validate_type": not_val.validate_type,
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
        actioncommands.VALIDATE_UATTRIBUTES,
        received_test_id=json_msg["test_id"],
    )


async def handle_initialize_transport_command(json_msg: Dict[str, Any]):
    global transport, listener
    source = dict_to_proto(json_msg["data"], UUri())
    if transport_name == "socket":
        transport = SocketUTransport(source)
        listener = SocketUListener()
    else:
        send_to_test_manager(
            UStatus(code=UCode.FAILED_PRECONDITION, message="Transport not implemented"),
            actioncommands.INITIALIZE_TRANSPORT,
            received_test_id=json_msg["test_id"],
        )
        return
    send_to_test_manager(
        UStatus(code=UCode.OK, message=""),
        actioncommands.INITIALIZE_TRANSPORT,
        received_test_id=json_msg["test_id"],
    )


action_handlers = {
    actioncommands.SEND_COMMAND: handle_send_command,
    actioncommands.REGISTER_LISTENER_COMMAND: handle_register_listener_command,
    actioncommands.UNREGISTER_LISTENER_COMMAND: handle_unregister_listener_command,
    actioncommands.SERIALIZE_URI: handle_serialize_uuri,
    actioncommands.DESERIALIZE_URI: handle_deserialize_uri,
    actioncommands.SERIALIZE_UUID: handle_serialize_uuid,
    actioncommands.DESERIALIZE_UUID: handle_deserialize_uuid,
    actioncommands.VALIDATE_URI: handle_uri_validate_command,
    actioncommands.VALIDATE_UATTRIBUTES: handle_uattributes_validate_command,
    actioncommands.VALIDATE_UUID: handle_uuid_validate_command,
    actioncommands.INITIALIZE_TRANSPORT: handle_initialize_transport_command,
}


async def process_message(json_data):
    action: str = json_data["action"]
    status = None
    if action in action_handlers:
        status: UStatus = await action_handlers[action](json_data)

    # For UTransport interface methods
    if status is not None:
        send_to_test_manager(status, action, received_test_id=json_data["test_id"])


async def receive_from_tm():
    while True:
        recv_data = ta_socket.recv(constants.BYTES_MSG_LENGTH)
        if not recv_data or recv_data == b"":
            return
        # Deserialize the JSON data
        json_data = json.loads(recv_data.decode("utf-8"))
        logger.info("Received data from test manager: %s", json_data)
        await process_message(json_data)


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("-t", "--transport", dest="transport", help="Select Transport", metavar="TRANSPORT")

    parser.add_argument("-s", "--sdkname", dest="sdkname", help="Write SDK Name", metavar="SDKNAME")

    args = parser.parse_args()

    if args.sdkname is not None:
        sdkname = args.sdkname

    if args.transport is not None:
        transport_name = args.transport

    ta_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ta_socket.connect(constants.TEST_MANAGER_ADDR)
    thread = Thread(target=asyncio.run, args=(receive_from_tm(),))
    thread.start()
    send_to_test_manager({"SDK_name": sdkname}, "initialize")
