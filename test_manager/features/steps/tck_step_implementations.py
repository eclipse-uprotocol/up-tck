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

import base64
import binascii
import codecs
import datetime
import json
import os
import re
import subprocess
import sys
import time
from typing import Any, Dict, List, Union

import parse
from behave import given, register_type, then, when
from behave.runner import Context
from hamcrest import assert_that, equal_to
from uprotocol.v1.ucode_pb2 import UCode

PYTHON_TA_PATH = "/test_agent/python/testagent.py"
JAVA_TA_PATH = "/test_agent/java/target/tck-test-agent-java-jar-with-dependencies.jar"
RUST_TA_PATH = "/test_agent/rust/target/debug/rust_tck"
CPP_TA_PATH = "/test_agent/cpp/build/bin/test_agent_cpp"


def create_command(context, filepath_from_root_repo: str, transport_to_send: str, sdk_name: str) -> List[str]:
    command: List[str] = []

    full_path = os.path.abspath(os.path.dirname(os.getcwd()) + "/" + filepath_from_root_repo)

    if filepath_from_root_repo.endswith(".jar"):
        command.append("java")
        command.append("-jar")
    elif filepath_from_root_repo.endswith(".py"):
        if sys.platform == "win32":
            command.append("python")
        elif sys.platform == "linux" or sys.platform == "linux2" or sys.platform == "darwin":
            command.append("python3")
    elif os.access(full_path, os.X_OK):
        # This is an executable file
        pass
    elif not filepath_from_root_repo.endswith("rust_tck"):
        raise Exception("only accept .jar, .py, and executable files")

    command.append(full_path)

    command.append("--transport")
    command.append(transport_to_send)
    command.append("--sdkname")
    command.append(sdk_name)
    return command


def create_subprocess(command: List[str]) -> subprocess.Popen:
    # Generate a unique log file name based on the current timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"process_{timestamp}.log"

    # Construct the full log file path
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)  # Create log directory if it doesn't exist
    log_filepath = os.path.join(log_dir, log_filename)

    with open(log_filepath, 'w') as logfile:
        if sys.platform == "win32":
            process = subprocess.Popen(command, shell=True, stdout=logfile, stderr=logfile)
        elif sys.platform == "linux" or sys.platform == "linux2" or sys.platform == "darwin":
            process = subprocess.Popen(command, stdout=logfile, stderr=logfile)
        else:
            print(sys.platform)
            raise Exception("only handle Windows and Linux commands for now")

    return process


def cast_data_to_jsonable_bytes(value: str):
    return "BYTES:" + value


def cast_data_to_bytes(value: str):
    return value.encode()


def cast(value: str, data_type: str, jsonable: bool = True) -> Union[str, int, bool, float]:
    """
    Cast value to a specific type represented as a string
    @param value The original value as string data type
    @param data_type Data type to cast to
    @raises ValueError Error if a data_type is not handled below
    @return Correctly typed value
    """

    if "UCode" in value:
        enum_member: str = value.split(".")[1]
        value = getattr(UCode, enum_member)

    if data_type == "int":
        try:
            value = int(value)
        except ValueError:
            value = None
    elif data_type == "str":
        pass
    elif data_type == "bool":
        value = bool(value)
    elif data_type == "float":
        value = float(value)
    elif data_type == "bytes":
        if jsonable:
            value = cast_data_to_jsonable_bytes(value)
        else:
            value = cast_data_to_bytes(value)
    else:
        raise ValueError(f"protobuf_field_type {data_type} not handled!")

    return value


@parse.with_pattern(r".*")
def parse_nullable_string(text):
    return text


# creates behave's input data type to be empty/blank/""
register_type(NullableString=parse_nullable_string)


@given('"{sdk_name}" creates data for "{command}"')
@when('"{sdk_name}" creates data for "{command}"')
def create_sdk_data(context, sdk_name: str, command: str):
    context.json_dict = {}

    ue_number = sdk_name.replace("uE", "")
    context.logger.info(f"ue_number: {ue_number}")

    if "uE" in sdk_name:
        sdk_name = context.ue_tracker[int(ue_number) - 1][0]
        transport = context.ue_tracker[int(ue_number) - 1][1]

    if not context.tm.has_sdk_connection(sdk_name):
        context.logger.info(f"Creating {sdk_name} process...")

        base_sdk_name = re.sub(r"_\d+", "", sdk_name)
        context.logger.info(f"base_sdk_name: {base_sdk_name}")
        sdk_paths = {"python": PYTHON_TA_PATH, "java": JAVA_TA_PATH, "rust": RUST_TA_PATH, "cpp": CPP_TA_PATH}
        if base_sdk_name in sdk_paths:
            run_command = create_command(context, sdk_paths[base_sdk_name], transport, sdk_name)
            # End scrtipt after priting the command
            context.logger.info(run_command)
        else:
            raise ValueError("Invalid SDK name")

        process = create_subprocess(run_command)
        if base_sdk_name in ["python", "java", "cpp", "rust"]:
            context.ues.setdefault(base_sdk_name, []).append(process)
        else:
            raise ValueError("Invalid SDK name")

        context.logger.info(f"Created {sdk_name} process...")

        while not context.tm.has_sdk_connection(sdk_name):
            time.sleep(1)
            context.logger.info(f"Waiting for {sdk_name} to connect...")

        response_json: Dict[str, Any] = context.tm.request(
            sdk_name, "initialize_transport", context.ue_tracker[int(ue_number) - 1][2]
        )
        context.logger.info(f"Response Json {command} -> {response_json}")

        try:
            assert_that(int(response_json["data"]["code"]), equal_to(UCode.OK))
        except ValueError:
            assert_that(response_json["data"]["code"], equal_to("OK"))

        context.logger.info(f"{sdk_name} connected to Test Manager...")

    try:
        context.rust_sender
    except AttributeError:
        context.rust_sender = False

    if "rust" in sdk_name and command == "send":
        context.rust_sender = True

    context.ue = sdk_name
    context.action = command

    # if feature file provides step-table data in step definition ...
    if context.table is not None:
        for row in context.table:
            field_name: str = row["protobuf_field_names"]
            value: str = row["protobuf_field_values"]

            value = cast(value, row["protobuf_field_type"])
            context.json_dict[field_name] = value

        context.logger.info("context.json_dict")
        context.logger.info(context.json_dict)


@when('sets "{key}" to previous response data')
def sets_key_to_previous_response(context, key: str):
    if key not in context.json_dict:
        context.json_dict[key] = context.response_data


@then('the serialized uri received is "{expected_uri}"')
def serialized_uri_received(context, expected_uri: str):
    try:
        actual_uri: str = context.response_data
        assert_that(expected_uri, equal_to(actual_uri))
    except AssertionError:
        raise AssertionError(f"Assertion error. Expected is {expected_uri} but received {actual_uri}")
    except Exception as ae:
        raise ValueError(f"Exception occurred. {ae}")


@then('the serialized uuid received is "{expected_uuid}"')
def serialized_uuid_received(context, expected_uuid: str):
    try:
        actual_uuid: str = context.response_data

        assert_that(expected_uuid, equal_to(actual_uuid))
    except AssertionError:
        raise AssertionError(f"Assertion error. Expected is {expected_uuid} but received {actual_uuid}")
    except Exception as ae:
        raise ValueError(f"Exception occurred. {ae}")


@then('receives validation result as "{expected_result: NullableString}"')
def receive_validation_result(context, expected_result):
    if expected_result == "none":
        return
    try:
        expected_result = expected_result.strip()
        actual_val_res = context.response_data["result"]
        assert_that(expected_result, equal_to(actual_val_res))
    except AssertionError:
        raise AssertionError(f"Assertion error. Expected is {expected_result} but received {repr(actual_val_res)}")
    except Exception as ae:
        raise ValueError(f"Exception occurred. {ae}")


@then('receives validation message as "{expected_message:NullableString}"')
def receive_validation_result(context, expected_message):
    try:
        expected_message = expected_message.strip()
        actual_val_msg = context.response_data["message"]
        assert_that(expected_message, equal_to(actual_val_msg))
    except AssertionError:
        raise AssertionError(f"Assertion error. Expected is {expected_message} but received {repr(actual_val_msg)}")
    except Exception as ae:
        raise ValueError(f"Exception occurred. {ae}")


@when('sends a "{command}" request with serialized input "{serialized:NullableString}"')
def send_serialized_command(context, command: str, serialized: str):
    context.logger.info(f"Json request for {command} -> {serialized}")
    response_json: Dict[str, Any] = context.tm.request(context.ue, context.action, serialized)
    context.logger.info(f"Response Json {command} -> {response_json}")
    if response_json is None:
        raise AssertionError("Response from Test Manager is None")
    elif "data" not in response_json:
        raise AssertionError('"data" field name doesn\'t exist on top response JSON level')
    context.response_data = response_json["data"]


@then("the deserialized uri received should have the following properties")
def verify_uri_received_properties(context):
    deserialized_uri: Dict[str, Any] = flatten_dict(context.response_data)
    context.logger.info(f"deserialized_uri_dict -> {deserialized_uri}")

    # Iterate over the rows of the table and verify the received properties
    int_type_fields = set(
        [
            "ue_id",
            "ue_version_major",
            "resource_id",
        ]
    )
    bytes_type_fields = set(["authority.id", "authority.ip"])

    try:
        for row in context.table:
            field: str = row["Field"]
            expected_value: str = row["Value"]
            context.logger.info(f"field {field}; {deserialized_uri[field]} vs. {expected_value}")
            if len(expected_value) > 0:
                if field in int_type_fields:
                    expected_value = int(expected_value)
                elif field in bytes_type_fields:
                    expected_value: bytes = expected_value.encode()
                    deserialized_uri[field] = str(deserialized_uri[field]).encode()
                assert_that(deserialized_uri[field], equal_to(expected_value))
            else:
                assert_that(
                    len(str(deserialized_uri[field])) > 0,
                    equal_to(len(expected_value) > 0),
                )

    except AssertionError as ae:
        raise AssertionError(f"Assertion error. {ae}")


@then("the deserialized uuid received should have the following properties")
def verify_uuid_received_properties(context):
    context.logger.info(f"deserialized context.response_data -> {context.response_data}")

    deserialized_uuid: Dict[str, int] = flatten_dict(context.response_data)
    context.logger.info(f"deserialized_uuid_dict -> {deserialized_uuid}")

    # Iterate over the rows of the table and verify the received properties
    int_type_fields = set(["msb", "lsb"])
    try:
        for row in context.table:
            field = row["Field"]
            expected_value = row["Value"]
            assert_that(field in deserialized_uuid, equal_to(len(expected_value) > 0))

            if len(expected_value) > 0:
                if field in int_type_fields:
                    expected_value: int = int(expected_value)
                assert_that(int(deserialized_uuid[field]), equal_to(expected_value))
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


@given('sets "{key}" to entity URI of "{ue}"')
@when('sets "{key}" to entity URI of "{ue}"')
def set_key_to_ue_uri(context: Context, key: str, ue: str):
    ue_number = ue.replace("uE", "")
    if key not in context.json_dict:
        context.json_dict[key] = context.ue_tracker[int(ue_number) - 1][2]


@given('sends "{command}" request')
@when('sends "{command}" request')
def send_command_request(context, command: str):
    context.json_dict = unflatten_dict(context.json_dict)
    context.logger.info(f"Json request for {command} -> {str(context.json_dict)}")

    response_json: Dict[str, Any] = context.tm.request(context.ue, command, context.json_dict)
    context.logger.info(f"Response Json {command} -> {response_json}")
    context.response_data = response_json["data"]


@then('the status received with "{field_name}" is "{expected_value}"')
def receive_status(context, field_name: str, expected_value: str):
    try:
        actual_value: str = context.response_data[field_name]
        expected_value_string = expected_value
        expected_value: int = getattr(UCode, expected_value)
        try:
            assert_that(expected_value, equal_to(int(actual_value)))
        except ValueError:
            assert_that(expected_value_string, equal_to(actual_value))
    except AssertionError:
        raise AssertionError(
            f"Assertion error. Expected is {expected_value} but received {context.response_data[field_name]}"
        )
    except Exception as ae:
        raise ValueError(f"Exception occurred. {ae}")


@then('"{sender_sdk_name}" sends onreceive message with field "{field_name}" as b"{expected_value}"')
def receive_value_as_bytes(context, sender_sdk_name: str, field_name: str, expected_value: str):
    try:
        expected_value = expected_value.strip()

        ue_number = sender_sdk_name.replace("uE", "")
        context.logger.info(f"ue_number: {ue_number}")

        if "uE" in sender_sdk_name:
            sender_sdk_name = context.ue_tracker[int(ue_number) - 1][0]
        context.logger.info(f"getting on_receive_msg from {sender_sdk_name}")

        on_receive_msg: Dict[str, Any] = context.tm.get_onreceive(sender_sdk_name)
        context.logger.info(f"got on_receive_msg:  {on_receive_msg}")
        context.logger.info(f"sender_sdk_name: {sender_sdk_name}")
        if sender_sdk_name == "rust" and not context.rust_sender:
            val = on_receive_msg["data"]["payload"]
            rec_field_value = bytes(
                val.replace('"', "")
                .replace(":", "")
                .replace("\\", "")
                .replace("x", "\\x")
                .replace("}", "")
                .strip()[1:],
                "utf-8",
            )
        else:
            val = access_nested_dict(on_receive_msg["data"], field_name)
            if context.rust_sender:
                context.logger.info(f"val {field_name}:  {val}")
                context.rust_sender = False
                decoded_string = "type.googleapis.com/" + val.split(".com/")[1]
                rec_field_value = bytes(decoded_string, "utf-8")
            else:
                try:
                    rec_field_value: bytes = val.encode("utf-8")
                except Exception as e:
                    context.logger.info(f"Exception: {e}")
        try:
            data_bytes = base64.b64decode(val)
            assert (
                data_bytes.split(b"googleapis.com/")[1] == expected_value.encode("utf-8").split(b"googleapis.com/")[1]
            )
        except binascii.Error:
            assert (
                rec_field_value.split(b"googleapis.com/")[1]
                == expected_value.encode("utf-8").split(b"googleapis.com/")[1]
            )

    except AssertionError:
        raise AssertionError(
            f"Assertion error. Expected is {expected_value.encode('utf-8')} but received {rec_field_value}"
        )
    except Exception as ae:
        raise ValueError(f"Exception occurred. {ae}")


@then('"{sdk_name}" receives data field "{field_name}" as b"{expected_value}"')
def receive_rpc_response_as_bytes(context, sdk_name, field_name: str, expected_value: str):
    try:
        if sdk_name == "rust":
            actual_value = context.response_data["data"]
            actual_value = bytes(
                actual_value.split("value")[1]
                .replace('"', "")
                .replace(":", "")
                .replace("\\", "")
                .replace("x", "\\x")
                .replace("}", "")
                .strip()[1:],
                "utf-8",
            )
        else:
            actual_value: str = access_nested_dict(context.response_data, field_name)
            if context.rust_sender:
                context.rust_sender = False
                actual_value = base64.b64decode(actual_value.encode("utf-8"))
                decoded_string = actual_value.decode("utf-8")
                decoded_string = decoded_string.replace('"', "").replace("\\", "").replace("x", "\\x")[1:]
                actual_value = bytes(decoded_string, "utf-8")
            else:
                actual_value: bytes = actual_value.encode("utf-8")

        # Convert bytes to byte string with escape sequences
        actual_value = codecs.encode(actual_value.decode("utf-8"), "unicode_escape")
        assert actual_value.split(b"googleapis.com/")[1] == expected_value.encode("utf-8").split(b"googleapis.com/")[1]
    except KeyError:
        raise KeyError(f"Key error. {sdk_name} has not received rpc response.")
    except AssertionError:
        raise AssertionError(
            f"Assertion error. Expected is {expected_value.encode('utf-8')} but received {repr(actual_value)}"
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

        context.logger.info(f"actual: {actual_bytes} | expect: {expected_bytes}")
        assert_that(expected_bytes, equal_to(actual_bytes))
    except AssertionError:
        raise AssertionError(f"Assertion error. Expected is {expected_bytes} but received {actual_bytes}")
    except Exception as ae:
        raise ValueError(f"Exception occurred. {ae}")


@when('sends a "{command}" request with micro serialized input "{micro_serialized_uri_as_base64_str}"')
def send_micro_serialized_command(context, command: str, micro_serialized_uri_as_base64_str: str):
    if micro_serialized_uri_as_base64_str == "<empty>":
        micro_serialized_uri_as_base64_str = ""

    micro_serialized_uri: bytes = base64_str_to_bytes(micro_serialized_uri_as_base64_str)
    context.logger.info(f"Json request for {command} -> {micro_serialized_uri}")

    micro_serialized_uri_as_str = micro_serialized_uri.decode("iso-8859-1")
    response_json: Dict[str, Any] = context.tm.request(context.ue, command, micro_serialized_uri_as_str)

    context.logger.info(f"Response Json {command} -> {response_json}")
    context.response_data = response_json["data"]


def access_nested_dict(dictionary, keys):
    if keys == "":
        return dictionary

    keys = keys.split(".")
    value = dictionary
    if isinstance(value, str):
        value = json.loads(value)
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


@then("receives json with following set fields")
def generic_expected_and_actual_json_comparison(context):
    for row in context.table:
        field_name: str = row["protobuf_field_names"]
        expected_value: str = row["protobuf_field_values"]
        expected_value = cast(expected_value, row["protobuf_field_type"], jsonable=False)

        # get the field_name's value from incoming context.response_data
        actual_value = access_nested_dict(context.response_data, field_name)
        if row["protobuf_field_type"] == "bytes":
            actual_value = actual_value.encode()

        context.logger.info(f"field_name ({field_name})  actual: {actual_value} | expect: {expected_value}")
        assert_that(actual_value, equal_to(expected_value))
