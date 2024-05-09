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

  Scenario Outline: Validate different types of URIs
    Given "uE1" creates data for "uri_validate"
      And sets "uri" to "<uri>"
      And sets "type" to "<validation_type>"

    When sends "uri_validate" request
      Then receives validation result as "<expected_status>"
      And  receives validation message as "<expected_message>"

    Examples:
        | uri                                                 | validation_type          | expected_status| expected_message             | 
        |                                                     | uri                      | False          | Uri is empty.                |
        | //                                                  | uri                      | False          | Uri is empty.                |
        | /neelam                                             | uri                      | True           | none                         |
        | neelam                                              | uri                      | False          | Uri is empty.                |
        | /neelam//rpc.echo                                   | rpc_method               | True           | none                         |
        | /neelam/echo                                        | rpc_method               | False          | Uri is empty.                |
        | neelam                                              | rpc_method               | False          | Uri is empty.                |
        | /neelam//rpc.response                               | rpc_response             | True           | none                         |
        | neelam                                              | rpc_response             | False          | Uri is empty.                |
        | /neelam//dummy.wrong                                | rpc_response             | False          | Invalid RPC response type.   |
        | //VCU.MY_CAR_VIN/body.access/1/door.front_left#Door | uri                      | True           | none                         |
        | //VCU.MY_CAR_VIN/body.access//door.front_left#Door  | uri                      | True           | none                         |
        | /body.access/1/door.front_left#Door                 | uri                      | True           | none                         |
        | /body.access//door.front_left#Door                  | uri                      | True           | none                         |
        | :                                                   | uri                      | False          | none                         |
        | /                                                   | uri                      | False          | none                         |
        | //                                                  | uri                      | False          | none                         |
        | ///body.access/1/door.front_left#Door               | uri                      | False          | none                         |
        | //VCU.myvin///door.front_left#Door                  | uri                      | False          | none                         |
        | /1/door.front_left#Door                             | uri                      | False          | none                         |
        | //VCU.myvin//1                                      | uri                      | False          | none                         |
        | //bo.cloud/petapp/1/rpc.response                    | rpc_method               | True           | none                         |
        | //bo.cloud/petapp//rpc.response                     | rpc_method               | True           | none                         |
        | /petapp/1/rpc.response                              | rpc_method               | True           | none                         |
        | /petapp//rpc.response                               | rpc_method               | True           | none                         |
        | :                                                   | rpc_method               | False          | none                         |
        | /petapp/1/dog                                       | rpc_method               | False          | none                         |
        | //petapp/1/dog                                      | rpc_method               | False          | none                         |
        | //                                                  | rpc_method               | False          | none                         |
        | ///body.access/1                                    | rpc_method               | False          | none                         |
        | //VCU.myvin                                         | rpc_method               | False          | none                         |
        | /1                                                  | rpc_method               | False          | none                         |
        | //VCU.myvin//1                                      | rpc_method               | False          | none                         |
        | //VCU.myvin/body.access/1/rpc.UpdateDoor            | rpc_method               | True           | none                         |
        | //VCU.myvin/body.access//rpc.UpdateDoor             | rpc_method               | True           | none                         |
        | /body.access/1/rpc.UpdateDoor                       | rpc_method               | True           | none                         |
        | /body.access//rpc.UpdateDoor                        | rpc_method               | True           | none                         |
        | ///body.access/1/rpc.UpdateDoor                     | rpc_method               | False          | none                         |
        | /1/rpc.UpdateDoor                                   | rpc_method               | False          | none                         |
        | //VCU.myvin//1/rpc.UpdateDoor                       | rpc_method               | False          | none                         |
        | /hartley                                            | uri                      | True           | none                         |
        | /hartley//                                          | uri                      | True           | none                         |
        | /hartley/0                                          | uri                      | True           | none                         |
        | /1                                                  | uri                      | True           | none                         |
        | /body.access/1                                      | uri                      | True           | none                         |
        | /body.access/1/door.front_left#Door                 | uri                      | True           | none                         |
        | //vcu.vin/body.access/1/door.front_left#Door        | uri                      | True           | none                         |
        | /body.access/1/rpc.OpenWindow                       | uri                      | True           | none                         |
        | /body.access/1/rpc.response                         | uri                      | True           | none                         |
        |                                                     | uri                      | False          | Uri is empty.                |
        | :                                                   | uri                      | False          | Uri is empty.                |
        | ///                                                 | uri                      | False          | Uri is empty.                |
        | ////                                                | uri                      | False          | Uri is empty.                |
        | 1                                                   | uri                      | False          | Uri is empty.                |
        | a                                                   | uri                      | False          | Uri is empty.                |
        | /petapp/1/rpc.OpenWindow                            | rpc_method               | True           | none                         |
        | /petapp/1/rpc.response                              | rpc_method               | True           | none                         |
        | /petapp/1/rpc.response                              | rpc_response             | True           | none                         |
        | /petapp/1/rpc.OpenWindow                            | rpc_response             | False          | none                         |
        | /petapp//                                           | rpc_method               | False          | none                         |
        | /petapp                                             | rpc_method               | False          | none                         |
        | /petapp/1/                                          | rpc_method               | False          | none                         |
        | /petapp/1/rpc                                       | rpc_method               | False          | none                         |
        | /petapp/1/dummy                                     | rpc_method               | False          | none                         |
        | /petapp/1/rpc_dummy                                 | rpc_method               | False          | none                         |
        |                                                     | is_empty                 | True           | none                         |
        | /hartley/23/rpc.echo                                | is_resolved              | False          | none                         |
        |                                                     | is_micro_form            | False          | none                         |
        | /hartley/23/                                        | is_micro_form            | False          | none                         |
        |                                                     | is_long_form_uuri        | False          | none                         |
        |                                                     | is_long_form_uauthority  | False          | none                         |
        | /hartley/23/                                        | is_long_form_uuri        | False          | none                         |
        | //vcu.veh.com/hartley/23/                           | is_long_form_uuri        | False          | none                         |
        | ///hartley/23/                                      | is_long_form_uuri        | False          | none                         |
        | ///hartley/23/                                      | is_long_form_uauthority  | False          | none                         |
        |                                                     | is_micro_form            | False          | none                         |
        | ///hartley/23/                                      | is_micro_form            | False          | none                         |