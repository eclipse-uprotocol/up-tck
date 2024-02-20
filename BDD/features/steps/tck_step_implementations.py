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

from behave import when, then, given, step
from behave.runner import Context
from hamcrest import assert_that, equal_to

from uprotocol.transport.ulistener import UListener
from uprotocol.proto.uattributes_pb2 import UAttributes
from uprotocol.proto.uri_pb2 import UUri
from uprotocol.proto.ustatus_pb2 import UStatus, UCode
from uprotocol.proto.upayload_pb2 import UPayload

received_payload = ''

class SocketUListener(UListener):
    def __init__(self, sdk_name: str = "python") -> None:
        pass

    def on_receive(self, topic: UUri, payload: UPayload, attributes: UAttributes) -> UStatus:
        """
        ULIstener is for each TA
        ADD SDK NAME in constructor or something

        Method called to handle/process events.<br><br>
        @param topic: Topic the underlying source of the message.
        @param payload: Payload of the message.
        @param attributes: Transportation attributes.
        @return Returns an Ack every time a message is received and processed.
        """
        print("Listener onreceived")

        print(f"{payload}")
        global received_payload
        received_payload = payload

        return UStatus(code=UCode.OK, message="all good")


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
    listener: UListener = SocketUListener()
    context.logger.info(f"Json request for {command} -> {str(context.json_array)}")
    context.status = context.tm.receive_action_request(context.json_array, listener)
    context.logger.info(f"Status Received: {context.status}")


@step(u'the status for "{command}" request is "{status}"')
def step_impl(context, command, status):
    context.logger.info(f"Status for {command} is {context.status}")
    assert_that(context.status.message, equal_to(status))


@then(u'"{sdk_name}" receives "{key}" as "{value}"')
def step_impl(context, sdk_name, key, value):
    global received_payload
    try:
        if received_payload not in ['', None]:
            context.logger.info(f"Payload data for {sdk_name} is {received_payload}")
            assert_that(received_payload.value.decode('utf-8'), equal_to(value))
        else:
            raise ValueError(f"Received empty payload for {sdk_name}")

    except AssertionError as ae:
        context.logger.error(f"Assertion error. Expected is {value} but "
                             f"received {received_payload.value.decode('utf-8')}",
                             exc_info=ae)
    except Exception as ex:
        context.logger.error(f"Exception Occurs: {ex}")
