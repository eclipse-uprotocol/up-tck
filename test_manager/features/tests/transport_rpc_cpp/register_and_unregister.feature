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

Feature: Testing register and unregister

  Scenario Outline: To test the registerlistener and unregisterlistener apis
    Given "<uE1>" creates data for "registerlistener"
    And sets "entity.name" to "body.access"
    And sets "entity.id" to "12345"
    And sets "entity.version_major" to "1"
    And sets "resource.name" to "door"
    And sets "resource.id" to "12345"
    And sets "resource.instance" to "front_left"
    And sets "resource.message" to "Door"
    When sends "registerlistener" request

    Then the status received with "code" is "OK"

    When "<uE1>" creates data for "unregisterlistener"
    And sets "entity.name" to "body.access"
    And sets "entity.id" to "12345"
    And sets "entity.version_major" to "1"
    And sets "resource.name" to "door"
    And sets "resource.id" to "12345"
    And sets "resource.instance" to "front_left"
    And sets "resource.message" to "Door"
    And sends "unregisterlistener" request

    Then the status received with "code" is "OK"

    Examples:
      | uE1    |
      | cpp    |


    Scenario Outline: Test unregisterlistener when no entity is registered to any topic
      Given "<uE1>" creates data for "unregisterlistener"
        And sets "entity.name" to "body.access"
        And sets "entity.id" to "12345"
        And sets "entity.version_major" to "1"
        And sets "resource.name" to "door"
        And sets "resource.id" to "12345"
        And sets "resource.instance" to "front_left"
        And sets "resource.message" to "Door"

      When sends "unregisterlistener" request

      Then the status received with "code" is "NOT_FOUND"

      Examples:
        | uE1    |
        | cpp    |
