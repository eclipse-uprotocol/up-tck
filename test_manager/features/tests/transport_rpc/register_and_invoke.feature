# -------------------------------------------------------------------------
#
# SPDX-FileCopyrightText: Copyright (c) 2024 Contributors to 
# the Eclipse Foundation
#
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http: *www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# SPDX-FileType: SOURCE
# SPDX-License-Identifier: Apache-2.0
#
# -------------------------------------------------------------------------

Feature: Testing RPC Functionality

  Scenario Outline: To test the registerlistener and invoke_method apis
    Given "uE1" creates data for "registerlistener"
    And sets "ue_id" to "12345"
    And sets "ue_version_major" to "1"
    And sets "resource_id" to "32769"

    When sends "registerlistener" request
    Then the status received with "code" is "OK"

    Given "uE2" creates data for "invokemethod"
    And sets "ue_id" to "12345"
    And sets "ue_version_major" to "1"
    And sets "resource_id" to "32769"
    And sets "payload" to b".type.googleapis.com/google.protobuf.Int32Value\x12\x02\x08\x03"

    When sends "invokemethod" request
    Then "uE2" receives data field "payload" as b"\n/type.googleapis.com/google.protobuf.StringValue\x12\x14\n\x12SuccessRPCResponse"

    Given "uE1" creates data for "unregisterlistener"
    And sets "ue_id" to "12345"
    And sets "ue_version_major" to "1"
    And sets "resource_id" to "32769"

    When sends "unregisterlistener" request
    Then the status received with "code" is "OK"

    Examples:
      | ignore | ignore |
      | ignore | ignore |
