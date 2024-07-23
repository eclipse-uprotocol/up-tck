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

Feature: Testing Publish and Subscribe Functionality

  Scenario Outline: To test the rpc server and client apis
    Given "uE1" creates data for "rpcserver"
    And sets "attributes.sink.authority_name" to "me_authority"
    And sets "attributes.sink.ue_id" to "65538"
    And sets "attributes.sink.ue_version_major" to "1"
    And sets "attributes.sink.resource_id" to "32600"
    And sets "attributes.payload_format" to "UPAYLOAD_FORMAT_PROTOBUF_WRAPPED_IN_ANY"
    And sets "payload" to b".type.googleapis.com/google.protobuf.Int32Value\x12\x02\x08\x03"
    
    And sends "rpcserver" request
    Then the status received with "code" is "OK"

    When "uE2" creates data for "invokemethod"
    And sets "attributes.sink.authority_name" to "me_authority"
    And sets "attributes.sink.ue_id" to "65538"
    And sets "attributes.sink.ue_version_major" to "1"
    And sets "attributes.sink.resource_id" to "32600"
    And sets "attributes.payload_format" to "UPAYLOAD_FORMAT_PROTOBUF_WRAPPED_IN_ANY"
    And sets "payload" to b".type.googleapis.com/google.protobuf.Int32Value\x12\x02\x08\x03"
    And sends "invokemethod" request

    Then the status received with "code" is "OK"
      And "uE1" receives data field "payload" as b"type.googleapis.com/google.protobuf.Int32Value\x12\x02\x08\x03"

    Examples:
      | ignore | ignore |
      | ignore | ignore |