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
import time
import sys
from behave import when, then, given, step
from behave.runner import Context
from hamcrest import assert_that, equal_to

from uprotocol.proto.upayload_pb2 import UPayload

sys.path.append("../")

from python.test_manager.testmanager import SocketTestManager

@given(u'“{sdk_name}” creates data for "{command}"')
@when(u'“{sdk_name}” creates data for "{command}"')
def step_impl(context, sdk_name: str, command: str):
    context.logger.info("Inside create register listener data")
    context.json_array = {}

    while not context.tm.has_sdk_connection(sdk_name):
        continue

    context.ue = sdk_name
    context.json_array['ue'] = [sdk_name]
    context.json_array['action'] = [command]


@given(u'sets "{key}" to "{value}"')
@when(u'sets "{key}" to "{value}"')
def step_impl(context: Context, key: str, value: str):
    context.logger.info("Json data: Key is " + str(key) + " value is " + str(value))
    if key not in context.json_array:
        context.json_array[key] = [value]


@given(u'sends "{command}" request')
@when(u'sends "{command}" request')
def step_impl(context, command: str):
    context.logger.info(f"Json request for {command} -> {str(context.json_array)}")
    context.status = context.tm.receive_action_request(context.json_array)
    context.logger.info(f"Status Received: {context.status}")


@step(u'the status for "{command}" request is "{status}"')
def step_impl(context, command, status):
    context.logger.info(f"Status for {command} is {context.status}")
    assert_that(context.status.message, equal_to(status))


@then(u'"{sdk_name}" receives "{key}" as "{value}"')
def step_impl(context, sdk_name, key, value):
    try:
        if context.tm.received_umessage not in ['', None]:
            received_payload: UPayload = context.tm.received_umessage.payload
            context.logger.info(f"Payload data for {sdk_name} is {received_payload}")
            assert_that(received_payload.value.decode('utf-8'), equal_to(value))
        else:
            raise ValueError(f"Received empty payload for {sdk_name}")

    except AssertionError as ae:
        raise AssertionError(f"Assertion error. Expected is {value} but "
                             f"received {received_payload.value.decode('utf-8')}",
                             exc_info=ae)
        
@given('"{sdk_name}" is connected to the Test Manager')
def tm_connects_to_ta_socket(context, sdk_name: str):
    test_manager: SocketTestManager = context.tm
    
    start_time: float = time.time()
    end_time: float = start_time
    wait_sec: float = 7.0
    
    while not test_manager.has_sdk_connection(sdk_name):
        time.sleep(1)
        end_time = time.time()
    if not test_manager.has_sdk_connection(sdk_name):
        context.logger.error(sdk_name + " Test Agent didn't connect in time")
        raise Exception(sdk_name + " Test Agent didn't connect in time")
    
    context.logger.info(f"{sdk_name} TA connects to TM {test_manager.sdk_to_test_agent_socket.keys()}")


@when('"{sdk_name}" closes its client socket connection')
def tm_closing_ta_socket(context, sdk_name: str):
    test_manager: SocketTestManager = context.tm
    # test_manager.close_ta(sdk_name)
    context.logger.info(f"TM closed TA connection {sdk_name} {test_manager.sdk_to_test_agent_socket.keys()}")
    pass
    
@then('Test Manager closes server socket connection to the "{sdk_name}"')
def step_impl(context, sdk_name: str):
    # context.logger.info("YOOOO SERVER cLOSED")
    pass