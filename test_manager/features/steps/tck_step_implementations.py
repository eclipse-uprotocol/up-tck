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
import time

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
    elif command == "uri_serialize":
        context.on_receive_deserialized_uri = None
    elif command == "performancesubscriber":
        context.sub_msgs = []
        context.pub_msgs = []

    while not context.tm.has_sdk_connection(sdk_name):
        continue

    context.ue = sdk_name
    context.action = command


@then(u'the serialized uri received is "{expected_uri}"')
def serialized_received(context, expected_uri):
    try:
        rec_field_value = context.on_receive_serialized_uri
        assert_that(expected_uri, equal_to(rec_field_value))
    except AssertionError as ae:
        raise AssertionError(f"Assertion error. Expected is {expected_uri} but "
                             f"received {context.on_receive_serialized_uri}")
    except Exception as ae:
        raise ValueError(f"Expection occured. {ae}")


@when(u'sends a "{command}" request with the value "{serialized_uri}"')
def send_serialized_command(context, command, serialized_uri):
    context.logger.info(f"Json request for {command} -> {serialized_uri}")
    context.tm.receive_from_bdd(context.ue, command, serialized_uri)


@then(u'the deserialized uri received should have the following properties')
def verify_received_properties(context):
    assert context.on_receive_deserialized_uri is not None
    deserialized_uri_dict = flatten_dict(context.on_receive_deserialized_uri)
    # Iterate over the rows of the table and verify the received properties
    try:
        for row in context.table:
            field = row['Field']
            expected_value = row['Value']
            if len(expected_value)>0:
                assert_that(deserialized_uri_dict[field], expected_value)
    except AssertionError as ae:
        raise AssertionError(f"Assertion error. {ae}")


@given(u'sets "{key}" to "{value}"')
@when(u'sets "{key}" to "{value}"')
def set_key_to_val(context: Context, key: str, value: str):
    if key not in context.json_dict:
        context.json_dict[key] = value


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
    context.tm.receive_from_bdd(context.ue, context.action, context.json_dict)


@when(u'user waits "{sec}" second')
@then(u'user waits "{sec}" second')
def user_wait(context, sec):
    time.sleep(int(sec))


@then(u'the status received with "{field}" is "{field_value}"')
def receive_status(context, field, field_value):
    try:
        rec_field_value = context.status_json[field]
        assert_that(field_value, equal_to(rec_field_value))
    except AssertionError as ae:
        raise AssertionError(f"Assertion error. Expected is {field_value} but "
                             f"received {context.status_json[field]}")
    except Exception as ae:
        raise ValueError(f"Expection occured. {ae}")


@then(u'"{sdk_name}" receives "{key}" as b"{value}"')
def receive_value_as_bytes(context, sdk_name, key, value):
    try:
        value = value.strip()
        val = access_nested_dict(context.on_receive_msg[sdk_name], key)
        rec_field_value = base64.b64decode(val.encode('utf-8'))
        assert rec_field_value.split(b'googleapis.com/')[1] == value.encode('utf-8').split(b'googleapis.com/')[1]
    except KeyError as ke:
        raise KeyError(f"Key error. {sdk_name} has not received topic update.")
    except AssertionError as ae:
        raise AssertionError(f"Assertion error. Expected is {value.encode('utf-8')} but "
                             f"received {rec_field_value}")
    except Exception as ae:
        raise ValueError(f"Expection occured. {ae}")


@then(u'"{sdk_name}" receives rpc response having "{key}" as b"{value}"')
def receive_rpc_response_as_bytes(context, sdk_name, key, value):
    try:
        val = access_nested_dict(context.on_receive_rpc_response[sdk_name], key)
        rec_field_value = base64.b64decode(val.encode('utf-8'))
        print(rec_field_value)
        # Convert bytes to byte string with escape sequences
        rec_field_value = codecs.encode(rec_field_value.decode('utf-8'), 'unicode_escape')
        assert rec_field_value.split(b'googleapis.com/')[1] == value.encode('utf-8').split(b'googleapis.com/')[1]
    except KeyError as ke:
        raise KeyError(f"Key error. {sdk_name} has not received rpc response.")
    except AssertionError as ae:
        raise AssertionError(f"Assertion error. Expected is {value.encode('utf-8')} but "
                             f"received {repr(rec_field_value)}")
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
