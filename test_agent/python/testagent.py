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

from concurrent.futures import Future
import json
import logging
import socket
import sys
import time
import git
from threading import Thread
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timezone

from google.protobuf import any_pb2
from google.protobuf.message import Message
from google.protobuf.descriptor import FieldDescriptor
from google.protobuf.wrappers_pb2 import StringValue
from google.protobuf.internal.enum_type_wrapper import EnumTypeWrapper
from uprotocol.proto.uattributes_pb2 import (
    UPriority,
    UMessageType,
    CallOptions,
    UAttributes,
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

import constants.constants as CONSTANTS
import constants.actioncommands as ACTION_COMMANDS
from constants.actioncommands import UAttributeBuilderCommands
from constants.error_messages import UAttributeBuilderErrors

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
        """When receives a message, responds to TA or TM with own message

        Args:
            umsg (UMessage): request message
        """
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
            send_to_test_manager(umsg, ACTION_COMMANDS.RESPONSE_ON_RECEIVE)


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


def dict_to_proto(parent_json_obj: Dict[str, Any], parent_proto_obj: Message):
    """converts a json/dict to a proto type with filled fields

    Args:
        parent_json_obj (Dict[str, Any]): root/beginning json data struct
        parent_proto_obj (Message): root/beginning protobuf data struct
    """

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
                        if field_type == int:
                            value = int(value)
                        elif field_type == float:
                            value = float(value)
                        elif isinstance(value, str) and field_type == bytes:
                            if value == "":
                                value = value.encode("utf-8")
                            else:
                                raise ValueError(
                                    "bytes json data MUST have prepended 'BYTES:' when sent value as a str"
                                )

                    except Exception:
                        pass

                    setattr(proto_obj, field_name, value)
        return proto_obj

    if isinstance(parent_json_obj, dict):
        populate_fields(parent_json_obj, parent_proto_obj)
    else:
        raise TypeError("variable parent_json_obj is not a Dict type")

    return parent_proto_obj


def check_proto_enum_value(
    value: Any, proto_enum: EnumTypeWrapper
) -> Optional[Any]:
    """checks if value exists within the enum protobuf

    Args:
        value (Any): a value protobuf enum can hold
        proto_enum (EnumTypeWrapper): protobuf enum with specific keys/values

    Returns:
        Optional[Any]: returns inputted value if value exists in protobuf enum
    """
    try:
        proto_enum.Name(value)
        return value
    except:
        return None


def handle_send_command(json_msg: Dict[str, Any]) -> UStatus:
    """converts json data to UMessage protobuf, and sends umsg to a Test Agent
    using UTransport

    Args:
        json_msg (Dict[str, Any]): given data as a json
    Returns:
        UStatus: the response after sending
    """
    umsg = dict_to_proto(json_msg["data"], UMessage())
    umsg.attributes.id.CopyFrom(Factories.UPROTOCOL.create())
    return transport.send(umsg)


def handle_register_listener_command(json_msg: Dict[str, Any]) -> UStatus:
    """Current Test Agent subscribes/registers to given UUri topic
    and when receive data to subbed topic, then acts w SocketUlistener listener
    Args:
        json_msg (Dict[str, Any]): given data as a json

    Returns:
        UStatus: the response after subscribing
    """
    uri = dict_to_proto(json_msg["data"], UUri())
    status: UStatus = transport.register_listener(uri, listener)
    return status


def handle_unregister_listener_command(json_msg: Dict[str, Any]) -> UStatus:
    """Current Test Agent unsubscribes/unregisters to given UUri topic

    Args:
        json_msg (Dict[str, Any]): given data as a json

    Returns:
        UStatus: the response after unsubscribing
    """
    uri = dict_to_proto(json_msg["data"], UUri())
    return transport.unregister_listener(uri, listener)


def handle_invoke_method_command(json_msg: Dict[str, Any]):
    """sends req to Test Agents subbed to UUri topic and calls the UListener
    in each subbed Test Agent, then gets a response from the UListener

    Args:
        json_msg (Dict[str, Any]): given data as a json
    """
    uri = dict_to_proto(json_msg["data"], UUri())
    payload = dict_to_proto(json_msg["data"]["payload"], UPayload())
    res_future: Future = transport.invoke_method(
        uri, payload, CallOptions(ttl=10000)
    )

    def handle_response(message: Future):
        message: Message = message.result()
        send_to_test_manager(
            message,
            ACTION_COMMANDS.INVOKE_METHOD_COMMAND,
            received_test_id=json_msg["test_id"],
        )

    res_future.add_done_callback(handle_response)


def handle_long_serialize_uuri(json_msg: Dict[str, Any]):
    """Given uuri data, then long serialize and return it back to Test Manager

    Args:
        json_msg (Dict[str, Any]): given data as a json
    """
    uri: UUri = dict_to_proto(json_msg["data"], UUri())
    serialized_uuri: str = LongUriSerializer().serialize(uri)
    send_to_test_manager(
        serialized_uuri,
        ACTION_COMMANDS.SERIALIZE_URI,
        received_test_id=json_msg["test_id"],
    )


def handle_long_deserialize_uri(json_msg: Dict[str, Any]):
    """Given serialized uuri data, then long deserialize and return UUri proto
    back to Test Manager

    Args:
        json_msg (Dict[str, Any]): given data as a json
    """
    uuri: UUri = LongUriSerializer().deserialize(json_msg["data"])
    send_to_test_manager(
        uuri,
        ACTION_COMMANDS.DESERIALIZE_URI,
        received_test_id=json_msg["test_id"],
    )


def handle_long_deserialize_uuid(json_msg: Dict[str, Any]):
    """Given serialized UUID data, then long deserialize and return UUID proto
    back to Test Manager

    Args:
        json_msg (Dict[str, Any]): given data as a json
    """
    uuid: UUID = LongUuidSerializer().deserialize(json_msg["data"])
    send_to_test_manager(
        uuid,
        ACTION_COMMANDS.DESERIALIZE_UUID,
        received_test_id=json_msg["test_id"],
    )


def handle_long_serialize_uuid(json_msg: Dict[str, Any]):
    """Given serialized UUID data, then long deserialize and return UUID proto
    back to Test Manager

    Args:
        json_msg (Dict[str, Any]): given data as a json
    """
    uuid: UUID = dict_to_proto(json_msg["data"], UUID())
    serialized_uuid: str = LongUuidSerializer().serialize(uuid)
    send_to_test_manager(
        serialized_uuid,
        ACTION_COMMANDS.SERIALIZE_UUID,
        received_test_id=json_msg["test_id"],
    )


def handle_uri_validate_command(json_msg: Dict[str, Any]):
    """Given uuri and validation type, then validate and send response to TM

    Args:
        json_msg (Dict[str, Any]): given data as a json
    """
    val_type: str = json_msg["data"]["validation_type"]
    uuri_data: Dict[str, Any] = json_msg["data"]["uuri"]

    uuri: UUri = dict_to_proto(uuri_data, UUri())

    validator_func = {
        "uri": UriValidator.validate,
        "rpc_response": UriValidator.validate_rpc_response,
        "rpc_method": UriValidator.validate_rpc_method,
        "is_empty": UriValidator.is_empty,
        "is_resolved": UriValidator.is_resolved,
        "is_micro_form": UriValidator.is_micro_form,
        "is_long_form": UriValidator.is_long_form,
    }.get(val_type)

    if validator_func:
        status: Union[bool, ValidationResult] = validator_func(uuri)
        if isinstance(status, bool):
            result = str(status)
            message = ""
        else:
            result = str(status.is_success())
            message = status.get_message()
        send_to_test_manager(
            {"result": result, "message": message},
            ACTION_COMMANDS.VALIDATE_URI,
            received_test_id=json_msg["test_id"],
        )
    else:
        send_to_test_manager(
            {
                "result": "False",
                "message": "Nonexistent UriValidator function",
            },
            ACTION_COMMANDS.VALIDATE_URI,
            received_test_id=json_msg["test_id"],
        )


def handle_micro_serialize_uri_command(json_msg: Dict[str, Any]):
    """Given Uuri data, micro serialize into bytes, then encode to utf-8 str
    so can send response back to Test Manager

    Args:
        json_msg (Dict[str, Any]): given data as a json
    """
    uri: UUri = dict_to_proto(json_msg["data"], UUri())
    serialized_uuri: bytes = MicroUriSerializer().serialize(uri)
    # Use "iso-8859-1" to decode bytes -> str, so no UnicodeDecodeError if "utf-8" decode
    serialized_uuri_json_packed: str = serialized_uuri.decode("iso-8859-1")
    send_to_test_manager(
        serialized_uuri_json_packed,
        ACTION_COMMANDS.MICRO_SERIALIZE_URI,
        received_test_id=json_msg["test_id"],
    )


def handle_micro_deserialize_uri_command(json_msg: Dict[str, Any]):
    """Given encoded micro serialized UUri data, decode str into bytes,
    then micro deserialize to UUri proto and send to Test Manager

    Args:
        json_msg (Dict[str, Any]): given data as a json
    """
    sent_micro_serialized_uuri: str = json_msg["data"]
    # Incoming micro serialized uuri is sent as an "iso-8859-1" str
    micro_serialized_uuri: bytes = sent_micro_serialized_uuri.encode(
        "iso-8859-1"
    )
    uuri: UUri = MicroUriSerializer().deserialize(micro_serialized_uuri)
    send_to_test_manager(
        uuri,
        ACTION_COMMANDS.MICRO_DESERIALIZE_URI,
        received_test_id=json_msg["test_id"],
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
        ACTION_COMMANDS.VALIDATE_UUID,
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
        ACTION_COMMANDS.VALIDATE_UATTRIBUTES,
        received_test_id=json_msg["test_id"],
    )


def build_UAttributes(
    builder: UAttributesBuilder, requested_uattribute_data: Dict[str, Any]
) -> Union[UAttributes, str]:
    """sets requested_uattribute_data json into UAttributesBuilder and builds,
    or returns an error message

    Args:
        builder (UAttributesBuilder): initial UAttributesBuilder w/ preset data
        requested_uattribute_data (Dict[str, Any]): given json data

    Returns:
        Union[UAttributes, str]: UAttributes proto or error message
    """
    for uattr_field_name, uattr_value in requested_uattribute_data.items():
        try:
            builder_field_value = getattr(builder, uattr_field_name)
        except AttributeError:
            # if attribute does not exist in UAttributesBuilder, ignore it
            continue

        if builder_field_value is None:  # if builder field is empty
            try:
                if uattr_field_name in ["source", "sink"]:
                    uattr_value: UUri = dict_to_proto(uattr_value, UUri())
                elif uattr_field_name == "reqid":
                    uattr_value: UUID = dict_to_proto(uattr_value, UUID())
                elif uattr_field_name == "commstatus":
                    uattr_value: Optional[int] = check_proto_enum_value(
                        uattr_value, UCode
                    )
                    if uattr_value is None:
                        raise ValueError("enum value out of bound!")
                elif uattr_field_name == "ttl" or uattr_field_name == "plevel":
                    if not isinstance(uattr_value, int):
                        raise TypeError(
                            f"{uattr_field_name} should be int type"
                        )
                    elif uattr_value < 0:
                        raise ValueError(f"{uattr_field_name} should be >= 0")
                elif (
                    uattr_field_name == "token"
                    or uattr_field_name == "traceparent"
                ):
                    if not isinstance(uattr_value, str):
                        raise TypeError(
                            f"{uattr_field_name} should be str type"
                        )

            except TypeError:
                attributes = UAttributeBuilderErrors.bad_data_type(
                    uattr_field_name
                )
                return attributes
            except ValueError:
                attributes = UAttributeBuilderErrors.bad_data_value(
                    uattr_field_name
                )
                return attributes
            except AttributeError:
                attributes = UAttributeBuilderErrors.bad_data_type(
                    uattr_field_name
                )
                return attributes

            setattr(builder, uattr_field_name, uattr_value)

    attributes: UAttributes = builder.build()
    return attributes


def get_uuri(
    field_name: str,
    uattributes_data: Dict[str, Any],
    command: str,
    test_id: str,
) -> UUri:
    """populates UUri proto or sends error message to Test Manager

    Args:
        field_name (str): "source" or "sink" key names
        uattributes_data (Dict[str, Any]): given UAttributes json data
        command (str): which UAttribute builder command failed when
            respond w/ error message
        test_id (str): respective message test id to respond w/ error message

    Returns:
        UUri: UUri proto
    """
    if field_name not in uattributes_data:
        send_to_test_manager(
            UAttributeBuilderErrors.not_given(field_name),
            command,
            received_test_id=test_id,
        )
        return
    try:
        source: UUri = dict_to_proto(uattributes_data[field_name], UUri())
        return source
    except TypeError:
        send_to_test_manager(
            UAttributeBuilderErrors.bad_data_type(field_name),
            command,
            received_test_id=test_id,
        )
        return
    except ValueError:
        send_to_test_manager(
            UAttributeBuilderErrors.bad_data_value(field_name),
            command,
            received_test_id=test_id,
        )
        return
    except AttributeError:
        send_to_test_manager(
            UAttributeBuilderErrors.bad_data_type(field_name),
            command,
            received_test_id=test_id,
        )
        return


def get_priority(
    uattributes_data: Dict[str, Any], command: str, test_id: str
) -> int:
    """Get the priority from given UAttr json data

    Args:
        uattributes_data (Dict[str, Any]): given UAttributes json data
        command (str): which UAttribute builder command failed when
            respond w/ error message
        test_id (str): respective message test id to respond w/ error message

    Returns:
        int: uPriority enum value
    """
    if "priority" not in uattributes_data:
        send_to_test_manager(
            UAttributeBuilderErrors.not_given("priority"),
            command,
            received_test_id=test_id,
        )
        return
    priority: Optional[int] = check_proto_enum_value(
        uattributes_data["priority"], UPriority
    )
    if priority is None:
        send_to_test_manager(
            UAttributeBuilderErrors.bad_data_value("priority"),
            command,
            received_test_id=test_id,
        )
        return

    return priority


def get_ttl(
    uattributes_data: Dict[str, Any], command: str, test_id: str
) -> int:
    """Get the ttl from given UAttr json data

    Args:
        uattributes_data (Dict[str, Any]): given UAttributes json data
        command (str): which UAttribute builder command failed when
            respond w/ error message
        test_id (str): respective message test id to respond w/ error message

    Returns:
        int: the ttl
    """
    if "ttl" not in uattributes_data:
        send_to_test_manager(
            UAttributeBuilderErrors.not_given("ttl"),
            command,
            received_test_id=test_id,
        )
        return

    try:
        if not isinstance(uattributes_data["ttl"], int):
            raise TypeError("ttl should be int type")
        elif uattributes_data["ttl"] < 0:
            raise ValueError("ttl should be >= 0")

        ttl: int = int(uattributes_data["ttl"])
    except TypeError:
        send_to_test_manager(
            UAttributeBuilderErrors.bad_data_type("ttl"),
            command,
            received_test_id=test_id,
        )
        return
    except ValueError:
        send_to_test_manager(
            UAttributeBuilderErrors.bad_data_value("ttl"),
            command,
            received_test_id=test_id,
        )
        return

    return ttl


def get_reqid(
    uattributes_data: Dict[str, Any], command: str, test_id: str
) -> UUID:
    """Get the reqid from given UAttr json data

    Args:
        uattributes_data (Dict[str, Any]): given UAttributes json data
        command (str): which UAttribute builder command failed when
            respond w/ error message
        test_id (str): respective message test id to respond w/ error message

    Returns:
        UUID: the reqid
    """
    if "reqid" not in uattributes_data:
        send_to_test_manager(
            UAttributeBuilderErrors.not_given("reqid"),
            command,
            received_test_id=test_id,
        )
        return
    try:
        reqid: UUID = dict_to_proto(uattributes_data["reqid"], UUID())
        return reqid
    except TypeError:
        send_to_test_manager(
            UAttributeBuilderErrors.bad_data_type("reqid"),
            command,
            received_test_id=test_id,
        )
        return
    except ValueError:
        send_to_test_manager(
            UAttributeBuilderErrors.bad_data_value("reqid"),
            command,
            received_test_id=test_id,
        )
        return
    except AttributeError:
        send_to_test_manager(
            UAttributeBuilderErrors.bad_data_type("reqid"),
            command,
            received_test_id=test_id,
        )
        return


def build_publish_uattributes(json_msg: Dict[str, Any]):
    """Builds UAttribute protobuf and replies back to Test Manager
    Prerequisite: incoming keys in json_msg["data"] MUST match with UAttributesBuilder's fields
    Args:
        json_msg (Dict[str, Any]): incoming json data
    """
    uattributes_data: Dict[str, Any] = json_msg["data"]
    test_id: str = json_msg["test_id"]

    source: UUri = get_uuri(
        "source",
        uattributes_data,
        UAttributeBuilderCommands.PUBLISH.value,
        test_id,
    )
    if source is None:
        return

    priority: UPriority = get_priority(
        uattributes_data, UAttributeBuilderCommands.PUBLISH.value, test_id
    )
    if priority is None:
        return

    builder: UAttributesBuilder = UAttributesBuilder.publish(source, priority)

    attributes = build_UAttributes(builder, uattributes_data)

    send_to_test_manager(
        attributes,
        UAttributeBuilderCommands.PUBLISH.value,
        received_test_id=json_msg["test_id"],
    )


def build_notification_uattributes(json_msg: Dict[str, Any]):
    """Builds UAttribute protobuf and replies back to Test Manager
    Prerequisite: incoming keys in json_msg["data"] MUST match with UAttributesBuilder's fields
    Args:
        json_msg (Dict[str, Any]): incoming json data
    """
    uattributes_data: Dict[str, Any] = json_msg["data"]
    test_id: str = json_msg["test_id"]

    source: UUri = get_uuri(
        "source",
        uattributes_data,
        UAttributeBuilderCommands.NOTIFICATION.value,
        test_id,
    )
    if source is None:
        return

    priority: UPriority = get_priority(
        uattributes_data, UAttributeBuilderCommands.NOTIFICATION.value, test_id
    )
    if priority is None:
        return

    sink: UUri = get_uuri(
        "sink",
        uattributes_data,
        UAttributeBuilderCommands.NOTIFICATION.value,
        test_id,
    )
    if sink is None:
        return

    builder: UAttributesBuilder = UAttributesBuilder.notification(
        source, sink, priority
    )

    attributes = build_UAttributes(builder, uattributes_data)

    send_to_test_manager(
        attributes,
        UAttributeBuilderCommands.NOTIFICATION.value,
        received_test_id=json_msg["test_id"],
    )


def build_request_uattributes(json_msg: Dict[str, Any]):
    """Builds UAttribute protobuf and replies back to Test Manager
    Prerequisite: incoming keys in json_msg["data"] MUST match with UAttributesBuilder's fields
    Args:
        json_msg (Dict[str, Any]): incoming json data
    """
    uattributes_data: Dict[str, Any] = json_msg["data"]
    test_id: str = json_msg["test_id"]

    source: UUri = get_uuri(
        "source",
        uattributes_data,
        UAttributeBuilderCommands.REQUEST.value,
        test_id,
    )
    if source is None:
        return

    priority: UPriority = get_priority(
        uattributes_data, UAttributeBuilderCommands.REQUEST.value, test_id
    )
    if priority is None:
        return

    sink: UUri = get_uuri(
        "sink",
        uattributes_data,
        UAttributeBuilderCommands.REQUEST.value,
        test_id,
    )
    if sink is None:
        return

    ttl: int = get_ttl(
        uattributes_data, UAttributeBuilderCommands.REQUEST.value, test_id
    )
    if ttl is None:
        return

    builder: UAttributesBuilder = UAttributesBuilder.request(
        source, sink, priority, ttl
    )

    attributes = build_UAttributes(builder, uattributes_data)

    send_to_test_manager(
        attributes,
        UAttributeBuilderCommands.REQUEST.value,
        received_test_id=json_msg["test_id"],
    )


def build_response_uattributes(json_msg: Dict[str, Any]):
    """Builds UAttribute protobuf and replies back to Test Manager
    Prerequisite: incoming keys in json_msg["data"] MUST match with UAttributesBuilder's fields
    Args:
        json_msg (Dict[str, Any]): incoming json data
    """
    uattributes_data: Dict[str, Any] = json_msg["data"]
    test_id: str = json_msg["test_id"]

    source: UUri = get_uuri(
        "source",
        uattributes_data,
        UAttributeBuilderCommands.RESPONSE.value,
        test_id,
    )
    if source is None:
        return

    priority: UPriority = get_priority(
        uattributes_data, UAttributeBuilderCommands.RESPONSE.value, test_id
    )
    if priority is None:
        return

    sink: UUri = get_uuri(
        "sink",
        uattributes_data,
        UAttributeBuilderCommands.RESPONSE.value,
        test_id,
    )
    if sink is None:
        return

    reqid: UUID = get_reqid(
        uattributes_data, UAttributeBuilderCommands.RESPONSE.value, test_id
    )
    if reqid is None:
        return

    builder: UAttributesBuilder = UAttributesBuilder.response(
        source, sink, priority, reqid
    )

    attributes = build_UAttributes(builder, uattributes_data)

    send_to_test_manager(
        attributes,
        UAttributeBuilderCommands.RESPONSE.value,
        received_test_id=json_msg["test_id"],
    )


action_handlers = {
    ACTION_COMMANDS.SEND_COMMAND: handle_send_command,
    ACTION_COMMANDS.REGISTER_LISTENER_COMMAND: handle_register_listener_command,
    ACTION_COMMANDS.UNREGISTER_LISTENER_COMMAND: handle_unregister_listener_command,
    ACTION_COMMANDS.INVOKE_METHOD_COMMAND: handle_invoke_method_command,
    ACTION_COMMANDS.SERIALIZE_URI: handle_long_serialize_uuri,
    ACTION_COMMANDS.DESERIALIZE_URI: handle_long_deserialize_uri,
    ACTION_COMMANDS.SERIALIZE_UUID: handle_long_serialize_uuid,
    ACTION_COMMANDS.DESERIALIZE_UUID: handle_long_deserialize_uuid,
    ACTION_COMMANDS.VALIDATE_URI: handle_uri_validate_command,
    ACTION_COMMANDS.VALIDATE_UATTRIBUTES: handle_uattributes_validate_command,
    ACTION_COMMANDS.MICRO_SERIALIZE_URI: handle_micro_serialize_uri_command,
    ACTION_COMMANDS.MICRO_DESERIALIZE_URI: handle_micro_deserialize_uri_command,
    ACTION_COMMANDS.VALIDATE_UUID: handle_uuid_validate_command,
    UAttributeBuilderCommands.PUBLISH.value: build_publish_uattributes,
    UAttributeBuilderCommands.NOTIFICATION.value: build_notification_uattributes,
    UAttributeBuilderCommands.REQUEST.value: build_request_uattributes,
    UAttributeBuilderCommands.RESPONSE.value: build_response_uattributes,
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
