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
    Given "<uE1>" creates data for "uri_deserialize"
    When sends a "uri_deserialize" request with serialized input "<serialized_uri>"

    Then the deserialized uri received should have the following properties:
      | Field                | Value                  |
      | ue_id                | <ue_id>                |
      | ue_version_major     | <ue_version_major>     |
      | resource_id          | <resource_id>          |

    Examples:
      | ue_id       | resource_id   | ue_version_major     | serialized_uri          |
      | 9029        | 0             | 2                    | /2345/2                 |
      | 9029        | 0             | 1                    | /2345/1                 |
      | 9029        | 4660          | 2                    | /2345/2/1234            |
      | 9029        | 4660          | 1                    | /2345/1/1234            |


  Scenario Outline: Testing the remote uri deserializer
    Given "<uE1>" creates data for "uri_deserialize"
    When sends a "uri_deserialize" request with serialized input "<serialized_uri>"
    Then the deserialized uri received should have the following properties:
      | Field                | Value                  |
      | authority_name       | <authority_name>       |
      | ue_id                | <ue_id>                |
      | ue_version_major     | <ue_version_major>     |
      | resource_id          | <resource_id>          |

    Examples:
      | authority_name | ue_id        | resource_id   | ue_version_major     | serialized_uri                            |
      | vcu.my_car_vin | 1193046      | 0             | 2                    | //vcu.my_car_vin/123456/2                 |
      | vcu.my_car_vin | 1193046      | 0             | 1                    | //vcu.my_car_vin/123456/1                 |
      | vcu.my_car_vin | 1193046      | 9029          | 1                    | //vcu.my_car_vin/123456/1/2345            |
      | vcu.my_car_vin | 1193046      | 9029          | 2                    | //vcu.my_car_vin/123456/2/2345            |
