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

Feature: URI Validation
  Scenario Outline: UUri Validation for an empty UUri
      Given "uE1" creates data for "uri_deserialize"

      When sends a "uri_deserialize" request with serialized input ""

      Then receives json with following set fields:
        | protobuf_field_names | protobuf_field_values         | protobuf_field_type |
        | authority_name       |                               | str                 |
        | ue_id                | 0                             | int                 |
        | ue_version_major     | 0                             | int                 |
        | resource_id          | 0                             | int                 |

      When "uE2" creates data for "uri_validate"
      And sets "validation_type" to "<validation_type>"
      And sets "uuri" to previous response data
      And sends "uri_validate" request

      Then receives validation result as "<bool_result>"

      Examples:
        | validation_type             | bool_result |
        | is_empty                    | True        |
        | is_rpc_method               | False       |
        | is_rpc_response             | False       |
        | is_default_resource_id      | False       |
        | is_topic                    | False       |


  Scenario Outline: UUri validation for a UUri with only authority_name
      Given "uE1" creates data for "uri_deserialize"

      When sends a "uri_deserialize" request with serialized input "//hi"

      Then receives json with following set fields:
        | protobuf_field_names | protobuf_field_values         | protobuf_field_type |
        | authority_name       | hi                            | str                 |
        | ue_id                | 0                             | int                 |
        | ue_version_major     | 0                             | int                 |
        | resource_id          | 0                             | int                 |

      When "uE2" creates data for "uri_validate"
      And sets "validation_type" to "<validation_type>"
      And sets "uuri" to previous response data
      And sends "uri_validate" request

      Then receives validation result as "<bool_result>"

      Examples:
        | validation_type             | bool_result |
        | is_empty                    | False       |
        | is_rpc_method               | False       |
        | is_rpc_response             | True        |
        | is_default_resource_id      | True        |
        | is_topic                    | False       |
  
  Scenario Outline: UUri validation for a UUri with resource_id less than min_topic_id
    Given "uE1" creates data for "uri_deserialize"

    When sends a "uri_deserialize" request with serialized input "//hi/1/1/7FFF"

    Then receives json with following set fields:
      | protobuf_field_names | protobuf_field_values         | protobuf_field_type |
      | authority_name       | hi                            | str                 |
      | ue_id                | 1                             | int                 |
      | ue_version_major     | 1                             | int                 |
      | resource_id          | 32767                         | int                 |

    When "uE2" creates data for "uri_validate"
    And sets "validation_type" to "<validation_type>"
    And sets "uuri" to previous response data
    And sends "uri_validate" request

    Then receives validation result as "<bool_result>"

    Examples:
      | validation_type             | bool_result |
      | is_rpc_method               | True        |

  Scenario Outline: UUri validation for a UUri with resource_id greater than min_topic_id
    Given "uE1" creates data for "uri_deserialize"

    When sends a "uri_deserialize" request with serialized input "//hi/1/1/8000"

    Then receives json with following set fields:
      | protobuf_field_names | protobuf_field_values         | protobuf_field_type |
      | authority_name       | hi                            | str                 |
      | ue_id                | 1                             | int                 |
      | ue_version_major     | 1                             | int                 |
      | resource_id          | 32768                         | int                 |

    When "uE2" creates data for "uri_validate"
    And sets "validation_type" to "<validation_type>"
    And sets "uuri" to previous response data
    And sends "uri_validate" request

    Then receives validation result as "<bool_result>"

    Examples:
      | validation_type             | bool_result |
      | is_rpc_method               | False       |

  Scenario Outline: UUri validation for a UUri with resource_id equal to rpc_response_id
    Given "uE1" creates data for "uri_deserialize"

    When sends a "uri_deserialize" request with serialized input "//hi/1/1/8000"

    Then receives json with following set fields:
      | protobuf_field_names | protobuf_field_values         | protobuf_field_type |
      | authority_name       | hi                            | str                 |
      | ue_id                | 1                             | int                 |
      | ue_version_major     | 1                             | int                 |
      | resource_id          | 32768                         | int                 |

    When "uE2" creates data for "uri_validate"
    And sets "validation_type" to "<validation_type>"
    And sets "uuri" to previous response data
    And sends "uri_validate" request

    Then receives validation result as "<bool_result>"

    Examples:
      | validation_type             | bool_result |
      | is_rpc_method               | False       |

  Scenario Outline: UUri matches when equal to //authority/A410/3/1003
    Given "uE1" creates data for "uri_deserialize"

    When sends a "uri_deserialize" request with serialized input "//authority/A410/3/1003"

    Then receives json with following set fields:
      | protobuf_field_names | protobuf_field_values         | protobuf_field_type |
      | authority_name       | authority                     | str                 |
      | ue_id                | 42000                         | int                 |
      | ue_version_major     | 3                             | int                 |
      | resource_id          | 4099                          | int                 |

    When "uE2" creates data for "uri_validate"
    And sets "validation_type" to "<validation_type>"
    And sets "uuri" to previous response data
    And sets "uuri_2" to "//authority/A410/3/1003"
    And sends "uri_validate" request

    Then receives validation result as "<bool_result>"

    Examples:
      | validation_type             | bool_result |
      | matches                     | True        |

  Scenario Outline: UUri matches when wildcard authority equal to //authority/A410/3/1003
    Given "uE1" creates data for "uri_deserialize"

    When sends a "uri_deserialize" request with serialized input "//*/A410/3/1003"

    Then receives json with following set fields:
      | protobuf_field_names | protobuf_field_values         | protobuf_field_type |
      | authority_name       | *                             | str                 |
      | ue_id                | 42000                         | int                 |
      | ue_version_major     | 3                             | int                 |
      | resource_id          | 4099                          | int                 |

    When "uE2" creates data for "uri_validate"
    And sets "validation_type" to "<validation_type>"
    And sets "uuri" to previous response data
    And sets "uuri_2" to "//authority/A410/3/1003"
    And sends "uri_validate" request

    Then receives validation result as "<bool_result>"

    Examples:
      | validation_type             | bool_result |
      | matches                     | True        |
  
  Scenario Outline: UUri matches when wildcard authority equal to /A410/3/1003
    Given "uE1" creates data for "uri_deserialize"

    When sends a "uri_deserialize" request with serialized input "//*/A410/3/1003"

    Then receives json with following set fields:
      | protobuf_field_names | protobuf_field_values         | protobuf_field_type |
      | authority_name       | *                             | str                 |
      | ue_id                | 42000                         | int                 |
      | ue_version_major     | 3                             | int                 |
      | resource_id          | 4099                          | int                 |

    When "uE2" creates data for "uri_validate"
    And sets "validation_type" to "<validation_type>"
    And sets "uuri" to previous response data
    And sets "uuri_2" to "/A410/3/1003"
    And sends "uri_validate" request

    Then receives validation result as "<bool_result>"

    Examples:
      | validation_type             | bool_result |
      | matches                     | True        |

  Scenario Outline: UUri matches when wildcard entity_id equal to //authority/A410/3/1003
    Given "uE1" creates data for "uri_deserialize"

    When sends a "uri_deserialize" request with serialized input "//authority/FFFF/3/1003"

    Then receives json with following set fields:
      | protobuf_field_names | protobuf_field_values         | protobuf_field_type |
      | authority_name       | authority                     | str                 |
      | ue_id                | 65535                         | int                 |
      | ue_version_major     | 3                             | int                 |
      | resource_id          | 4099                          | int                 |

    When "uE2" creates data for "uri_validate"
    And sets "validation_type" to "<validation_type>"
    And sets "uuri" to previous response data
    And sets "uuri_2" to "//authority/A410/3/1003"
    And sends "uri_validate" request

    Then receives validation result as "<bool_result>"

    Examples:
      | validation_type             | bool_result |
      | matches                     | True        |

  Scenario Outline: UUri matches when matching entity instance equal to //authority/2A410/3/1003
    Given "uE1" creates data for "uri_deserialize"

    When sends a "uri_deserialize" request with serialized input "//authority/A410/3/1003"

    Then receives json with following set fields:
      | protobuf_field_names | protobuf_field_values         | protobuf_field_type |
      | authority_name       | authority                     | str                 |
      | ue_id                | 42000                         | int                 |
      | ue_version_major     | 3                             | int                 |
      | resource_id          | 4099                          | int                 |

    When "uE2" creates data for "uri_validate"
    And sets "validation_type" to "<validation_type>"
    And sets "uuri" to previous response data
    And sets "uuri_2" to "//authority/2A410/3/1003"
    And sends "uri_validate" request

    Then receives validation result as "<bool_result>"

    Examples:
      | validation_type             | bool_result |
      | matches                     | True        |

  Scenario Outline: UUri matches when wildcard entity version equal to //authority/A410/3/1003
    Given "uE1" creates data for "uri_deserialize"

    When sends a "uri_deserialize" request with serialized input "//authority/A410/FF/1003"

    Then receives json with following set fields:
      | protobuf_field_names | protobuf_field_values         | protobuf_field_type |
      | authority_name       | authority                     | str                 |
      | ue_id                | 42000                         | int                 |
      | ue_version_major     | 255                           | int                 |
      | resource_id          | 4099                          | int                 |

    When "uE2" creates data for "uri_validate"
    And sets "validation_type" to "<validation_type>"
    And sets "uuri" to previous response data
    And sets "uuri_2" to "//authority/A410/3/1003"
    And sends "uri_validate" request

    Then receives validation result as "<bool_result>"

    Examples:
      | validation_type             | bool_result |
      | matches                     | True        |

  Scenario Outline: UUri matches when wildcard resource id equal to //authority/A410/3/1003
    Given "uE1" creates data for "uri_deserialize"

    When sends a "uri_deserialize" request with serialized input "//authority/A410/3/FFFF"

    Then receives json with following set fields:
      | protobuf_field_names | protobuf_field_values         | protobuf_field_type |
      | authority_name       | authority                     | str                 |
      | ue_id                | 42000                         | int                 |
      | ue_version_major     | 3                             | int                 |
      | resource_id          | 65535                         | int                 |

    When "uE2" creates data for "uri_validate"
    And sets "validation_type" to "<validation_type>"
    And sets "uuri" to previous response data
    And sets "uuri_2" to "//authority/A410/3/1003"
    And sends "uri_validate" request

    Then receives validation result as "<bool_result>"

    Examples:
      | validation_type             | bool_result |
      | matches                     | True        |
  
  Scenario Outline: UUri doesn't match when uppercase authorty not equal to //authority/A410/3/1003
    Given "uE1" creates data for "uri_deserialize"

    When sends a "uri_deserialize" request with serialized input "//Authority/A410/3/1003"

    Then receives json with following set fields:
      | protobuf_field_names | protobuf_field_values         | protobuf_field_type |
      | authority_name       | Authority                     | str                 |
      | ue_id                | 42000                         | int                 |
      | ue_version_major     | 3                             | int                 |
      | resource_id          | 4099                          | int                 |

    When "uE2" creates data for "uri_validate"
    And sets "validation_type" to "<validation_type>"
    And sets "uuri" to previous response data
    And sets "uuri_2" to "//authority/A410/3/1003"
    And sends "uri_validate" request

    Then receives validation result as "<bool_result>"

    Examples:
      | validation_type             | bool_result |
      | matches                     | False       |

  Scenario Outline: UUri doesn't match when local pattern match isn't equal to //authority/A410/3/1003
    Given "uE1" creates data for "uri_deserialize"

    When sends a "uri_deserialize" request with serialized input "/A410/3/1003"

    Then receives json with following set fields:
      | protobuf_field_names | protobuf_field_values         | protobuf_field_type |
      | authority_name       |                               | str                 |
      | ue_id                | 42000                         | int                 |
      | ue_version_major     | 3                             | int                 |
      | resource_id          | 4099                          | int                 |

    When "uE2" creates data for "uri_validate"
    And sets "validation_type" to "<validation_type>"
    And sets "uuri" to previous response data
    And sets "uuri_2" to "//authority/A410/3/1003"
    And sends "uri_validate" request

    Then receives validation result as "<bool_result>"

    Examples:
      | validation_type             | bool_result |
      | matches                     | False       |
  
  Scenario Outline: UUri doesn't match when different authority to //authority/A410/3/1003
    Given "uE1" creates data for "uri_deserialize"

    When sends a "uri_deserialize" request with serialized input "//other/A410/3/1003"

    Then receives json with following set fields:
      | protobuf_field_names | protobuf_field_values         | protobuf_field_type |
      | authority_name       | other                         | str                 |
      | ue_id                | 42000                         | int                 |
      | ue_version_major     | 3                             | int                 |
      | resource_id          | 4099                          | int                 |

    When "uE2" creates data for "uri_validate"
    And sets "validation_type" to "<validation_type>"
    And sets "uuri" to previous response data
    And sets "uuri_2" to "//authority/A410/3/1003"
    And sends "uri_validate" request

    Then receives validation result as "<bool_result>"

    Examples:
      | validation_type             | bool_result |
      | matches                     | False       |
  
  Scenario Outline: UUri doesn't match when different entity id to //authority/A410/3/1003
    Given "uE1" creates data for "uri_deserialize"

    When sends a "uri_deserialize" request with serialized input "//authority/45/3/1003"

    Then receives json with following set fields:
      | protobuf_field_names | protobuf_field_values         | protobuf_field_type |
      | authority_name       | authority                     | str                 |
      | ue_id                | 69                            | int                 |
      | ue_version_major     | 3                             | int                 |
      | resource_id          | 4099                          | int                 |

    When "uE2" creates data for "uri_validate"
    And sets "validation_type" to "<validation_type>"
    And sets "uuri" to previous response data
    And sets "uuri_2" to "//authority/A410/3/1003"
    And sends "uri_validate" request

    Then receives validation result as "<bool_result>"

    Examples:
      | validation_type             | bool_result |
      | matches                     | False       |

  Scenario Outline: UUri doesn't match when different entity instance to //authority/A410/3/1003
    Given "uE1" creates data for "uri_deserialize"

    When sends a "uri_deserialize" request with serialized input "//authority/30A410/3/1003"

    Then receives json with following set fields:
      | protobuf_field_names | protobuf_field_values         | protobuf_field_type |
      | authority_name       | authority                     | str                 |
      | ue_id                | 3187728                       | int                 |
      | ue_version_major     | 3                             | int                 |
      | resource_id          | 4099                          | int                 |

    When "uE2" creates data for "uri_validate"
    And sets "validation_type" to "<validation_type>"
    And sets "uuri" to previous response data
    And sets "uuri_2" to "//authority/A410/3/1003"
    And sends "uri_validate" request

    Then receives validation result as "<bool_result>"

    Examples:
      | validation_type             | bool_result |
      | matches                     | False       |
  
  Scenario Outline: UUri doesn't match when different entity version to //authority/A410/3/1003
    Given "uE1" creates data for "uri_deserialize"

    When sends a "uri_deserialize" request with serialized input "//authority/A410/1/1003"

    Then receives json with following set fields:
      | protobuf_field_names | protobuf_field_values         | protobuf_field_type |
      | authority_name       | authority                     | str                 |
      | ue_id                | 42000                         | int                 |
      | ue_version_major     | 1                             | int                 |
      | resource_id          | 4099                          | int                 |

    When "uE2" creates data for "uri_validate"
    And sets "validation_type" to "<validation_type>"
    And sets "uuri" to previous response data
    And sets "uuri_2" to "//authority/A410/3/1003"
    And sends "uri_validate" request

    Then receives validation result as "<bool_result>"

    Examples:
      | validation_type             | bool_result |
      | matches                     | False       |

  Scenario Outline: UUri doesn't match when different resource id to //authority/A410/3/1003
    Given "uE1" creates data for "uri_deserialize"

    When sends a "uri_deserialize" request with serialized input "//authority/A410/3/ABCD"

    Then receives json with following set fields:
      | protobuf_field_names | protobuf_field_values         | protobuf_field_type |
      | authority_name       | authority                     | str                 |
      | ue_id                | 42000                         | int                 |
      | ue_version_major     | 3                             | int                 |
      | resource_id          | 43981                         | int                 |

    When "uE2" creates data for "uri_validate"
    And sets "validation_type" to "<validation_type>"
    And sets "uuri" to previous response data
    And sets "uuri_2" to "//authority/A410/3/1003"
    And sends "uri_validate" request

    Then receives validation result as "<bool_result>"

    Examples:
      | validation_type             | bool_result |
      | matches                     | False       |