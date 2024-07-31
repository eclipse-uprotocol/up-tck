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

Feature: UUID de-serialization

  Scenario Outline: Testing the long uuid deserializer
    Given "uE1" creates data for "uuid_deserialize"
    When sends a "uuid_deserialize" request with serialized input "<serialized_uuid>"
    Then the deserialized uuid received should have the following properties:
      | Field | Value |
      | lsb   | <lsb> |
      | msb   | <msb> |

    Examples:
      | lsb                  | msb                | serialized_uuid                      |
      | 11155833020022798372 | 112128268635242497 | 018e5c10-f548-8001-9ad1-7b068c083824 |