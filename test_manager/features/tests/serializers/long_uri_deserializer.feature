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

Feature: Local and Remote URI de-serialization

  Scenario Outline: Testing the local uri deserializer
    Given "uE1" creates data for "uri_deserialize"
    When sends a "uri_deserialize" request with serialized input "<serialized_uri>"

    Then the deserialized uri received should have the following properties:
      | Field                | Value                  |
      | entity.name          | <entity_name>          |
      | entity.version_major | <entity_version_major> |
      | resource.name        | <resource_name>        |
      | resource.instance    | <resource_instance>    |
      | resource.message     | <resource_message>     |

    Examples:
      | entity_name | resource_name | resource_instance | resource_message | entity_version_major | serialized_uri            |
      | neelam      | rpc           | test              |                  | 0                    | /neelam//rpc.test         |
      | neelam      |               |                   |                  | 0                    | /neelam                   |
      | neelam      |               |                   |                  | 1                    | /neelam/1                 |
      | neelam      | test          |                   |                  | 0                    | /neelam//test             |
      | neelam      | test          |                   |                  | 1                    | /neelam/1/test            |
      | neelam      | test          | front             |                  | 0                    | /neelam//test.front       |
      | neelam      | test          | front             |                  | 1                    | /neelam/1/test.front      |
      | neelam      | test          | front             | Test             | 0                    | /neelam//test.front#Test  |
      | neelam      | test          | front             | Test             | 1                    | /neelam/1/test.front#Test |


  Scenario Outline: Testing the remote uri deserializer
    Given "uE1" creates data for "uri_deserialize"
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
      | authority_name | entity_name | resource_name | resource_instance | resource_message | entity_version_major | serialized_uri                            |
      | vcu.my_car_vin | neelam      |               |                   |                  | 0                    | //vcu.my_car_vin/neelam                   |
      | vcu.my_car_vin | neelam      |               |                   |                  | 1                    | //vcu.my_car_vin/neelam/1                 |
      | vcu.my_car_vin | neelam      | test          |                   |                  | 1                    | //vcu.my_car_vin/neelam/1/test            |
      | vcu.my_car_vin | neelam      | test          |                   |                  | 0                    | //vcu.my_car_vin/neelam//test             |
      | vcu.my_car_vin | neelam      | test          | front             |                  | 1                    | //vcu.my_car_vin/neelam/1/test.front      |
      | vcu.my_car_vin | neelam      | test          | front             |                  | 0                    | //vcu.my_car_vin/neelam//test.front       |
      | vcu.my_car_vin | neelam      | test          | front             | Test             | 1                    | //vcu.my_car_vin/neelam/1/test.front#Test |
      | vcu.my_car_vin | neelam      | test          | front             | Test             | 0                    | //vcu.my_car_vin/neelam//test.front#Test  |
      | vcu.my_car_vin | petapp      | rpc           | response          |                  | 0                    | //vcu.my_car_vin/petapp//rpc.response     |