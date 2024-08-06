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

Feature: UAttributes Validation

  Scenario Outline: Validate different types of UAttributes
    Given "uE1" creates data for "uattributes_validate"
      And sets "validation_method" to "<val_method>"
      And sets "validation_type" to "<val_type>"
      And sets "attributes.source.authority_name" to "<source_authority_name>"
      And sets "attributes.source.ue_id" to "<source_ue_id>"
      And sets "attributes.source.ue_version_major" to "<source_version_major>"
      And sets "attributes.source.resource_id" to "<source_resource_id>"
      And sets "attributes.sink.authority_name" to "<sink_authority_name>"
      And sets "attributes.sink.ue_id" to "<sink_ue_id>"
      And sets "attributes.sink.ue_version_major" to "<sink_version_major>"
      And sets "attributes.sink.resource_id" to "<sink_resource_id>"
      And sets "attributes.priority" to "<priority>"
      And sets "attributes.type" to "<message_type>"
      And sets "id" to "<id_type>"
      And sets "attributes.ttl" to "<ttl>"
      And sets "attributes.permission_level" to "<permission_level>"
      And sets "attributes.comm_status" to "<comm_status>"
      And sets "reqid" to "<reqid_type>"

    When sends "uattributes_validate" request
      Then receives validation result as "<expected_status>"

    Examples:
      | val_type                     | val_method               | source_authority_name  | source_ue_id      | source_version_major | source_resource_id   | sink_authority_name               | sink_ue_id                | sink_version_major | sink_resource_id | priority              | message_type               | id_type   | token | ttl  | permission_level | comm_status | reqid_type | expected_status |
      | get_validator                |                          | vcu.someVin.veh.com    | 42000             | 1                    | 1                    |                                   |                           |                    |                  | UPRIORITY_CS0         | UMESSAGE_TYPE_PUBLISH      |           |       |      |                  |             |            |                 |
      | get_validator                |                          | vcu.someVin.veh.com    | 42000             | 1                    | 1                    |                                   |                           |                    |                  | UPRIORITY_CS4         | UMESSAGE_TYPE_REQUEST      |           |       | 1000 |                  |             |            |                 |
      | get_validator                |                          | vcu.someVin.veh.com    | 42000             | 1                    | 1                    |                                   |                           |                    |                  | UPRIORITY_CS4         | UMESSAGE_TYPE_RESPONSE     |           |       |      |                  |             |            |                 |
      | get_validator                |                          | vcu.someVin.veh.com    | 42000             | 1                    | 1                    |                                   |                           |                    |                  | UPRIORITY_CS4         | UMESSAGE_TYPE_NOTIFICATION |           |       |      |                  |             |            |                 |
      | get_validator                |                          |                        |                   |                      |                      |                                   |                           |                    |                  |                       |                            |           |       |      |                  |             |            |                 |
      |                              | publish_validator        | vcu.someVin.veh.com    | 42000             | 1                    | 1                    |                                   |                           |                    |                  | UPRIORITY_CS1         | UMESSAGE_TYPE_PUBLISH      | uprotocol |       |      |                  |             |            | True            |
      |                              | publish_validator        | vcu.someVin.veh.com    | 42000             | 1                    | 1                    |                                   |                           |                    |                  | UPRIORITY_CS1         | UMESSAGE_TYPE_PUBLISH      | uprotocol |       | 1000 | 2                | 3           |            | True            |
      |                              | publish_validator        | vcu.someVin.veh.com    | 42000             | 1                    | 1                    | vcu.someVin.veh.com               | 1234                      | 1                  | 0                | UPRIORITY_CS1         | UMESSAGE_TYPE_RESPONSE     | uprotocol |       |      |                  |             | uprotocol  | False           |
      |                              | publish_validator        | vcu.someVin.veh.com    | 42000             | 1                    | 1                    | default                           |                           |                    |                  | UPRIORITY_CS1         | UMESSAGE_TYPE_PUBLISH      | uprotocol |       |      |                  |             |            | False           |
      |                              | request_validator        | vcu.someVin.veh.com    | 42000             | 1                    | 1                    | vcu.someVin.veh.com               | 1234                      | 1                  | 1234             | UPRIORITY_CS4         | UMESSAGE_TYPE_REQUEST      | uprotocol |       | 1000 |                  |             |            | True            |
      |                              | request_validator        | vcu.someVin.veh.com    | 42000             | 1                    | 1                    | vcu.someVin.veh.com               | 1234                      | 1                  | 1234             | UPRIORITY_CS4         | UMESSAGE_TYPE_REQUEST      | uprotocol |       | 1000 | 2                | 3           |            | True            |
      |                              | request_validator        | vcu.someVin.veh.com    | 42000             | 1                    | 1                    | vcu.someVin.veh.com               | 1234                      | 1                  | 0                | UPRIORITY_CS4         | UMESSAGE_TYPE_RESPONSE     | uprotocol |       | 1000 |                  |             | uprotocol  | False           |
      |                              | request_validator        | vcu.someVin.veh.com    | 42000             | 1                    | 1                    | default                           |                           |                    |                  | UPRIORITY_CS4         | UMESSAGE_TYPE_REQUEST      | uprotocol |       | 1000 |                  |             |            | False           |
      |                              | response_validator       | vcu.someVin.veh.com    | 42000             | 1                    | 1                    | vcu.someVin.veh.com               | 1234                      | 1                  | 0                | UPRIORITY_CS4         | UMESSAGE_TYPE_RESPONSE     | uprotocol |       |      |                  |             | uprotocol  | True            |
      |                              | response_validator       | vcu.someVin.veh.com    | 42000             | 1                    | 1                    | vcu.someVin.veh.com               | 1234                      | 1                  | 0                | UPRIORITY_CS4         | UMESSAGE_TYPE_RESPONSE     | uprotocol |       |      | 2                | 3           | uprotocol  | True            |
      |                              | response_validator       | vcu.someVin.veh.com    | 42000             | 1                    | 1                    | vcu.someVin.veh.com               | 1234                      | 1                  | 0                | UPRIORITY_CS4         | UMESSAGE_TYPE_NOTIFICATION | uprotocol |       |      |                  |             |            | False           |
      |                              | response_validator       | vcu.someVin.veh.com    | 42000             | 1                    | 1                    | default                           |                           |                    |                  | UPRIORITY_CS4         | UMESSAGE_TYPE_RESPONSE     | uprotocol |       |      |                  |             |            | False           |
      |                              | response_validator       | vcu.someVin.veh.com    | 42000             | 1                    | 1                    | vcu.someVin.veh.com               | 1234                      | 1                  | 0                | UPRIORITY_CS4         | UMESSAGE_TYPE_RESPONSE     | uprotocol |       |      |                  |             |            | False           |
      | is_expired                   | publish_validator        | vcu.someVin.veh.com    | 42000             | 1                    | 1                    | vcu.someVin.veh.com               | 1234                      |                    |                  | UPRIORITY_CS0         | UMESSAGE_TYPE_PUBLISH      | uprotocol |       |      |                  |             |            | False           |
      | is_expired                   | publish_validator        | vcu.someVin.veh.com    | 42000             | 1                    | 1                    | vcu.someVin.veh.com               | 1234                      |                    |                  | UPRIORITY_CS0         | UMESSAGE_TYPE_PUBLISH      | uprotocol |       | 0    |                  |             |            | False           |
      | is_expired                   | publish_validator        | vcu.someVin.veh.com    | 42000             | 1                    | 1                    | vcu.someVin.veh.com               | 1234                      |                    |                  | UPRIORITY_CS0         | UMESSAGE_TYPE_PUBLISH      | uprotocol |       | 10000|                  |             |            | False           |
      | is_expired                   | publish_validator        | vcu.someVin.veh.com    | 42000             | 1                    | 1                    | vcu.someVin.veh.com               | 1234                      |                    |                  | UPRIORITY_CS0         | UMESSAGE_TYPE_PUBLISH      | uprotocol |       | 1    |                  |             |            | True            |
      | validate_ttl                 | publish_validator        | vcu.someVin.veh.com    | 42000             | 1                    | 1                    |                                   |                           |                    |                  | UPRIORITY_CS0         | UMESSAGE_TYPE_PUBLISH      | uprotocol |       | 100  |                  |             |            | True            |
      | validate_sink                | publish_validator        | vcu.someVin.veh.com    | 42000             | 1                    | 1                    | default                           |                           |                    |                  | UPRIORITY_CS0         | UMESSAGE_TYPE_PUBLISH      | uprotocol |       |      |                  |             |            | False           |
      | validate_sink                | publish_validator        | vcu.someVin.veh.com    | 42000             | 1                    | 1                    |                                   |                           |                    |                  | UPRIORITY_CS0         | UMESSAGE_TYPE_PUBLISH      | uprotocol |       |      |                  |             |            | True            |
      | validate_req_id              | publish_validator        | vcu.someVin.veh.com    | 42000             | 1                    | 1                    |                                   |                           |                    |                  | UPRIORITY_CS0         | UMESSAGE_TYPE_PUBLISH      | uprotocol |       |      |                  |             |            | True            |
      | validate_type                | notification_validator   | vcu.someVin.veh.com    | 42000             | 1                    | 1                    | vcu.someVin.veh.com               | 1234                      | 1                  | 0                | UPRIORITY_CS0         | UMESSAGE_TYPE_NOTIFICATION | uprotocol |       |      |                  |             | uprotocol  | True            |
      | validate_sink                | notification_validator   | vcu.someVin.veh.com    | 42000             | 1                    | 1                    | vcu.someVin.veh.com               | 1234                      | 1                  | 0                | UPRIORITY_CS0         | UMESSAGE_TYPE_NOTIFICATION | uprotocol |       |      |                  |             | uprotocol  | True            |
      | validate_sink                | notification_validator   | vcu.someVin.veh.com    | 42000             | 1                    | 1                    | default                           |                           |                    |                  | UPRIORITY_CS0         | UMESSAGE_TYPE_NOTIFICATION | uprotocol |       |      |                  |             | uprotocol  | False           |
      | validate_permission_level    | publish_validator        | vcu.someVin.veh.com    | 42000             | 1                    | 1                    | default                           |                           |                    |                  | UPRIORITY_CS0         | UMESSAGE_TYPE_PUBLISH      | uprotocol |       |      | 3                |             | uprotocol  | True            |
      | validate_permission_level    | publish_validator        | vcu.someVin.veh.com    | 42000             | 1                    | 1                    | default                           |                           |                    |                  | UPRIORITY_CS0         | UMESSAGE_TYPE_PUBLISH      | uprotocol |       |      | 0                |             | uprotocol  | False           |
      |                              | request_validator        | vcu.someVin.veh.com    | 42000             | 1                    | 1                    |                                   |                           |                    |                  | UPRIORITY_CS4         | UMESSAGE_TYPE_PUBLISH      | uprotocol |       |      |                  |             |            | False           |
      |                              | publish_validator        | vcu.someVin.veh.com    | 42000             | 1                    | 1                    | vcu.someVin.veh.com               | 1234                      | 1                  | 0                | UPRIORITY_CS6         | UMESSAGE_TYPE_REQUEST      | uprotocol |       | 1000 | 2                | 3           | uprotocol  | False           |
      |                              | response_validator       | vcu.someVin.veh.com    | 42000             | 1                    | 1                    |                                   |                           |                    |                  | UPRIORITY_CS6         | UMESSAGE_TYPE_PUBLISH      | uprotocol |       | 1000 | 2                | 3           |            | False           |
      |                              | publish_validator        | vcu.someVin.veh.com    | 42000             | 1                    | 1                    |                                   |                           |                    |                  | UPRIORITY_CS6         | UMESSAGE_TYPE_PUBLISH      | uprotocol | null  |      |                  |             |            | True            |
      | validate_id                  | publish_validator        | vcu.someVin.veh.com    | 42000             | 1                    | 1                    |                                   |                           |                    |                  | UPRIORITY_CS6         | UMESSAGE_TYPE_PUBLISH      |           |       |      |                  |             |            | False           |
      | validate_id                  | notification_validator   | vcu.someVin.veh.com    | 42000             | 1                    | 1                    | vcu.someVin.veh.com               | 1234                      | 1                  | 0                | UPRIORITY_CS6         | UMESSAGE_TYPE_NOTIFICATION |           |       |      |                  |             |            | False           |
      | validate_id                  | request_validator        | vcu.someVin.veh.com    | 42000             | 1                    | 1                    | vcu.someVin.veh.com               | 1234                      | 1                  | 0                | UPRIORITY_CS6         | UMESSAGE_TYPE_REQUEST      |           |       | 1000 |                  |             |            | False           |
      | validate_id                  | response_validator       | vcu.someVin.veh.com    | 42000             | 1                    | 1                    | vcu.someVin.veh.com               | 1234                      | 1                  | 0                | UPRIORITY_CS6         | UMESSAGE_TYPE_RESPONSE     |           |       |      |                  |             | uprotocol  | False           |