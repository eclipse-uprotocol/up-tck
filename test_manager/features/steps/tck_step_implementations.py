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
import codecs
from typing import Any, Dict
from uprotocol.proto.ustatus_pb2 import UCode

from behave import when, then, given
from behave.runner import Context
from hamcrest import assert_that, equal_to


@given('"{sdk_name}" creates data for "{command}"')
@when('"{sdk_name}" creates data for "{command}"')
def create_sdk_data(context, sdk_name: str, command: str):
    context.json_dict = {}
    context.status_json = None
    if sdk_name == "uE1":
        sdk_name = context.config.userdata['uE1']

    while not context.tm.has_sdk_connection(sdk_name):
        continue

    context.ue = sdk_name
    context.action = command


@then('the serialized uri received is "{expected_uri}"')
def serialized_uri_received(context, expected_uri: str):
    try:
        actual_uri: str = context.response_data
        assert_that(expected_uri, equal_to(actual_uri))
    except AssertionError:
        raise AssertionError(
            f"Assertion error. Expected is {expected_uri} but "
            f"received {actual_uri}"
        )
    except Exception as ae:
        raise ValueError(f"Exception occurred. {ae}")


@then('the serialized uuid received is "{expected_uuid}"')
def serialized_uuid_received(context, expected_uuid: str):
    try:
        actual_uuid: str = context.response_data

        assert_that(expected_uuid, equal_to(actual_uuid))
    except AssertionError:
        raise AssertionError(
            f"Assertion error. Expected is {expected_uuid} but "
            f"received {actual_uuid}"
        )
    except Exception as ae:
        raise ValueError(f"Exception occurred. {ae}")


@then('receives validation result as "{expected_result}"')
def receive_validation_result(context, expected_result):
    if expected_result == "none":
        return
    try:
        expected_result = expected_result.strip()
        actual_val_res = context.response_data["result"]
        assert_that(expected_result, equal_to(actual_val_res))
    except AssertionError:
        raise AssertionError(
            f"Assertion error. Expected is {expected_result} but "
            f"received {repr(actual_val_res)}"
        )
    except Exception as ae:
        raise ValueError(f"Exception occurred. {ae}")


@then('receives validation message as "{expected_message}"')
def receive_validation_result(context, expected_message):
    if expected_message == "none":
        return
    try:
        expected_message = expected_message.strip()
        actual_val_msg = context.response_data["message"]
        assert_that(expected_message, equal_to(actual_val_msg))
    except AssertionError:
        raise AssertionError(
            f"Assertion error. Expected is {expected_message} but "
            f"received {repr(actual_val_msg)}"
        )
    except Exception as ae:
        raise ValueError(f"Exception occurred. {ae}")


@when('sends a "{command}" request with serialized input "{serialized}"')
def send_serialized_command(context, command: str, serialized: str):
    context.logger.info(f"Json request for {command} -> {serialized}")
    response_json: Dict[str, Any] = context.tm.request(
        context.ue, context.action, serialized
    )
    context.logger.info(f"Response Json {command} -> {response_json}")

    if response_json is None:
        raise AssertionError("Response from Test Manager is None")
    elif "data" not in response_json:
        raise AssertionError(
            '"data" field name doesn\'t exist on top response JSON level'
        )
    context.response_data = response_json["data"]


@then("the deserialized uri received should have the following properties")
def verify_uri_received_properties(context):
    deserialized_uri: Dict[str, Any] = flatten_dict(context.response_data)
    context.logger.info(f"deserialized_uri_dict -> {deserialized_uri}")

    # Iterate over the rows of the table and verify the received properties
    int_type_fields = set(
        [
            "entity.id",
            "entity.version_major",
            "entity.version_minor",
            "resource.id",
        ]
    )
    bytes_type_fields = set(["authority.id", "authority.ip"])

    try:
        for row in context.table:
            field: str = row["Field"]
            expected_value: str = row["Value"]
            context.logger.info(
                f"field {field}; {deserialized_uri[field]} vs. {expected_value}"
            )
            if len(expected_value) > 0:

                if field in int_type_fields:
                    expected_value = int(expected_value)
                elif field in bytes_type_fields:
                    expected_value: bytes = expected_value.encode()
                    deserialized_uri[field] = str(
                        deserialized_uri[field]
                    ).encode()
                assert_that(deserialized_uri[field], equal_to(expected_value))
            else:
                assert_that(
                    len(deserialized_uri[field]) > 0,
                    equal_to(len(expected_value) > 0),
                )

    except AssertionError as ae:
        raise AssertionError(f"Assertion error. {ae}")


@then("the deserialized uuid received should have the following properties")
def verify_uuid_received_properties(context):
    context.logger.info(
        f"deserialized context.response_data -> {context.response_data}"
    )

    deserialized_uuid: Dict[str, int] = flatten_dict(context.response_data)
    context.logger.info(f"deserialized_uuid_dict -> {deserialized_uuid}")

    # Iterate over the rows of the table and verify the received properties
    int_type_fields = set(["msb", "lsb"])
    try:
        for row in context.table:
            field = row["Field"]
            expected_value = row["Value"]
            assert_that(
                field in deserialized_uuid, equal_to(len(expected_value) > 0)
            )

            if len(expected_value) > 0:
                if field in int_type_fields:
                    expected_value: int = int(expected_value)
                assert_that(deserialized_uuid[field], equal_to(expected_value))
    except AssertionError as ae:
        raise AssertionError(f"Assertion error. {ae}")


@given('sets "{key}" to "{value}"')
@when('sets "{key}" to "{value}"')
def set_key_to_val(context: Context, key: str, value: str):
    if key not in context.json_dict:
        context.json_dict[key] = value


@given('sets "{key}" to ""')
def set_blank_key(context, key):
    pass


@given('sets "{key}" to b"{value}"')
@when('sets "{key}" to b"{value}"')
def set_key_to_bytes(context, key: str, value: str):
    if key not in context.json_dict:
        context.json_dict[key] = "BYTES:" + value


@given('sends "{command}" request')
@when('sends "{command}" request')
def send_command_request(context, command: str):
    context.json_dict = unflatten_dict(context.json_dict)
    context.logger.info(
        f"Json request for {command} -> {str(context.json_dict)}"
    )

    response_json: Dict[str, Any] = context.tm.request(
        context.ue, command, context.json_dict
    )
    context.logger.info(f"Response Json {command} -> {response_json}")
    context.response_data = response_json["data"]


@then('the status received with "{field_name}" is "{expected_value}"')
def receive_status(context, field_name: str, expected_value: str):
    try:
        actual_value: str = context.response_data[field_name]
        expected_value: int = getattr(UCode, expected_value)
        assert_that(expected_value, equal_to(actual_value))
    except AssertionError:
        raise AssertionError(
            f"Assertion error. Expected is {expected_value} but "
            f"received {context.response_data[field_name]}"
        )
    except Exception as ae:
        raise ValueError(f"Exception occurred. {ae}")


@then(
    '"{sender_sdk_name}" sends onreceive message with field "{field_name}" as b"{expected_value}"'
)
def receive_value_as_bytes(
    context, sender_sdk_name: str, field_name: str, expected_value: str
):
    try:
        expected_value = expected_value.strip()
        context.logger.info(f"getting on_receive_msg from {sender_sdk_name}")
        on_receive_msg: Dict[str, Any] = context.tm.get_onreceive(
            sender_sdk_name
        )
        context.logger.info(f"got on_receive_msg:  {on_receive_msg}")
        val = access_nested_dict(on_receive_msg["data"], field_name)
        context.logger.info(f"val {field_name}:  {val}")

        rec_field_value = val.encode("utf-8")
        assert (
            rec_field_value.split(b"googleapis.com/")[1]
            == expected_value.encode("utf-8").split(b"googleapis.com/")[1]
        )

    except AssertionError:
        raise AssertionError(
            f"Assertion error. Expected is {expected_value.encode('utf-8')} but "
            f"received {rec_field_value}"
        )
    except Exception as ae:
        raise ValueError(f"Exception occurred. {ae}")


@then('"{sdk_name}" receives data field "{field_name}" as b"{expected_value}"')
def receive_rpc_response_as_bytes(
    context, sdk_name, field_name: str, expected_value: str
):
    try:
        actual_value: str = access_nested_dict(
            context.response_data, field_name
        )
        actual_value: bytes = actual_value.encode("utf-8")

        # Convert bytes to byte string with escape sequences
        actual_value = codecs.encode(
            actual_value.decode("utf-8"), "unicode_escape"
        )
        assert (
            actual_value.split(b"googleapis.com/")[1]
            == expected_value.encode("utf-8").split(b"googleapis.com/")[1]
        )
    except KeyError:
        raise KeyError(f"Key error. {sdk_name} has not received rpc response.")
    except AssertionError:
        raise AssertionError(
            f"Assertion error. Expected is {expected_value.encode('utf-8')} but "
            f"received {repr(actual_value)}"
        )
    except Exception as ae:
        raise ValueError(f"Exception occurred. {ae}")


def bytes_to_base64_str(b: bytes) -> str:
    return base64.b64encode(b).decode("ascii")


def base64_str_to_bytes(base64_str: str) -> bytes:
    base64_bytes: bytes = base64_str.encode("ascii")
    return base64.b64decode(base64_bytes)


@then('receives micro serialized uri "{expected_bytes_as_base64_str}"')
def receive_micro_serialized_uuri(context, expected_bytes_as_base64_str: str):
    if expected_bytes_as_base64_str == "<empty>":
        expected_bytes_as_base64_str = ""

    expected_bytes: bytes = base64_str_to_bytes(expected_bytes_as_base64_str)
    context.logger.info(f"expected_bytes: {expected_bytes}")

    try:
        actual_bytes_as_str: str = context.response_data
        actual_bytes: bytes = actual_bytes_as_str.encode("iso-8859-1")

        context.logger.info(
            f"actual: {actual_bytes} | expect: {expected_bytes}"
        )
        assert_that(expected_bytes, equal_to(actual_bytes))
    except AssertionError:
        raise AssertionError(
            f"Assertion error. Expected is {expected_bytes} but "
            f"received {actual_bytes}"
        )
    except Exception as ae:
        raise ValueError(f"Exception occurred. {ae}")


@when(
    'sends a "{command}" request with micro serialized input "{micro_serialized_uri_as_base64_str}"'
)
def send_micro_serialized_command(
    context, command: str, micro_serialized_uri_as_base64_str: str
):
    if micro_serialized_uri_as_base64_str == "<empty>":
        micro_serialized_uri_as_base64_str = ""

    micro_serialized_uri: bytes = base64_str_to_bytes(
        micro_serialized_uri_as_base64_str
    )
    context.logger.info(
        f"Json request for {command} -> {micro_serialized_uri}"
    )

    micro_serialized_uri_as_str = micro_serialized_uri.decode("iso-8859-1")
    response_json: Dict[str, Any] = context.tm.request(
        context.ue, command, micro_serialized_uri_as_str
    )

    context.logger.info(f"Response Json {command} -> {response_json}")
    context.response_data = response_json["data"]


def access_nested_dict(dictionary, keys):
    keys = keys.split(".")
    value = dictionary
    for key in keys:
        value = value[key]
    return value


def flatten_dict(nested_dict, parent_key="", sep="."):
    flattened = {}
    for k, v in nested_dict.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, dict):
            flattened.update(flatten_dict(v, new_key, sep=sep))
        else:
            flattened[new_key] = v
    return flattened


def unflatten_dict(d, delimiter="."):
    unflattened = {}
    for key, value in d.items():
        parts = key.split(delimiter)
        temp = unflattened
        for part in parts[:-1]:
            if part not in temp:
                temp[part] = {}
            temp = temp[part]
        temp[parts[-1]] = value
    return unflattened
