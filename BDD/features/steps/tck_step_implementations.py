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

from behave import when, then, given
from hamcrest import assert_that, equal_to
import sys
import git

from up_tck.python_utils.protobuf_setter_utils import set_umessage_fields, set_uuri_fields
from up_tck.python_utils.variable_type_converter import type_converter
from up_tck.python_utils.constants import SEND_COMMAND, REGISTER_LISTENER_COMMAND, \
    UNREGISTER_LISTENER_COMMAND, INVOKE_METHOD_COMMAND
from up_tck.test_manager.testmanager import SocketTestManager

from google.protobuf.any_pb2 import Any
from uprotocol.proto.upayload_pb2 import UPayload
from uprotocol.proto.uri_pb2 import UResource
from uprotocol.proto.ustatus_pb2 import UStatus
from uprotocol.proto.ustatus_pb2 import UCode
from uprotocol.proto.uri_pb2 import UEntity
from uprotocol.proto.uri_pb2 import UUri
from uprotocol.proto.uattributes_pb2 import UAttributes, UPriority
from uprotocol.proto.umessage_pb2 import UMessage
from uprotocol.transport.builder.uattributesbuilder import UAttributesBuilder


repo = git.Repo('.', search_parent_directories=True)
sys.path.append(repo.working_tree_dir)


@given('Test Agent "{sdk_name}" begins "{command}" test')
def begin_test(context, sdk_name: str, command: str):
    context.logger.info(f"sdk_name: {sdk_name}; command: {command}")


@given('sets "{uattr}" creates publish message with parameter source equal to created protobuf "{value}"')
def initialize_attribute_protobuf(context, uattr: str, value: str):
    value: Any = context.initialized_data[value]

    new_builder: UAttributesBuilder = UAttributesBuilder.publish(value, UPriority.UPRIORITY_CS1)
    context.initialized_data[uattr] = new_builder
    context.initialized_data["attributes"] = new_builder


@given('sets "{field}" field "{param}" equal to "{type}" "{value}"')
def initialize_generic_protobuf(context, field: str, param: str, type: str, value: str):

    proto_matchers = {
        "upayload": UPayload(),
        "uattributes": UAttributes(),
        "umessage": UMessage(),
        "uuri": UUri(),
        "uresource": UResource(),
        "uentity": UEntity()
    }

    if field not in context.initialized_data:
        context.initialized_data[field] = proto_matchers[field]

    if field == "upayload":
        context.initialized_data["payload"] = context.initialized_data[field]
    if type == "protobuf" and field == "uuri":
        context.initialized_data["source"] = context.initialized_data[field]
        set_uuri_fields(context.initialized_data[field], param, context.initialized_data[value])
    else:
        setattr(context.initialized_data[field], param, type_converter(type, value))


@when('Test Agent "{sdk_name}" executes "{command}" on given UUri')
def tm_sends_request(context, command: str, sdk_name: str):
    command = command.lower().strip()
    umsg: UMessage = UMessage()

    if command in [REGISTER_LISTENER_COMMAND, UNREGISTER_LISTENER_COMMAND]:
        uuri: UUri = context.initialized_data["source"]

        attributes: UAttributes = UAttributesBuilder.publish(uuri, UPriority.UPRIORITY_CS1).build()

        set_umessage_fields(umsg, "attributes", attributes)

    elif command in [SEND_COMMAND, INVOKE_METHOD_COMMAND]:
        uuri: UUri = context.initialized_data["source"]

        uattr_builder: UAttributesBuilder = context.initialized_data["attributes"]
        attributes: UAttributes = uattr_builder.build()

        upayload: UPayload = context.initialized_data["payload"]

        set_umessage_fields(umsg, "attributes", attributes)
        set_umessage_fields(umsg, "payload", upayload)

    # Wait until TA is connected
    while not context.tm.has_sdk_connection(sdk_name):
        continue

    test_manager: SocketTestManager = context.tm
    context.logger.info(f"sdk_name: {sdk_name}; command: {command}")

    status: UStatus = test_manager.request(sdk_name, command, umsg)
    context.sdk_to_status[sdk_name] = status

    context.logger.info("context.sdk_to_status:")
    context.logger.info(context.sdk_to_status[sdk_name])


@then('Test Agent "{sdk_name}" receives an "{status_code}" status for latest execute')
def tm_receives_response(context, status_code: str, sdk_name: str):
    response_status: UStatus = context.sdk_to_status[sdk_name]
    if response_status is None:
        raise ValueError("Request did not receive a response UStatus")

    status_code = status_code.lower().strip()
    if status_code == "ok":
        assert_that(response_status.code, equal_to(UCode.OK))

    # Reset status variable
    context.sdk_to_status[sdk_name] = None


@then('Test Agent "{sdk_name}" builds OnReceive UMessage with parameter UPayload "{param}" with parameter "{inner_param}" as "{expected}"')
def tm_receives_onreceive(context, sdk_name: str, param: str, inner_param: str, expected: str):
    test_manager: SocketTestManager = context.tm

    umsg: UMessage = test_manager.get_onreceive(sdk_name)

    upay: UPayload = getattr(umsg, param)

    actual = getattr(upay, inner_param)

    assert_that(actual.decode('utf-8'), equal_to(expected))
