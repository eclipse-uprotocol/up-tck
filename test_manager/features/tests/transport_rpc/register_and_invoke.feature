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

Feature: Testing RPC Functionality

  Scenario Outline: To test the registerlistener and invoke_method apis
    Given "<uE1>" creates data for "registerlistener"
    And sets "entity.name" to "body.access"
    And sets "resource.name" to "door"
    And sets "resource.instance" to "front_left"
    And sets "resource.message" to "Door"
    When sends "registerlistener" request
    And user waits "2" second
    Then the status received with "code" is "OK"
#
    Given "<uE2>" creates data for "invokemethod"
    And sets "entity.name" to "body.access"
    And sets "resource.name" to "door"
    And sets "resource.instance" to "front_left"
    And sets "resource.message" to "Door"

    And sets "payload.format" to "UPAYLOAD_FORMAT_PROTOBUF_WRAPPED_IN_ANY"
    And sets "payload.value" to b".type.googleapis.com/google.protobuf.Int32Value\x12\x02\x08\x03"

    When sends "invokemethod" request
    And user waits "8" second

    Then "<uE2>" receives rpc response having "payload.value" as b"\n/type.googleapis.com/google.protobuf.StringValue\x12\x14\n\x12SuccessRPCResponse"

    Given "<uE1>" creates data for "unregisterlistener"
    And sets "entity.name" to "body.access"
    And sets "resource.name" to "door"
    And sets "resource.instance" to "front_left"
    And sets "resource.message" to "Door"
    When sends "unregisterlistener" request
    And user waits "2" second
    Then the status received with "code" is "OK"

    Examples:
      | uE1    | uE2    |
      | java   | java   |
      | python | python |
      | java   | python |
      | python | java   |
