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
Feature: UAttributes Builder publish()

  Scenario Outline: Testing UAttributes Builder's publish()
    Given "<uE1>" creates data for "build_uattribute_publish":
      | protobuf_field_names        | protobuf_field_values         | protobuf_field_type |
      | source.authority.name       | vcu.someVin.veh.sample.gm.com | str                 |
      | source.entity.name          | petapp.sample.gm.com          | str                 |
      | source.entity.version_major | 1                             | int                 |
      | source.resource.name        | rpc                           | str                 |
      | priority                    | UPriority.UPRIORITY_CS1       | int                 |

    When sends "build_uattribute_publish" request

    Then receives json with following set fields: 
      | protobuf_field_names        | protobuf_field_values              | protobuf_field_type |

      | source.authority.name       | vcu.someVin.veh.sample.gm.com      | str                 |
      | source.authority.id         |                                    | bytes               |
      | source.authority.ip         |                                    | bytes               |
      | source.entity.id            | 0                                  | int                 |
      | source.entity.name          | petapp.sample.gm.com               | str                 |
      | source.entity.version_major | 1                                  | int                 |
      | source.entity.version_minor | 0                                  | int                 |
      | source.resource.id          | 0                                  | int                 |
      | source.resource.name        | rpc                                | str                 |
      | source.resource.instance    |                                    | str                 |
      | source.resource.message     |                                    | str                 |

      | sink.authority.name         |                                    | str                 |
      | sink.authority.id           |                                    | bytes               |
      | sink.authority.ip           |                                    | bytes               |
      | sink.entity.id              | 0                                  | int                 |
      | sink.entity.name            |                                    | str                 |
      | sink.entity.version_major   | 0                                  | int                 |
      | sink.entity.version_minor   | 0                                  | int                 |
      | sink.resource.id            | 0                                  | int                 |
      | sink.resource.name          |                                    | str                 |
      | sink.resource.instance      |                                    | str                 |
      | sink.resource.message       |                                    | str                 |

      | priority                    | UPriority.UPRIORITY_CS1            | int                 |
      | type                        | UMessageType.UMESSAGE_TYPE_PUBLISH | int                 |
      | ttl                         | 0                                  | int                 |

    Examples:
    | uE1    | 
    | python | 
    | java   | 
  
  Scenario Outline: Testing UAttributes Builder's publish() with dataset 2
    Given "<uE1>" creates data for "build_uattribute_publish":
      | protobuf_field_names        | protobuf_field_values         | protobuf_field_type |
      | source.authority.ip         | ipaddress.ip.ip.address       | bytes               |
      | source.authority.name       | authority_name_nameName       | str                 |
      | source.entity.id            | 101                           | int                 |
      | source.entity.name          | name of entity                | str                 |
      | source.entity.version_major | 64                            | int                 |
      | source.entity.version_minor | 32                            | int                 |
      | source.resource.name        | resource name                 | str                 |
      | source.resource.instance    | resource instance             | str                 |
      | source.resource.message     | message of resource           | str                 |
      | source.resource.id          | 5                             | int                 |

      | priority                    | UPriority.UPRIORITY_UNSPECIFIED| int                 |

    When sends "build_uattribute_publish" request

    Then receives json with following set fields: 
      | protobuf_field_names        | protobuf_field_values              | protobuf_field_type |

      | source.authority.name       | authority_name_nameName            | str                 |
      | source.authority.id         |                                    | bytes               |
      | source.authority.ip         | ipaddress.ip.ip.address            | bytes               |
      | source.entity.id            | 101                                | int                 |
      | source.entity.name          | name of entity                     | str                 |
      | source.entity.version_major | 64                                 | int                 |
      | source.entity.version_minor | 32                                 | int                 |
      | source.resource.name        | resource name                      | str                 |
      | source.resource.instance    | resource instance                  | str                 |
      | source.resource.message     | message of resource                | str                 |
      | source.resource.id          | 5                                  | int                 |

      | sink.authority.name         |                                    | str                 |
      | sink.authority.id           |                                    | bytes               |
      | sink.authority.ip           |                                    | bytes               |
      | sink.entity.id              | 0                                  | int                 |
      | sink.entity.name            |                                    | str                 |
      | sink.entity.version_major   | 0                                  | int                 |
      | sink.entity.version_minor   | 0                                  | int                 |
      | sink.resource.id            | 0                                  | int                 |
      | sink.resource.name          |                                    | str                 |
      | sink.resource.instance      |                                    | str                 |
      | sink.resource.message       |                                    | str                 |

      | priority                    | UPriority.UPRIORITY_UNSPECIFIED    | int                 |
      | type                        | UMessageType.UMESSAGE_TYPE_PUBLISH | int                 |
      | ttl                         | 0                                  | int                 |

    Examples:
    | uE1    | 
    | python | 
    | java   | 
    
  
  Scenario Outline: Testing UAttributes Builder's publish() with additional parameters
    Given "<uE1>" creates data for "build_uattribute_publish":
      | protobuf_field_names        | protobuf_field_values         | protobuf_field_type |

      | source.authority.name       | vcu.someVin.veh.sample.gm.com | str                 |
      | source.entity.name          | petapp.sample.gm.com          | str                 |
      | source.entity.version_major | 1                             | int                 |
      | source.resource.name        | rpc                           | str                 |

      | priority                    | UPriority.UPRIORITY_CS1       | int                 |
      | ttl                         | 100                           | int                 |
      | token                       | test_token                    | str                 |

      | sink.authority.name         | vcu.someVin.veh.sample.gm.com | str                 |
      | sink.entity.name            | petapp.sample.gm.com          | str                 |
      | sink.entity.version_major   | 1                             | int                 |
      | sink.resource.name          | rpc                           | str                 |

      | plevel                      | 2                             | int                 |
      | commstatus                  | UCode.CANCELLED               | int                 |
      | reqid.msb                   | 12345                         | int                 |
      | reqid.lsb                   | 54321                         | int                 |
      | traceparent                 | test_traceparent              | str                 |

    When sends "build_uattribute_publish" request

    Then receives json with following set fields: 
      | protobuf_field_names        | protobuf_field_values              | protobuf_field_type |

      | source.authority.name       | vcu.someVin.veh.sample.gm.com      | str                 |
      | source.authority.id         |                                    | bytes               |
      | source.authority.ip         |                                    | bytes               |
      | source.entity.id            | 0                                  | int                 |
      | source.entity.name          | petapp.sample.gm.com               | str                 |
      | source.entity.version_major | 1                                  | int                 |
      | source.entity.version_minor | 0                                  | int                 |
      | source.resource.id          | 0                                  | int                 |
      | source.resource.name        | rpc                                | str                 |
      | source.resource.instance    |                                    | str                 |
      | source.resource.message     |                                    | str                 |

      | sink.authority.name         | vcu.someVin.veh.sample.gm.com      | str                 |
      | sink.authority.id           |                                    | bytes               |
      | sink.authority.ip           |                                    | bytes               |
      | sink.entity.id              | 0                                  | int                 |
      | sink.entity.name            | petapp.sample.gm.com               | str                 |
      | sink.entity.version_major   | 1                                  | int                 |
      | sink.entity.version_minor   | 0                                  | int                 |
      | sink.resource.id            | 0                                  | int                 |
      | sink.resource.name          | rpc                                | str                 |
      | sink.resource.instance      |                                    | str                 |
      | sink.resource.message       |                                    | str                 |

      | priority                    | UPriority.UPRIORITY_CS1            | int                 |
      | type                        | UMessageType.UMESSAGE_TYPE_PUBLISH | int                 |
      | ttl                         | 100                                | int                 |
      | token                       | test_token                         | str                 |

      | permission_level            | 2                                  | int                 |
      | commstatus                  | 1                                  | int                 |
      | reqid.msb                   | 12345                              | int                 |
      | reqid.lsb                   | 54321                              | int                 |
      | traceparent                 | test_traceparent                   | str                 |

    Examples:
    | uE1    | 
    | python | 
    | java   | 
  
  Scenario Outline: Testing UAttributes Builder's publish() when attribute field does not exist
    Given "<uE1>" creates data for "build_uattribute_publish":
      | protobuf_field_names        | protobuf_field_values         | protobuf_field_type |
      | source.authority.name       | vcu.someVin.veh.sample.gm.com | str                 |
      | source.entity.name          | petapp.sample.gm.com          | str                 |
      | source.resource.name        | rpc                           | str                 |
      | priority                    | UPriority.UPRIORITY_CS1       | int                 |

      | nonexistant_field           | pretend_value                 | str                 |
      | source.nonexistant_field    | source_pretend_value          | str                 |
      | sink.nonexistant_field      | sink_pretend_value            | str                 |
      | sink.no.nonexistant_field   | sink_pretend_value            | str                 |
      | reqid.nonexistant_field     | reqi_pretend_value            | str                 |
      | reqid.no.nonexistant_field  | reqi_pretend_value            | str                 |

    When sends "build_uattribute_publish" request

    Then receives json with following set fields: 
      | protobuf_field_names        | protobuf_field_values              | protobuf_field_type |

      | source.authority.name       | vcu.someVin.veh.sample.gm.com      | str                 |
      | source.authority.id         |                                    | bytes               |
      | source.authority.ip         |                                    | bytes               |
      | source.entity.id            | 0                                  | int                 |
      | source.entity.name          | petapp.sample.gm.com               | str                 |
      | source.entity.version_major | 0                                  | int                 |
      | source.entity.version_minor | 0                                  | int                 |
      | source.resource.id          | 0                                  | int                 |
      | source.resource.name        | rpc                                | str                 |
      | source.resource.instance    |                                    | str                 |
      | source.resource.message     |                                    | str                 |

      | sink.authority.name         |                                    | str                 |
      | sink.authority.id           |                                    | bytes               |
      | sink.authority.ip           |                                    | bytes               |
      | sink.entity.id              | 0                                  | int                 |
      | sink.entity.name            |                                    | str                 |
      | sink.entity.version_major   | 0                                  | int                 |
      | sink.entity.version_minor   | 0                                  | int                 |
      | sink.resource.id            | 0                                  | int                 |
      | sink.resource.name          |                                    | str                 |
      | sink.resource.instance      |                                    | str                 |
      | sink.resource.message       |                                    | str                 |

      | priority                    | UPriority.UPRIORITY_CS1            | int                 |
      | type                        | UMessageType.UMESSAGE_TYPE_PUBLISH | int                 |
      | ttl                         | 0                                  | int                 |

    Examples:
    | uE1    | 
    | python | 
    | java   | 
  
  Scenario Outline: Testing UAttributes Builder's publish() when proto attribute field is set to incorrect data type 0
    Given "<uE1>" creates data for "build_uattribute_publish":
      | protobuf_field_names        | protobuf_field_values         | protobuf_field_type |
      | source.authority.id         | supposed to be bytes          | str                 |
      | priority                    | 2                             | int                 |

    When sends "build_uattribute_publish" request

    Then receives json with following set fields: 
      | protobuf_field_names | protobuf_field_values              | protobuf_field_type |

      |                      | ERROR: data type misalignment in "source" uAttribute field assignment| str                 |

    Examples:
    | uE1    | 
    | python | 
    | java   | 
  
  Scenario Outline: Testing UAttributes Builder's publish() when proto attribute field is set to incorrect data type 1
    Given "<uE1>" creates data for "build_uattribute_publish":
      | protobuf_field_names        | protobuf_field_values         | protobuf_field_type |
      | source.authority.name       | 101                           | int                 |
      | priority                    | 2                             | int                 |

    When sends "build_uattribute_publish" request

    Then receives json with following set fields: 
      | protobuf_field_names | protobuf_field_values              | protobuf_field_type |

      |                      | ERROR: data type misalignment in "source" uAttribute field assignment| str                 |

    Examples:
    | uE1    | 
    | python | 
    | java   | 

  Scenario Outline: Testing UAttributes Builder's publish() when proto attribute field is set to incorrect data type 2
    Given "<uE1>" creates data for "build_uattribute_publish":
      | protobuf_field_names        | protobuf_field_values         | protobuf_field_type |
      | source.entity.name          | 102                           | int                 |
      | priority                    | 2                             | int                 |

    When sends "build_uattribute_publish" request

    Then receives json with following set fields: 
      | protobuf_field_names | protobuf_field_values              | protobuf_field_type |

      |                      | ERROR: data type misalignment in "source" uAttribute field assignment| str                 |

    Examples:
    | uE1    | 
    | python | 
    | java   | 

  Scenario Outline: Testing UAttributes Builder's publish() when proto attribute field is set to incorrect data type 3
    Given "<uE1>" creates data for "build_uattribute_publish":
      | protobuf_field_names        | protobuf_field_values         | protobuf_field_type |
      | source.entity.version_major | supposed to be int            | bytes                |
      | priority                    | 2                             | int                 |

    When sends "build_uattribute_publish" request

    Then receives json with following set fields: 
      | protobuf_field_names | protobuf_field_values              | protobuf_field_type |

      |                      | ERROR: data type misalignment in "source" uAttribute field assignment| str                 |

    Examples:
    | uE1    | 
    | python | 
    | java   | 

  
  Scenario Outline: Testing UAttributes Builder's publish() when proto attribute field is set to incorrect data type 4
    Given "<uE1>" creates data for "build_uattribute_publish":
      | protobuf_field_names        | protobuf_field_values         | protobuf_field_type |
      | source.resource.name        | 103                           | int                 |
      | priority                    | 2                             | int                 |

    When sends "build_uattribute_publish" request

    Then receives json with following set fields: 
      | protobuf_field_names | protobuf_field_values              | protobuf_field_type |

      |                      | ERROR: data type misalignment in "source" uAttribute field assignment| str                 |

    Examples:
    | uE1    | 
    | python | 
    | java   | 
  
  Scenario Outline: Testing UAttributes Builder's publish() when proto attribute field is set to incorrect data type 5
    Given "<uE1>" creates data for "build_uattribute_publish":
      | protobuf_field_names        | protobuf_field_values         | protobuf_field_type |
      | source.resource.name        | name                          | str                 |
      | priority                    | 2                             | int                 |

      | sink.authority.name         | 5.5555                        | float               |

    When sends "build_uattribute_publish" request

    Then receives json with following set fields: 
      | protobuf_field_names | protobuf_field_values              | protobuf_field_type |

      |                      | ERROR: data type misalignment in "sink" uAttribute field assignment| str                 |

    Examples:
    | uE1    | 
    | python | 
    | java   | 
  
  Scenario Outline: Testing UAttributes Builder's publish() when proto attribute field is set to incorrect data type 6
    Given "<uE1>" creates data for "build_uattribute_publish":
      | protobuf_field_names        | protobuf_field_values         | protobuf_field_type |
      | source.resource.name        | name                          | str                 |
      | priority                    | 2                             | int                 |

      | sink.entity.name            | 102                           | int                 |

    When sends "build_uattribute_publish" request

    Then receives json with following set fields: 
      | protobuf_field_names | protobuf_field_values              | protobuf_field_type |

      |                      | ERROR: data type misalignment in "sink" uAttribute field assignment| str                 |

    Examples:
    | uE1    | 
    | python | 
    | java   | 
  
  Scenario Outline: Testing UAttributes Builder's publish() when proto attribute field is set to incorrect data type 7
    Given "<uE1>" creates data for "build_uattribute_publish":
      | protobuf_field_names        | protobuf_field_values         | protobuf_field_type |
      | source.resource.name        | name                          | str                 |
      | priority                    | 2                             | int                 |

      | sink.entity.version_major   | supposed to be int            | str                 |

    When sends "build_uattribute_publish" request

    Then receives json with following set fields: 
      | protobuf_field_names | protobuf_field_values              | protobuf_field_type |

      |                      | ERROR: data type misalignment in "sink" uAttribute field assignment| str                 |

    Examples:
    | uE1    | 
    | python | 
    | java   | 

  Scenario Outline: Testing UAttributes Builder's publish() when proto attribute field is set to incorrect data type 8
    Given "<uE1>" creates data for "build_uattribute_publish":
      | protobuf_field_names        | protobuf_field_values         | protobuf_field_type |
      | source.resource.name        | name                          | str                 |
      | priority                    | 2                             | int                 |

      | reqid.msb                   | supposed to be int            | str                 |

    When sends "build_uattribute_publish" request

    Then receives json with following set fields: 
      | protobuf_field_names | protobuf_field_values              | protobuf_field_type |

      |                      | ERROR: data type misalignment in "reqid" uAttribute field assignment| str                 |

    Examples:
    | uE1    | 
    | python | 
    | java   | 
  
  Scenario Outline: Testing UAttributes Builder's publish() when primitive attribute field is set to incorrect data type 1
    Given "<uE1>" creates data for "build_uattribute_publish":
      | protobuf_field_names        | protobuf_field_values         | protobuf_field_type |
      | source.authority.name       | vcu.someVin.veh.sample.gm.com | str                 |
      | priority                    | UPriority.UPRIORITY_CS1       | int                 |
      | ttl                         | supposed to be int            | str                 | 

    When sends "build_uattribute_publish" request

    Then receives json with following set fields: 
      | protobuf_field_names | protobuf_field_values              | protobuf_field_type |

      |                      | ERROR: data type misalignment in "ttl" uAttribute field assignment   | str                 |

    Examples:
    | uE1    | 
    | python | 
    | java   | 

  
  Scenario Outline: Testing UAttributes Builder's publish() when primitive attribute field is set to incorrect data type 2
    Given "<uE1>" creates data for "build_uattribute_publish":
      | protobuf_field_names        | protobuf_field_values         | protobuf_field_type |
      | source.authority.name       | vcu.someVin.veh.sample.gm.com | str                 |
      | priority                    | UPriority.UPRIORITY_CS1       | int                 |

      | plevel                      | supposed to be int            | bytes                 |

    When sends "build_uattribute_publish" request

    Then receives json with following set fields: 
      | protobuf_field_names | protobuf_field_values              | protobuf_field_type |

      |                      | ERROR: data type misalignment in "plevel" uAttribute field assignment   | str                 |

    Examples:
    | uE1    | 
    | python | 
    | java   | 


  Scenario Outline: Testing UAttributes Builder's publish() when primitive attribute field is set to incorrect data value/range
    Given "<uE1>" creates data for "build_uattribute_publish":
      | protobuf_field_names        | protobuf_field_values         | protobuf_field_type |
      | source.authority.name       | vcu.someVin.veh.sample.gm.com | str                 |
      | priority                    | UPriority.UPRIORITY_CS1       | int                 |

      | commstatus                  | -10                           | int                 |

    When sends "build_uattribute_publish" request

    Then receives json with following set fields: 
      | protobuf_field_names | protobuf_field_values              | protobuf_field_type |

      |                      | ERROR: "commstatus" field must be int between [0, 16] | str                 |

    Examples:
    | uE1    | 
    | python | 
    | java   | 

  Scenario Outline: Testing UAttributes Builder's publish() when primitive attribute field is set to incorrect data type 3
    Given "<uE1>" creates data for "build_uattribute_publish":
      | protobuf_field_names        | protobuf_field_values         | protobuf_field_type |
      | source.authority.name       | vcu.someVin.veh.sample.gm.com | str                 |
      | priority                    | UPriority.UPRIORITY_CS1       | int                 |

      # was str
      | traceparent                 | 777                           | int                 |  

    When sends "build_uattribute_publish" request

    Then receives json with following set fields: 
      | protobuf_field_names | protobuf_field_values              | protobuf_field_type |

      |                      | ERROR: data type misalignment in "traceparent" uAttribute field assignment   | str                 |

    Examples:
    | uE1    | 
    | python | 
    | java   | 

  Scenario Outline: Testing UAttributes Builder's publish() when primitive attribute field is set to incorrect data type but works
    Given "<uE1>" creates data for "build_uattribute_publish":
      | protobuf_field_names        | protobuf_field_values         | protobuf_field_type |
      | source.authority.name       | vcu.someVin.veh.sample.gm.com | str                 |
      | priority                    | UPriority.UPRIORITY_CS1       | int                 |

      | ttl                         | -10                           | int                 |

    When sends "build_uattribute_publish" request

    Then receives json with following set fields: 
      | protobuf_field_names | protobuf_field_values              | protobuf_field_type |

      |                      | ERROR: same data type but bad value in "ttl" uAttribute field assignment | str                 |

    Examples:
    | uE1    | 
    | python | 
    | java   | 

  
  Scenario Outline: Testing UAttributes Builder's publish() with no source UUri set
    Given "<uE1>" creates data for "build_uattribute_publish":
      | protobuf_field_names        | protobuf_field_values         | protobuf_field_type |
      | priority                    | UPriority.UPRIORITY_CS1       | int                 |

    When sends "build_uattribute_publish" request

    Then receives json with following set fields: 
      | protobuf_field_names | protobuf_field_values              | protobuf_field_type |

      |                      | ERROR: "source" field must exist   | str                 |

    Examples:
    | uE1    | 
    | python | 
    | java   | 
  
  Scenario Outline: Testing UAttributes Builder's publish() with bad priority set
    Given "<uE1>" creates data for "build_uattribute_publish":
      | protobuf_field_names        | protobuf_field_values         | protobuf_field_type |
      | source.authority.name       | vcu.someVin.veh.sample.gm.com | str                 |
      | priority                    | 1000                          | int                 |

    When sends "build_uattribute_publish" request

    Then receives json with following set fields: 
      | protobuf_field_names | protobuf_field_values              | protobuf_field_type |

      |                      | ERROR: "priority" field must be int between [0, 7]  | str                 |

    Examples:
    | uE1    | 
    | python | 
    | java   | 

    Scenario Outline: Testing UAttributes Builder's publish() with no priority set
    Given "<uE1>" creates data for "build_uattribute_publish":
      | protobuf_field_names        | protobuf_field_values         | protobuf_field_type |
      | source.authority.name       | vcu.someVin.veh.sample.gm.com | str                 |

    When sends "build_uattribute_publish" request

    Then receives json with following set fields: 
      | protobuf_field_names | protobuf_field_values              | protobuf_field_type |

      |                      | ERROR: "priority" field must exist   | str                 |

    Examples:
    | uE1    | 
    | python | 
    | java   | 
  
  Scenario Outline: Testing UAttributes Builder's publish() with wrong depth protobuf's field assignment 
    Given "<uE1>" creates data for "build_uattribute_publish":
      | protobuf_field_names        | protobuf_field_values         | protobuf_field_type |
      | source                      | wrong assignment              | str                 |
      | priority                    | UPriority.UPRIORITY_CS1       | int                 |

    When sends "build_uattribute_publish" request

    Then receives json with following set fields: 
      | protobuf_field_names | protobuf_field_values              | protobuf_field_type |

      |                      | ERROR: data type misalignment in "source" uAttribute field assignment  | str                 |

    Examples:
    | uE1    | 
    | python | 
    | java   | 

  Scenario Outline: Testing UAttributes Builder's publish() with wrong depth protobuf's field assignment 
    Given "<uE1>" creates data for "build_uattribute_publish":
      | protobuf_field_names        | protobuf_field_values         | protobuf_field_type |
      | source.authority.name       | vcu.someVin.veh.sample.gm.com | str                 |
      | priority                    | UPriority.UPRIORITY_CS1       | int                 |
      | sink.authority              | wrong assignment              | str                 |

    When sends "build_uattribute_publish" request

    Then receives json with following set fields: 
      | protobuf_field_names | protobuf_field_values              | protobuf_field_type |

      |                      | ERROR: data type misalignment in "sink" uAttribute field assignment  | str                 |

    Examples:
    | uE1    | 
    | python | 
    | java   | 
  