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
def step_impl(context, sdk_name: str, command: str):
    context.logger.info("Inside create register listener data")
    context.json_dict = {}
    context.status_json = None
    if command == "send":
        context.on_receive_msg.pop(sdk_name, None)
    if command == "invokemethod":
        context.on_receive_rpc_response.pop(sdk_name, None)

    while not context.tm.has_sdk_connection(sdk_name):
        continue

    context.ue = sdk_name
    context.action = command


@given(u'sets "{key}" to "{value}"')
@when(u'sets "{key}" to "{value}"')
def step_impl(context: Context, key: str, value: str):
    if key not in context.json_dict:
        context.json_dict[key] = value


@given(u'sets "{key}" to b"{value}"')
@when(u'sets "{key}" to b"{value}"')
def step_impl(context, key, value):
    if key not in context.json_dict:
        context.json_dict[key] = "BYTES:" + value


@given(u'sends "{command}" request')
@when(u'sends "{command}" request')
def step_impl(context, command: str):
    context.json_dict = unflatten_dict(context.json_dict)
    context.logger.info(f"Json request for {command} -> {str(context.json_dict)}")
    context.tm.receive_from_bdd(context.ue, context.action, context.json_dict)


@when(u'user waits "{sec}" second')
@then(u'user waits "{sec}" second')
def step_impl(context, sec):
    time.sleep(int(sec))


@then(u'the status received with "{field}" is "{field_value}"')
def step_impl(context, field, field_value):
    try:
        rec_field_value = context.status_json[field]
        assert_that(field_value, equal_to(rec_field_value))
    except AssertionError as ae:
        raise AssertionError(f"Assertion error. Expected is {field_value} but "
                             f"received {context.status_json[field]}")
    except Exception as ae:
        raise ValueError(f"Expection occured. {ae}")


@then(u'"{sdk_name}" receives "{key}" as b"{value}"')
def step_impl(context, sdk_name, key, value):
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
def step_impl(context, sdk_name, key, value):
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
