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

Feature: Testing Notifiaction Sink and Source Functionality

  Scenario Outline: To test the notification sink and source apis
    Given "uE1" creates data for "notificationsink"
    And sets "authority_name" to "me_authority"
    And sets "ue_id" to "65538"
    And sets "ue_version_major" to "1"
    And sets "resource_id" to "32770"
    
    And sends "notificationsink" request
    Then the status received with "code" is "OK"

    When "uE2" creates data for "notificationsource"
    And sets "attributes.source.authority_name" to "me_authority"
    And sets "attributes.source.ue_id" to "65538"
    And sets "attributes.source.ue_version_major" to "1"
    And sets "attributes.source.resource_id" to "32770"
    And sets "attributes.sink" to entity URI of "uE1"
    And sets "attributes.payload_format" to "UPAYLOAD_FORMAT_PROTOBUF_WRAPPED_IN_ANY"
    And sets "payload" to b".type.googleapis.com/google.protobuf.Int32Value\x12\x02\x08\x03"
    And sends "notificationsource" request

    Then the status received with "code" is "OK"
      And "uE1" sends onreceive message with field "payload" as b"type.googleapis.com/google.protobuf.Int32Value\x12\x02\x08\x03"

    Examples:
      | ignore | ignore |
      | ignore | ignore |