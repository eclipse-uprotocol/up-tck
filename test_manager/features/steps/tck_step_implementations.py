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
import git
import sys
import base64
import codecs
import time
from typing import Any, Dict
from uprotocol.proto.ustatus_pb2 import UCode

from behave import when, then, given
from behave.runner import Context
from hamcrest import assert_that, equal_to

@given(u'"{sdk_name}" creates data for "{command}"')
@when(u'"{sdk_name}" creates data for "{command}"')
def create_sdk_data(context, sdk_name: str, command: str):
    context.logger.info("Inside create register listener data")
    context.json_dict = {}
    context.status_json = None
    if command == "send":
        context.on_receive_msg.pop(sdk_name, None)
    elif command == "invokemethod":
        context.on_receive_rpc_response.pop(sdk_name, None)
    elif command == "uri_serialize":
        context.on_receive_serialized_uri = None
    elif command == "uri_deserialize":
        context.on_receive_deserialized_uri = None
    elif command == "uuid_serialize":
        context.on_receive_serialized_uuid = None
    elif command == "uuid_deserialize":
        context.on_receive_deserialized_uuid = None

    while not context.tm.has_sdk_connection(sdk_name):
        continue

    context.ue = sdk_name
    context.action = command


@then(u'receives uri serialization "{expected_uri}"')
def serialized_uri_received(context, expected_uri):
    try:
        rec_field_value = context.response_json
        assert_that(expected_uri, equal_to(rec_field_value))
    except AssertionError as ae:
        raise AssertionError(f"Assertion error. Expected is {expected_uri} but "
                             f"received {context.on_receive_serialized_uri}")
    except Exception as ae:
        raise ValueError(f"Expection occured. {ae}")


@then(u'receives uuid serialization "{expected_uuid}"')
def serialized_uuid_received(context, expected_uuid: str):
    try:
        rec_field_value = context.response_json
        # context.logger.info(f"uuid serialization -> {rec_field_value}")

        assert_that(expected_uuid, equal_to(rec_field_value))
    except AssertionError as ae:
        raise AssertionError(f"Assertion error. Expected is {expected_uuid} but "
                             f"received {context.on_receive_serialized_uuid}")
    except Exception as ae:
        raise ValueError(f"Expection occured. {ae}")


@when(u'sends a "{command}" request with serialized input "{serialized}"')
def send_serialized_command(context, command, serialized):
    context.logger.info(f"Json request for {command} -> {serialized}")
    response_json: Dict[str, Any] = context.tm.request(context.ue, context.action, serialized)
    context.logger.info(f"Response Json {command} -> {response_json}")
    context.response_json = response_json['data']

@then(u'the deserialized uri received should have the following properties')
def verify_uri_received_properties(context):
    deserialized_uri: Dict[str, Any] = flatten_dict(context.response_json)
    context.logger.info(f"deserialized_uri_dict -> {deserialized_uri}")
    
    # Iterate over the rows of the table and verify the received properties    
    int_type_fields = set(["entity.id", "entity.version_major", "entity.version_minor", 'resource.id'])
    try:
        for row in context.table:
            field = row['Field']
            expected_value = row['Value']
            context.logger.info(f"field {field}; {deserialized_uri[field]} vs. {expected_value}")
            if len(expected_value) > 0:

                if field in int_type_fields:
                    expected_value = int(expected_value)
                assert_that(deserialized_uri[field], equal_to(expected_value))
            else:
                assert_that(len(deserialized_uri[field]) > 0, equal_to(len(expected_value) > 0))

    except AssertionError as ae:
        raise AssertionError(f"Assertion error. {ae}")


@then(u'the deserialized uuid received should have the following properties')
def verify_uuid_received_properties(context):
    # assert context.on_receive_deserialized_uuid is not None
    # deserialized_uuid_dict = flatten_dict(context.on_receive_deserialized_uuid)
    context.logger.info(f"deserialized context.response_json -> {context.response_json}")

    deserialized_uuid: Dict[str, int]= flatten_dict(context.response_json)
    context.logger.info(f"deserialized_uuid_dict -> {deserialized_uuid}")
    
    ### !!!! PROBLEM: data types returned and given are STRINGS and some returns are ints/strings !!!!
    ### SO set expected data types to BE those data types!!!!

    # Iterate over the rows of the table and verify the received properties
    int_type_fields = set(["msb", "lsb"])
    try:
        for row in context.table:
            field = row['Field']
            expected_value = row['Value']
            assert_that(field in deserialized_uuid, equal_to(len(expected_value) > 0))
            
            if len(expected_value) > 0:
                if field in int_type_fields:
                    expected_value: int = int(expected_value)
                assert_that(deserialized_uuid[field], equal_to(expected_value))
    except AssertionError as ae:
        raise AssertionError(f"Assertion error. {ae}")


@given(u'sets "{key}" to "{value}"')
@when(u'sets "{key}" to "{value}"')
def set_key_to_val(context: Context, key: str, value: str):
    if key not in context.json_dict:
        context.json_dict[key] = value
    # context.logger.info(f"Dict -> {context.json_dict}")

@given(u'sets "{key}" to ""')
def set_blank_key(context, key):
    pass


@given(u'sets "{key}" to b"{value}"')
@when(u'sets "{key}" to b"{value}"')
def set_key_to_bytes(context, key, value):
    if key not in context.json_dict:
        context.json_dict[key] = "BYTES:" + value


@given(u'sends "{command}" request')
@when(u'sends "{command}" request')
def send_command_request(context, command: str):
    context.json_dict = unflatten_dict(context.json_dict)
    context.logger.info(f"Json request for {command} -> {str(context.json_dict)}")
    # context.tm.receive_from_bdd(context.ue, context.action, context.json_dict)
    response_json: Dict[str, Any] = context.tm.request(context.ue, context.action, context.json_dict)
    context.logger.info(f"Response Json {command} -> {response_json}")
    context.response_json = response_json['data']


@when(u'user waits "{sec}" second')
@then(u'user waits "{sec}" second')
def user_wait(context, sec):
    time.sleep(int(sec))


@then(u'the status received with "{field}" is "{field_value}"')
def receive_status(context, field, field_value: str):
    try:
        rec_field_value: str = context.response_json[field]
        field_value: int = getattr(UCode, field_value)
        assert_that(field_value, equal_to(rec_field_value))
    except AssertionError as ae:
        raise AssertionError(f"Assertion error. Expected is {field_value} but "
                             f"received {context.response_json[field]}")
    except Exception as ae:
        raise ValueError(f"Expection occured. {ae}")


@then(u'"{sdk_name}" receives onreceive message "{key}" as b"{value}"')
def receive_value_as_bytes(context, sdk_name, key, value):
    try:
        value = value.strip()
        
        on_receive_msg: Dict[str, Any] = context.tm.get_onreceive(sdk_name)
        context.logger.info(f"context.on_receive_msg:  {on_receive_msg}")
        val = access_nested_dict(on_receive_msg["data"], key)
        context.logger.info(f"val {key}:  {val}")

        # rec_field_value = base64.b64decode(val.encode('utf-8'))
        rec_field_value = val.encode('utf-8')
        assert rec_field_value.split(b'googleapis.com/')[1] == value.encode('utf-8').split(b'googleapis.com/')[1]
    except KeyError as ke:
        raise KeyError(f"Key error. {sdk_name} has not received topic update.")
    except AssertionError as ae:
        raise AssertionError(f"Assertion error. Expected is {value.encode('utf-8')} but "
                             f"received {rec_field_value}")
    except Exception as ae:
        raise ValueError(f"Expection occured. {ae}")


@then(u'"{sdk_name}" receives "{action_type}" having "{key}" as b"{expected_value}"')
def receive_rpc_response_as_bytes(context, sdk_name, action_type: str, key, expected_value):
    try:
        actual_value: str = access_nested_dict(context.response_json, key)
        # actual_value: bytes = base64.b64decode(actual_value.encode('utf-8'))
        actual_value: bytes = actual_value.encode('utf-8')
        
        # Convert bytes to byte string with escape sequences
        actual_value = codecs.encode(actual_value.decode('utf-8'), 'unicode_escape')
        assert actual_value.split(b'googleapis.com/')[1] == expected_value.encode('utf-8').split(b'googleapis.com/')[1]
    except KeyError as ke:
        raise KeyError(f"Key error. {sdk_name} has not received rpc response.")
    except AssertionError as ae:
        raise AssertionError(f"Assertion error. Expected is {expected_value.encode('utf-8')} but "
                             f"received {repr(actual_value)}")
    except Exception as ae:
        raise ValueError(f"Expection occured. {ae}")


def access_nested_dict(dictionary, keys):
    keys = keys.split('.')
    value = dictionary
    for key in keys:
        value = value[key]
    return value


def flatten_dict(nested_dict, parent_key='', sep='.'):
    flattened = {}
    for k, v in nested_dict.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, dict):
            flattened.update(flatten_dict(v, new_key, sep=sep))
        else:
            flattened[new_key] = v
    return flattened


def unflatten_dict(d, delimiter='.'):
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
