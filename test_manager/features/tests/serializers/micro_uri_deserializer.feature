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

  Scenario Outline: Testing the local uri micro deserializer
    Given "uE1" creates data for "micro_deserialize_uri"
    When sends a "micro_deserialize_uri" request with micro serialized input "<micro_serialized_uri_as_base64_str>"

    Then the deserialized uri received should have the following properties:
      | Field                | Value                  |
      | authority.id         | <authority_id>         |
      | authority.name       | <authority_name>       |
      | entity.id            | <entity_id>            |
      | entity.name          | <entity_name>          |
      | entity.version_major | <entity_version_major> |
      | resource.id          | <resource_id>          |
      | resource.name        | <resource_name>        |
      | resource.instance    | <resource_instance>    |
      | resource.message     | <resource_message>     |
    Examples:
      | authority_id       | authority_name | entity_id | entity_name | entity_version_major | resource_id | resource_name | resource_instance | resource_message | micro_serialized_uri_as_base64_str |
      |                    |                | 0         |             | 0                    | 0           |               |                   |                  | <empty>                      |
      |                    |                | 1         |             | 0                    | 1           | rpc           |                   |                  | AQAAAQABAAA= |
      |                    |                | 1         |             | 0                    | 1           | rpc           |                   |                  | AQAAAQABAAA= |
      |                    |                | 1         |             | 1                    | 1           | rpc           |                   |                  | AQAAAQABAQA= |
      |                    |                | 1         |             | 0                    | 1           | rpc           |                   |                  | AQAAAQABAAA= |
      |                    |                | 2         |             | 1                    | 3           | rpc           |                   |                  | AQAAAwACAQA= |
      |                    |                | 0         |             | 0                    | 0           | rpc           | response          |                  | AQAAAAAAAAA= |
      |                    |                | 100       |             | 1                    | 300         | rpc           |                   |                  | AQABLABkAQA= |
      |                    |                | 255       |             | 0                    | 255         | rpc           |                   |                  | AQAA/wD/AAA= |
      |                    |                | 256       |             | 1                    | 256         | rpc           |                   |                  | AQABAAEAAQA= |
      | unique id 1234     |                | 29999     |             | 254                  | 99          | rpc           |                   |                  | AQMAY3Uv/gAOdW5pcXVlIGlkIDEyMzQ= |