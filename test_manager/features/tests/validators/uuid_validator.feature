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

Feature: UUID Validation

  Scenario Outline: Validate UUIDs with Various Versions and Types
    Given "uE1" creates data for "uuid_validate"
        And sets "uuid_type" to "<uuid_type>"
        And sets "validator_type" to "<validator_type>"

    When sends "uuid_validate" request
        Then receives validation result as "<expected_status>"
        And  receives validation message as "<expected_message>"

    Examples:
      | uuid_type      | validator_type                 | expected_status    | expected_message                                              |
      | uprotocol      | get_validator                  | True               | none                                                          |
      | uprotocol      | uprotocol                      | True               | none                                                          |
      | invalid        | get_validator                  | False              | Invalid UUID Version,Invalid UUID Variant,Invalid UUID Time   |
      | uprotocol_time | uprotocol                      | False              | Invalid UUID Time                                             |
      |                | uprotocol                      | False              | Invalid UUIDv8 Version,Invalid UUID Time                      |
      | uuidv6         | uprotocol                      | False              | Invalid UUIDv8 Version                                        |
      | invalid        | uprotocol                      | False              | Invalid UUIDv8 Version,Invalid UUID Time                      |
      | uuidv4         | uprotocol                      | False              | Invalid UUIDv8 Version,Invalid UUID Time                      |
      | uuidv6         | get_validator_is_uuidv6        | True               | none                                                          |
      | uuidv6         | get_validator                  | True               | none                                                          |
      | invalid        | uuidv6                         | False              | Not a UUIDv6 Version,Invalid UUIDv6 variant,Invalid UUID Time |
      |                | uuidv6                         | False              | Not a UUIDv6 Version,Invalid UUIDv6 variant,Invalid UUID Time |
      | uprotocol      | uuidv6                         | False              | Not a UUIDv6 Version                                          |