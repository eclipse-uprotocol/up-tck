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

Feature: Publish Subscribe Performance

  Scenario Outline: To test send method at various rates

    Given "<uE2>" creates data for "performancesubscriber"
        And sets "topics" to "<topics>"
    When sends "performancesubscriber" request
    And user waits "2" second
    Then the status received with "code" is "OK"

    Given "<uE1>" creates data for "performancepublisher"
        And sets "topics" to "<topics>"
        And sets "events" to "<events>"
        And sets "interval" to "<interval>"
        And sets "timeout" to "<timeout>"
    When sends "performancepublisher" request
    And  user waits for publisher timeout
    Then the status received with "code" is "OK"
    And average latency is less than "<average_latency>" in milliseconds
    
    Given "<uE2>" creates data for "unregistersubscribers"
        And sets "topics" to "<topics>"
    When sends "unregistersubscribers" request
    And user waits "2" second
    Then the status received with "code" is "OK"

    Examples:
      | uE1    | uE2      | topics | events | interval   | timeout | average_latency |
      | java   | python   | 1      | 20     | 200        | 5       | 1000            |
      | java   | python   | 1      | 50     | 150        | 5       | 1000            |
      | java   | python   | 1      | 50     | 100        | 5       | 1000            |
      | java   | python   | 1      | 100    | 50         | 5       | 1000            |
      | python | python   | 1      | 20     | 200        | 5       | 1000            |
      | python | python   | 1      | 50     | 150        | 5       | 1000            |
      | python | python   | 1      | 50     | 100        | 5       | 1000            |
      | python | python   | 1      | 100    | 50         | 5       | 1000            |
      | java   | java     | 1      | 20     | 200        | 5       | 1000            |
      | java   | java     | 1      | 50     | 150        | 5       | 1000            |
      | java   | java     | 1      | 50     | 100        | 5       | 1000            |
      | java   | java     | 1      | 100    | 50         | 5       | 1000            |
      | python | java     | 1      | 20     | 200        | 5       | 1000            |
      | python | java     | 1      | 50     | 150        | 5       | 1000            |
      | python | java     | 1      | 50     | 100        | 5       | 1000            |
      | python | java     | 1      | 100    | 50         | 5       | 1000            |