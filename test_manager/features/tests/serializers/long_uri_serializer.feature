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
Feature: Default

  Scenario Outline: Testing the local uri serializer
    Given "<uE1>" creates data for "uri_serialize"
    And sets "entity.name" to "<entity_name>"
    And sets "entity.version_major" to "<entity_version_major>"
    And sets "resource.name" to "<resource_name>"
    And sets "resource.instance" to "<resource_instance>"
    And sets "resource.message" to "<resource_message>"
    When sends "uri_serialize" request
    And user waits "1" second
    Then the serialized uri received is "<expected_uri>"
    Examples:
      | uE1    | entity_name | resource_name | resource_instance | resource_message | entity_version_major | expected_uri              |
      | python | neelam      | rpc           | test              |                  |                      | /neelam//rpc.test         |
      | python | neelam      |               |                   |                  |                      | /neelam                   |
      | python | neelam      |               |                   |                  | 1                    | /neelam/1                 |
      | python | neelam      | test          |                   |                  |                      | /neelam//test             |
      | python | neelam      | test          |                   |                  | 1                    | /neelam/1/test            |
      | python | neelam      | test          | front             |                  |                      | /neelam//test.front       |
      | python | neelam      | test          | front             |                  | 1                    | /neelam/1/test.front      |
      | python | neelam      | test          | front             | Test             |                      | /neelam//test.front#Test  |
      | python | neelam      | test          | front             | Test             | 1                    | /neelam/1/test.front#Test |
      | java   | neelam      | rpc           | test              |                  |                      | /neelam//rpc.test         |
      | java   | neelam      |               |                   |                  |                      | /neelam                   |
      | java   | neelam      |               |                   |                  | 1                    | /neelam/1                 |
      | java   | neelam      | test          |                   |                  |                      | /neelam//test             |
      | java   | neelam      | test          |                   |                  | 1                    | /neelam/1/test            |
      | java   | neelam      | test          | front             |                  |                      | /neelam//test.front       |
      | java   | neelam      | test          | front             |                  | 1                    | /neelam/1/test.front      |
      | java   | neelam      | test          | front             | Test             |                      | /neelam//test.front#Test  |
      | java   | neelam      | test          | front             | Test             | 1                    | /neelam/1/test.front#Test |

