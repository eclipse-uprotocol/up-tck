# -------------------------------------------------------------------------
#
# Copyright (c) 2024 General Motors GTO LLC
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# License); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# AS IS BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
# SPDX-FileType: SOURCE
# SPDX-FileCopyrightText: 2024 General Motors GTO LLC
# SPDX-License-Identifier: Apache-2.0
#
# -------------------------------------------------------------------------

Feature: URI Validation
  Scenario Outline: UUri validate completely filled UUri
    Given "uE1" creates data for "uri_deserialize"

    When sends a "uri_deserialize" request with serialized input "//authority_name_nameName/name of entity/64/resource name.resource instance#message of resource"

    Then receives json with following set fields:
      | protobuf_field_names | protobuf_field_values         | protobuf_field_type |
      | authority.ip         |                               | bytes               |
      | authority.id         |                               | bytes               |
      | authority.name       | authority_name_nameName       | str                 |
      | entity.id            | 0                             | int                 |
      | entity.name          | name of entity                | str                 |
      | entity.version_major | 64                            | int                 |
      | entity.version_minor | 0                             | int                 |
      | resource.name        | resource name                 | str                 |
      | resource.instance    | resource instance             | str                 |
      | resource.message     | message of resource           | str                 |
      | resource.id          | 0                             | int                 |

    When "uE2" creates data for "uri_validate"
    And sets "validation_type" to "<validation_type>"
    And sets "uuri" to previous response data
    And sends "uri_validate" request

    Then receives validation result as "<bool_result>"
    And  receives validation message as "<message_result>"

    Examples:
      | validation_type | bool_result | message_result             |
      | uri             | True        |                            |
      # False for now bc default message="" is set, but should be True
      | rpc_response    | False       | Invalid RPC response type. |
      | rpc_method      | False       | Invalid RPC method uri. Uri should be the method to be called, or method from response. |
      | is_empty        | False       |                            |

      # is_resolved == is long formed (filled names in uauth, enti, & resrc) and micro formed (existing ids in uauth, enti, & resrc )
      | is_resolved     | True        |                            |
      | is_micro_form   | True        |                            |
      | is_long_form    | True        |                            |

  Scenario Outline: UUri validate completely filled UUri 2
    Given "uE1" creates data for "uri_deserialize"

    When sends a "uri_deserialize" request with serialized input "//uAuthName/entityName/1/resrcName.instance#Message"

    Then receives json with following set fields:
      | protobuf_field_names | protobuf_field_values         | protobuf_field_type |
      | authority.ip         |                               | bytes               |
      | authority.id         |                               | bytes               |
      | authority.name       | uAuthName                     | str                 |
      | entity.id            | 0                             | int                 |
      | entity.name          | entityName                    | str                 |
      | entity.version_major | 1                             | int                 |
      | entity.version_minor | 0                             | int                 |
      | resource.name        | resrcName                     | str                 |
      | resource.instance    | instance                      | str                 |
      | resource.message     | Message                       | str                 |
      | resource.id          | 0                             | int                 |

    When "uE2" creates data for "uri_validate"
    And sets "validation_type" to "<validation_type>"
    And sets "uuri" to previous response data
    And sends "uri_validate" request

    Then receives validation result as "<bool_result>"
    And  receives validation message as "<message_result>"

    Examples:
      | validation_type | bool_result | message_result             |
      | uri             | True        |                            |
      # False for now bc default message="" is set, but should be True
      | rpc_response    | False       | Invalid RPC response type. |
      # rpc_method: resource.name == "rpc", resource.instance != "" or id < 32768
      | rpc_method      | False       | Invalid RPC method uri. Uri should be the method to be called, or method from response. |
      | is_empty        | False       |                            |

      # is_resolved == is long formed (filled names in uauth, enti, & resrc) and micro formed (existing ids in uauth, enti, & resrc )
      | is_resolved     | True        |                            |
      | is_micro_form   | True        |                            |
      | is_long_form    | True        |                            |

  Scenario Outline: UUri validate completely filled UUri, but no uAuthority
    Given "uE1" creates data for "uri_deserialize"

    When sends a "uri_deserialize" request with serialized input "/entityName/1/resrcName.instance#Message"

    Then receives json with following set fields:
      | protobuf_field_names | protobuf_field_values         | protobuf_field_type |
      | authority.ip         |                               | bytes               |
      | authority.id         |                               | bytes               |
      | authority.name       |                               | str                 |
      | entity.id            | 0                             | int                 |
      | entity.name          | entityName                    | str                 |
      | entity.version_major | 1                             | int                 |
      | entity.version_minor | 0                             | int                 |
      | resource.name        | resrcName                     | str                 |
      | resource.instance    | instance                      | str                 |
      | resource.message     | Message                       | str                 |
      | resource.id          | 0                             | int                 |

    When "uE2" creates data for "uri_validate"
    And sets "validation_type" to "<validation_type>"
    And sets "uuri" to previous response data
    And sends "uri_validate" request

    Then receives validation result as "<bool_result>"
    And  receives validation message as "<message_result>"

    Examples:
      | validation_type | bool_result | message_result             |
      | uri             | True        |                            |
      # False for now bc default message="" is set, but should be True
      | rpc_response    | False       | Invalid RPC response type. |
      # rpc_method: resource.name == "rpc", resource.instance != "" or id < 32768
      | rpc_method      | False       | Invalid RPC method uri. Uri should be the method to be called, or method from response. |
      | is_empty        | False       |                            |

      # is_resolved == is long formed (filled names in uauth, enti, & resrc) and micro formed (existing ids in uauth, enti, & resrc )
      | is_resolved     | False       |                            |
      | is_micro_form   | True        |                            |
      | is_long_form    | False       |                            |

  Scenario Outline: UUri validate completely filled UUri, but no UEntity
    Given "uE1" creates data for "uri_deserialize"

    When sends a "uri_deserialize" request with serialized input "//uAuthName///resrcName.instance#Message"

    Then receives json with following set fields:
      | protobuf_field_names | protobuf_field_values         | protobuf_field_type |
      | authority.ip         |                               | bytes               |
      | authority.id         |                               | bytes               |
      | authority.name       | uAuthName                     | str                 |
      | entity.id            | 0                             | int                 |
      | entity.name          |                               | str                 |
      | entity.version_major | 0                             | int                 |
      | entity.version_minor | 0                             | int                 |
      | resource.name        | resrcName                     | str                 |
      | resource.instance    | instance                      | str                 |
      | resource.message     | Message                       | str                 |
      | resource.id          | 0                             | int                 |

    When "uE2" creates data for "uri_validate"
    And sets "validation_type" to "<validation_type>"
    And sets "uuri" to previous response data
    And sends "uri_validate" request

    Then receives validation result as "<bool_result>"
    And  receives validation message as "<message_result>"

    Examples:
      | validation_type | bool_result | message_result             |
      | uri             | False       | Uri is missing uSoftware Entity name. |
      # False for now bc default message="" is set, but should be True
      | rpc_response    | False       | Uri is missing uSoftware Entity name. |
      # rpc_method: resource.name == "rpc", resource.instance != "" or id < 32768
      | rpc_method      | False       | Uri is missing uSoftware Entity name. |
      | is_empty        | False       |                            |

      # is_resolved == is long formed (filled names in uauth, enti, & resrc) and micro formed (existing ids in uauth, enti, & resrc )
      | is_resolved     | False       |                            |
      | is_micro_form   | True        |                            |
      | is_long_form    | False       |                            |
       

  Scenario Outline: UUri validate completely filled UUri, but no uResource
    Given "uE1" creates data for "uri_deserialize"

    When sends a "uri_deserialize" request with serialized input "//uAuthName/entityName/1"

    Then receives json with following set fields:
      | protobuf_field_names | protobuf_field_values         | protobuf_field_type |
      | authority.ip         |                               | bytes               |
      | authority.id         |                               | bytes               |
      | authority.name       | uAuthName                     | str                 |
      | entity.id            | 0                             | int                 |
      | entity.name          | entityName                    | str                 |
      | entity.version_major | 1                             | int                 |
      | entity.version_minor | 0                             | int                 |
      | resource.name        |                               | str                 |
      | resource.instance    |                               | str                 |
      | resource.message     |                               | str                 |
      | resource.id          | 0                             | int                 |

    When "uE2" creates data for "uri_validate"
    And sets "validation_type" to "<validation_type>"
    And sets "uuri" to previous response data
    And sends "uri_validate" request

    Then receives validation result as "<bool_result>"
    And  receives validation message as "<message_result>"

    Examples:
      | validation_type | bool_result | message_result             |
      | uri             | True        |                            |
      # False for now bc default message="" is set, but should be True
      | rpc_response    | False       | Invalid RPC response type. |
      # rpc_method: resource.name == "rpc", resource.instance != "" or id < 32768
      | rpc_method      | False       | Invalid RPC method uri. Uri should be the method to be called, or method from response. |
      | is_empty        | False       |                            |

      # is_resolved == is long formed (filled names in uauth, enti, & resrc) and micro formed (existing ids in uauth, enti, & resrc )
      | is_resolved     | False       |                            |
      | is_micro_form   | True        |                            |
      | is_long_form    | False       |                            |
       
  
  Scenario Outline: UUri validate purely remote UUri
    Given "uE1" creates data for "uri_deserialize"

    When sends a "uri_deserialize" request with serialized input ""

    Then receives json with following set fields:
      | protobuf_field_names | protobuf_field_values         | protobuf_field_type |
      | authority.ip         |                               | bytes               |
      | authority.name       |                               | str                 |
      | entity.id            | 0                             | int                 |
      | entity.name          |                               | str                 |
      | entity.version_major | 0                             | int                 |
      | entity.version_minor | 0                             | int                 |
      | resource.name        |                               | str                 |
      | resource.instance    |                               | str                 |
      | resource.message     |                               | str                 |
      | resource.id          | 0                             | int                 |

    When "uE2" creates data for "uri_validate"
    And sets "validation_type" to "<validation_type>"
    And sets "uuri" to previous response data
    And sends "uri_validate" request

    Then receives validation result as "<bool_result>"
    And  receives validation message as "<message_result>"

    Examples:
      | validation_type | bool_result | message_result             |
      | uri             | False       | Uri is missing uSoftware Entity name. |
      # False for now bc default message="" is set, but should be True
      | rpc_response    | False       | Uri is missing uSoftware Entity name. |
      # rpc_method: resource.name == "rpc", resource.instance != "" or id < 32768
      | rpc_method      | False       | Uri is missing uSoftware Entity name. |
      | is_empty        | False       |                            |

      # is_resolved == is long formed (filled names in uauth, enti, & resrc) and micro formed (existing ids in uauth, enti, & resrc )
      | is_resolved     | False       |                            |
      | is_micro_form   | True        |                            |
      | is_long_form    | False       |                            |

  Scenario Outline: UUri validate with random string
    Given "uE1" creates data for "uri_deserialize"

    When sends a "uri_deserialize" request with serialized input "random string"

    Then receives json with following set fields:
      | protobuf_field_names | protobuf_field_values         | protobuf_field_type |
      | authority.ip         |                               | bytes               |
      | authority.name       |                               | str                 |
      | entity.id            | 0                             | int                 |
      | entity.name          |                               | str                 |
      | entity.version_major | 0                             | int                 |
      | entity.version_minor | 0                             | int                 |
      | resource.name        |                               | str                 |
      | resource.instance    |                               | str                 |
      | resource.message     |                               | str                 |
      | resource.id          | 0                             | int                 |

    When "uE2" creates data for "uri_validate"
    And sets "validation_type" to "<validation_type>"
    And sets "uuri" to previous response data
    And sends "uri_validate" request

    Then receives validation result as "<bool_result>"
    And  receives validation message as "<message_result>"

    Examples:
      | validation_type | bool_result | message_result             |
      | uri             | False       | Uri is missing uSoftware Entity name. |
      # False for now bc default message="" is set, but should be True
      | rpc_response    | False       | Uri is missing uSoftware Entity name. |
      # rpc_method: resource.name == "rpc", resource.instance != "" or id < 32768
      | rpc_method      | False       | Uri is missing uSoftware Entity name. |
      | is_empty        | False       |                            |

      # is_resolved == is long formed (filled names in uauth, enti, & resrc) and micro formed (existing ids in uauth, enti, & resrc )
      | is_resolved     | False       |                            |
      | is_micro_form   | True        |                            |
      | is_long_form    | False       |                            |
  
  Scenario Outline: UUri validate just entity name to validate correctly
    Given "uE1" creates data for "uri_deserialize"

    When sends a "uri_deserialize" request with serialized input "/neelam"

    Then receives json with following set fields:
      | protobuf_field_names | protobuf_field_values         | protobuf_field_type |
      | authority.ip         |                               | bytes               |
      | authority.name       |                               | str                 |
      | entity.id            | 0                             | int                 |
      | entity.name          | neelam                        | str                 |
      | entity.version_major | 0                             | int                 |
      | entity.version_minor | 0                             | int                 |
      | resource.name        |                               | str                 |
      | resource.instance    |                               | str                 |
      | resource.message     |                               | str                 |
      | resource.id          | 0                             | int                 |

    When "uE2" creates data for "uri_validate"
    And sets "validation_type" to "<validation_type>"
    And sets "uuri" to previous response data
    And sends "uri_validate" request

    Then receives validation result as "<bool_result>"
    And  receives validation message as "<message_result>"

    Examples:
      | validation_type | bool_result | message_result             |
      | uri             | True        |                            |
      # False for now bc default message="" is set, but should be True
      | rpc_response    | False       | Invalid RPC response type. |
      # rpc_method: resource.name == "rpc", resource.instance != "" or id < 32768
      | rpc_method      | False       | Invalid RPC method uri. Uri should be the method to be called, or method from response. |
      | is_empty        | False       |                            |

      # is_resolved == is long formed (filled names in uauth, enti, & resrc) and micro formed (existing ids in uauth, enti, & resrc )
      | is_resolved     | False       |                            |
      | is_micro_form   | True        |                            |
      | is_long_form    | False       |                            |

  Scenario Outline: UUri validate filled UAuthority and partially filled UEntity, but no UEntity name
    Given "uE1" creates data for "uri_deserialize"

    When sends a "uri_deserialize" request with serialized input "//VCU.myvin//1"

    Then receives json with following set fields:
      | protobuf_field_names | protobuf_field_values         | protobuf_field_type |
      | authority.ip         |                               | bytes               |
      | authority.name       | VCU.myvin                     | str                 |
      | entity.id            | 0                             | int                 |
      | entity.name          |                               | str                 |
      | entity.version_major | 1                             | int                 |
      | entity.version_minor | 0                             | int                 |
      | resource.name        |                               | str                 |
      | resource.instance    |                               | str                 |
      | resource.message     |                               | str                 |
      | resource.id          | 0                             | int                 |

    When "uE2" creates data for "uri_validate"
    And sets "validation_type" to "<validation_type>"
    And sets "uuri" to previous response data
    And sends "uri_validate" request

    Then receives validation result as "<bool_result>"
    And  receives validation message as "<message_result>"

    Examples:
      | validation_type | bool_result | message_result             |
      | uri             | False       | Uri is missing uSoftware Entity name. |
      # False for now bc default message="" is set, but should be True
      | rpc_response    | False       | Uri is missing uSoftware Entity name. |
      # rpc_method: resource.name == "rpc", resource.instance != "" or id < 32768
      | rpc_method      | False       | Uri is missing uSoftware Entity name. |
      | is_empty        | False       |                            |

      # is_resolved == is long formed (filled names in uauth, enti, & resrc) and micro formed (existing ids in uauth, enti, & resrc )
      | is_resolved     | False       |                            |
      | is_micro_form   | True        |                            |
      | is_long_form    | False       |                            |

  Scenario Outline: UUri validate just UEntity name and version major
    Given "uE1" creates data for "uri_deserialize"

    When sends a "uri_deserialize" request with serialized input "/hartley/1000"

    Then receives json with following set fields:
      | protobuf_field_names | protobuf_field_values         | protobuf_field_type |
      | authority.ip         |                               | bytes               |
      | authority.name       |                               | str                 |
      | entity.id            | 0                             | int                 |
      | entity.name          | hartley                       | str                 |
      | entity.version_major | 1000                          | int                 |
      | entity.version_minor | 0                             | int                 |
      | resource.name        |                               | str                 |
      | resource.instance    |                               | str                 |
      | resource.message     |                               | str                 |
      | resource.id          | 0                             | int                 |

    When "uE2" creates data for "uri_validate"
    And sets "validation_type" to "<validation_type>"
    And sets "uuri" to previous response data
    And sends "uri_validate" request

    Then receives validation result as "<bool_result>"
    And  receives validation message as "<message_result>"

    Examples:
      | validation_type | bool_result | message_result             |
      | uri             | True        |                            |
      # False for now bc default message="" is set, but should be True
      | rpc_response    | False       | Invalid RPC response type. |
      # rpc_method: resource.name == "rpc", resource.instance != "" or id < 32768
      | rpc_method      | False       | Invalid RPC method uri. Uri should be the method to be called, or method from response. |
      | is_empty        | False       |                            |

      # is_resolved == is long formed (filled names in uauth, enti, & resrc) and micro formed (existing ids in uauth, enti, & resrc )
      | is_resolved     | False       |                            |
      | is_micro_form   | True        |                            |
      | is_long_form    | False       |                            |

  Scenario Outline: UUri validate random string 2
    Given "uE1" creates data for "uri_deserialize"

    When sends a "uri_deserialize" request with serialized input ":"

    Then receives json with following set fields:
      | protobuf_field_names | protobuf_field_values         | protobuf_field_type |
      | authority.ip         |                               | bytes               |
      | authority.name       |                               | str                 |
      | entity.id            | 0                             | int                 |
      | entity.name          |                               | str                 |
      | entity.version_major | 0                             | int                 |
      | entity.version_minor | 0                             | int                 |
      | resource.name        |                               | str                 |
      | resource.instance    |                               | str                 |
      | resource.message     |                               | str                 |
      | resource.id          | 0                             | int                 |

    When "uE2" creates data for "uri_validate"
    And sets "validation_type" to "<validation_type>"
    And sets "uuri" to previous response data
    And sends "uri_validate" request

    Then receives validation result as "<bool_result>"
    And  receives validation message as "<message_result>"

    Examples:
      | validation_type | bool_result | message_result             |
      | uri             | False       | Uri is missing uSoftware Entity name. |
      # False for now bc default message="" is set, but should be True
      | rpc_response    | False       | Uri is missing uSoftware Entity name. |
      # rpc_method: resource.name == "rpc", resource.instance != "" or id < 32768
      | rpc_method      | False       | Uri is missing uSoftware Entity name. |
      | is_empty        | False       |                            |

      # is_resolved == is long formed (filled names in uauth, enti, & resrc) and micro formed (existing ids in uauth, enti, & resrc )
      | is_resolved     | False       |                            |
      | is_micro_form   | True        |                            |
      | is_long_form    | False       |                            |

  Scenario Outline: UUri validate random string 3
    Given "uE1" creates data for "uri_deserialize"

    When sends a "uri_deserialize" request with serialized input "///"

    Then receives json with following set fields:
      | protobuf_field_names | protobuf_field_values         | protobuf_field_type |
      | authority.ip         |                               | bytes               |
      | authority.name       |                               | str                 |
      | entity.id            | 0                             | int                 |
      | entity.name          |                               | str                 |
      | entity.version_major | 0                             | int                 |
      | entity.version_minor | 0                             | int                 |
      | resource.name        |                               | str                 |
      | resource.instance    |                               | str                 |
      | resource.message     |                               | str                 |
      | resource.id          | 0                             | int                 |

    When "uE2" creates data for "uri_validate"
    And sets "validation_type" to "<validation_type>"
    And sets "uuri" to previous response data
    And sends "uri_validate" request

    Then receives validation result as "<bool_result>"
    And  receives validation message as "<message_result>"

    Examples:
      | validation_type | bool_result | message_result             |
      | uri             | False       | Uri is missing uSoftware Entity name. |
      # False for now bc default message="" is set, but should be True
      | rpc_response    | False       | Uri is missing uSoftware Entity name. |
      # rpc_method: resource.name == "rpc", resource.instance != "" or id < 32768
      | rpc_method      | False       | Uri is missing uSoftware Entity name. |
      | is_empty        | False       |                            |

      # is_resolved == is long formed (filled names in uauth, enti, & resrc) and micro formed (existing ids in uauth, enti, & resrc )
      | is_resolved     | False       |                            |
      | is_micro_form   | True        |                            |
      | is_long_form    | False       |                            |

  # Tests UriValidator.validate_rpc_method()
  Scenario Outline: UUri validate rpc_method filled entity name, resource name and instance
    Given "uE1" creates data for "uri_deserialize"

    When sends a "uri_deserialize" request with serialized input "/neelam//rpc.echo"

    Then receives json with following set fields:
      | protobuf_field_names | protobuf_field_values         | protobuf_field_type |
      | authority.ip         |                               | bytes               |
      | authority.name       |                               | str                 |
      | entity.id            | 0                             | int                 |
      | entity.name          | neelam                        | str                 |
      | entity.version_major | 0                             | int                 |
      | entity.version_minor | 0                             | int                 |
      | resource.name        | rpc                           | str                 |
      | resource.instance    | echo                          | str                 |
      | resource.message     |                               | str                 |
      | resource.id          | 0                             | int                 |

    When "uE2" creates data for "uri_validate"
    And sets "validation_type" to "<validation_type>"
    And sets "uuri" to previous response data
    And sends "uri_validate" request

    Then receives validation result as "<bool_result>"
    And  receives validation message as "<message_result>"

    Examples:
      | validation_type | bool_result | message_result             |
      | uri             | True        |                            |
      # False for now bc default message="" is set, but should be True
      | rpc_response    | False       | Invalid RPC response type. |
      # rpc_method: resource.name == "rpc", resource.instance != "" or id < 32768
      | rpc_method      | True        |                            |
      | is_empty        | False       |                            |

      # is_resolved == is long formed (filled names in uauth, enti, & resrc) and micro formed (existing ids in uauth, enti, & resrc )
      | is_resolved     | False       |                            |
      | is_micro_form   | True        |                            |
      | is_long_form    | False       |                            |


  Scenario Outline: UUri validate rpc_method as rpc methods 2
    Given "uE1" creates data for "uri_deserialize"

    When sends a "uri_deserialize" request with serialized input "//bo.cloud/petapp/1/rpc.response"

    Then receives json with following set fields:
      | protobuf_field_names | protobuf_field_values         | protobuf_field_type |
      | authority.ip         |                               | bytes               |
      | authority.name       | bo.cloud                      | str                 |
      | entity.id            | 0                             | int                 |
      | entity.name          | petapp                        | str                 |
      | entity.version_major | 1                             | int                 |
      | entity.version_minor | 0                             | int                 |
      | resource.name        | rpc                           | str                 |
      | resource.instance    | response                      | str                 |
      | resource.message     |                               | str                 |
      | resource.id          | 0                             | int                 |

    When "uE2" creates data for "uri_validate"
    And sets "validation_type" to "<validation_type>"
    And sets "uuri" to previous response data
    And sends "uri_validate" request

    Then receives validation result as "<bool_result>"
    And  receives validation message as "<message_result>"

    Examples:
      | validation_type | bool_result | message_result             |
      | uri             | True        |                            |
      # False for now bc default message="" is set, but should be True
      | rpc_response    | False       | Invalid RPC response type. |
      # rpc_method: resource.name == "rpc", resource.instance != "" or id < 32768
      | rpc_method      | True        |                            |
      | is_empty        | False       |                            |

      # is_resolved == is long formed (filled names in uauth, enti, & resrc) and micro formed (existing ids in uauth, enti, & resrc )
      | is_resolved     | True        |                            |
      | is_micro_form   | True        |                            |
      | is_long_form    | True        |                            |

  
   Scenario Outline: UUri validate rpc_method as rpc methods 3
    Given "uE1" creates data for "uri_deserialize"

    When sends a "uri_deserialize" request with serialized input "/petapp//rpc.response"

    Then receives json with following set fields:
      | protobuf_field_names | protobuf_field_values         | protobuf_field_type |
      | authority.ip         |                               | bytes               |
      | authority.name       |                               | str                 |
      | entity.id            | 0                             | int                 |
      | entity.name          | petapp                        | str                 |
      | entity.version_major | 0                             | int                 |
      | entity.version_minor | 0                             | int                 |
      | resource.name        | rpc                           | str                 |
      | resource.instance    | response                      | str                 |
      | resource.message     |                               | str                 |
      | resource.id          | 0                             | int                 |

    When "uE2" creates data for "uri_validate"
    And sets "validation_type" to "<validation_type>"
    And sets "uuri" to previous response data
    And sends "uri_validate" request

    Then receives validation result as "<bool_result>"
    And  receives validation message as "<message_result>"

    Examples:
      | validation_type | bool_result | message_result             |
      | uri             | True        |                            |
      # False for now bc default message="" is set, but should be True
      | rpc_response    | False       | Invalid RPC response type. |
      # rpc_method: resource.name == "rpc", resource.instance != "" or id < 32768
      | rpc_method      | True        |                            |
      | is_empty        | False       |                            |

      # is_resolved == is long formed (filled names in uauth, enti, & resrc) and micro formed (existing ids in uauth, enti, & resrc )
      | is_resolved     | False       |                            |
      | is_micro_form   | True        |                            |
      | is_long_form    | False       |                            |

  Scenario: UUri validate rpc_method, even tho resource.instance == "", resource id < 32768 so still rpc_method
    Given "uE1" creates data for "uri_deserialize"

    When sends a "uri_deserialize" request with serialized input "/petapp/1/rpc"

    Then receives json with following set fields:
      | protobuf_field_names | protobuf_field_values         | protobuf_field_type |
      | authority.ip         |                               | bytes               |
      | authority.name       |                               | str                 |
      | entity.id            | 0                             | int                 |
      | entity.name          | petapp                        | str                 |
      | entity.version_major | 1                             | int                 |
      | entity.version_minor | 0                             | int                 |
      | resource.name        | rpc                           | str                 |
      | resource.instance    |                               | str                 |
      | resource.message     |                               | str                 |
      | resource.id          | 0                             | int                 |

    When "uE2" creates data for "uri_validate"
    And sets "validation_type" to "rpc_method"
    And sets "uuri" to previous response data
    And sends "uri_validate" request

    Then receives validation result as "True"
    And  receives validation message as ""


  # Below is False, BUT should be TRUE! fix until new UUri signature is implemented by June 10ish, 2024
  Scenario: UUri validate is_rpc_response given inputs 
    Given "uE1" creates data for "uri_deserialize"

    When sends a "uri_deserialize" request with serialized input ""

    Then receives json with following set fields:
      | protobuf_field_names | protobuf_field_values         | protobuf_field_type |
      | authority.ip         |                               | bytes               |
      | authority.name       |                               | str                 |
      | entity.id            | 0                             | int                 |
      | entity.name          |                               | str                 |
      | entity.version_major | 0                             | int                 |
      | entity.version_minor | 0                             | int                 |
      | resource.name        |                               | str                 |
      | resource.instance    |                               | str                 |
      | resource.message     |                               | str                 |
      | resource.id          | 0                             | int                 |

    When "uE2" creates data for "uri_validate"
    And sets "validation_type" to "is_empty"
    And sets "uuri" to previous response data
    And sends "uri_validate" request

    Then receives validation result as "False"
    And  receives validation message as ""

