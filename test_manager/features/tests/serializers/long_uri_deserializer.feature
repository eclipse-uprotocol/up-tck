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
Feature: Local and Remote URI de-serialization

  Scenario Outline: Testing the local uri deserializer
    Given "<uE1>" creates data for "uri_deserialize"
    When sends a "uri_deserialize" request with serialized input "<serialized_uri>"
    # And user waits "1" second
    Then the deserialized uri received should have the following properties:
      | Field                | Value                  |
      | entity.name          | <entity_name>          |
      | entity.version_major | <entity_version_major> |
      | resource.name        | <resource_name>        |
      | resource.instance    | <resource_instance>    |
      | resource.message     | <resource_message>     |
    Examples:
      | uE1    | entity_name | resource_name | resource_instance | resource_message | entity_version_major | serialized_uri            |
      | python | neelam      | rpc           | test              |                  | 0                    | /neelam//rpc.test         |
      | python | neelam      |               |                   |                  | 0                    | /neelam                   |
      | python | neelam      |               |                   |                  | 1                    | /neelam/1                 |
      | python | neelam      | test          |                   |                  | 0                    | /neelam//test             |
      | python | neelam      | test          |                   |                  | 1                    | /neelam/1/test            |
      | python | neelam      | test          | front             |                  | 0                    | /neelam//test.front       |
      | python | neelam      | test          | front             |                  | 1                    | /neelam/1/test.front      |
      | python | neelam      | test          | front             | Test             | 0                    | /neelam//test.front#Test  |
      | python | neelam      | test          | front             | Test             | 1                    | /neelam/1/test.front#Test |
      | java   | neelam      | rpc           | test              |                  | 0                    | /neelam//rpc.test         |
      | java   | neelam      |               |                   |                  | 0                    | /neelam                   |
      | java   | neelam      |               |                   |                  | 1                    | /neelam/1                 |
      | java   | neelam      | test          |                   |                  | 0                    | /neelam//test             |
      | java   | neelam      | test          |                   |                  | 1                    | /neelam/1/test            |
      | java   | neelam      | test          | front             |                  | 0                    | /neelam//test.front       |
      | java   | neelam      | test          | front             |                  | 1                    | /neelam/1/test.front      |
      | java   | neelam      | test          | front             | Test             | 0                    | /neelam//test.front#Test  |
      | java   | neelam      | test          | front             | Test             | 1                    | /neelam/1/test.front#Test |


  Scenario Outline: Testing the remote uri deserializer
    Given "<uE1>" creates data for "uri_deserialize"
    When sends a "uri_deserialize" request with serialized input "<serialized_uri>"
    Then the deserialized uri received should have the following properties:
      | Field                | Value                  |
      | authority.name       | <authority_name>       |

      | entity.name          | <entity_name>          |
      | entity.version_major | <entity_version_major> |
      | resource.name        | <resource_name>        |
      | resource.instance    | <resource_instance>    |
      | resource.message     | <resource_message>     |
    Examples:
      | uE1    | authority_name | entity_name | resource_name | resource_instance | resource_message | entity_version_major | serialized_uri                              |
      | python | vcu.my_car_vin | neelam      |               |                   |                  | 0                    | //vcu.my_car_vin/neelam                   |
      | python | vcu.my_car_vin | neelam      |               |                   |                  | 1                    | //vcu.my_car_vin/neelam/1                 |
      | python | vcu.my_car_vin | neelam      | test          |                   |                  | 1                    | //vcu.my_car_vin/neelam/1/test            |
      | python | vcu.my_car_vin | neelam      | test          |                   |                  | 0                    | //vcu.my_car_vin/neelam//test             |
      | python | vcu.my_car_vin | neelam      | test          | front             |                  | 1                    | //vcu.my_car_vin/neelam/1/test.front      |
      | python | vcu.my_car_vin | neelam      | test          | front             |                  | 0                    | //vcu.my_car_vin/neelam//test.front       |
      | python | vcu.my_car_vin | neelam      | test          | front             | Test             | 1                    | //vcu.my_car_vin/neelam/1/test.front#Test |
      | python | vcu.my_car_vin | neelam      | test          | front             | Test             | 0                    | //vcu.my_car_vin/neelam//test.front#Test  |
      | python | vcu.my_car_vin | petapp      | rpc           | response          |                  | 0                    | //vcu.my_car_vin/petapp//rpc.response     |
      | java   | vcu.my_car_vin | neelam      |               |                   |                  | 0                    | //vcu.my_car_vin/neelam                   |
      | java   | vcu.my_car_vin | neelam      |               |                   |                  | 1                    | //vcu.my_car_vin/neelam/1                 |
      | java   | vcu.my_car_vin | neelam      | test          |                   |                  | 1                    | //vcu.my_car_vin/neelam/1/test            |
      | java   | vcu.my_car_vin | neelam      | test          |                   |                  | 0                    | //vcu.my_car_vin/neelam//test             |
      | java   | vcu.my_car_vin | neelam      | test          | front             |                  | 1                    | //vcu.my_car_vin/neelam/1/test.front      |
      | java   | vcu.my_car_vin | neelam      | test          | front             |                  | 0                    | //vcu.my_car_vin/neelam//test.front       |
      | java   | vcu.my_car_vin | neelam      | test          | front             | Test             | 1                    | //vcu.my_car_vin/neelam/1/test.front#Test |
      | java   | vcu.my_car_vin | neelam      | test          | front             | Test             | 0                    | //vcu.my_car_vin/neelam//test.front#Test  |
      | java   | vcu.my_car_vin | petapp      | rpc           | response          |                  | 0                    | //vcu.my_car_vin/petapp//rpc.response     |
