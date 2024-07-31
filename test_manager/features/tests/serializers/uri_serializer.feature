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

Feature: Local and Remote URI serialization

  Scenario Outline: Testing the local uri serializer
    Given "uE1" creates data for "uri_serialize"
    And sets "ue_id" to "<ue_id>"
    And sets "ue_version_major" to "<version_major>"
    And sets "resource_id" to "<resource_id>"

    When sends "uri_serialize" request
    Then the serialized uri received is "<expected_uri>"

    Examples:
      | ue_id       | resource_id  | version_major        | expected_uri            |
      | 2345        | 1234         | 2                    | /929/2/4d2              |
      | 2345        |              |                      | /929/0/0                |
      | 2345        |              | 2                    | /929/2/0                |
      | 2345        |              | 1                    | /929/1/0                |
      | 2345        | 1234         | 1                    | /929/1/4d2              |

  Scenario Outline: Testing the remote uri serializer
    Given "uE1" creates data for "uri_serialize"
    And sets "authority_name" to "<authority_name>"
    And sets "ue_id" to "<ue_id>"
    And sets "ue_version_major" to "<version_major>"
    And sets "resource_id" to "<resource_id>"
    
    When sends "uri_serialize" request
    Then the serialized uri received is "<expected_uri>"
    
    Examples:
      | authority_name | ue_id       | resource_id   | version_major        | expected_uri                          |
      | vcu.my_car_vin | 1235        |               | 2                    | //vcu.my_car_vin/4d3/2/0              |
      | vcu.my_car_vin | 2345        |               | 1                    | //vcu.my_car_vin/929/1/0              |
      | vcu.my_car_vin | 2345        |               |                      | //vcu.my_car_vin/929/0/0              |
      | vcu.my_car_vin | 2345        | 1234          | 1                    | //vcu.my_car_vin/929/1/4d2            |
      | vcu.my_car_vin | 2345        | 1234          | 2                    | //vcu.my_car_vin/929/2/4d2            |