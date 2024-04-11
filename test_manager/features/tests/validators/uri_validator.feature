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
    Given "<sdk_name>" creates data for "uri_validate"
    And sets "uri" to "<uri>"
    And sets "type" to "<validation_type>"
    When sends "uri_validate" request
    And user waits "1" second
    Then "<sdk_name>" receives validation result as "<expected_status>"
    And "<sdk_name>" receives validation message as "<expected_message>"

    Examples:
        |sdk_name| uri                                                 | validation_type          | expected_status| expected_message             | 
        | java   |                                                     | uri                      | False          | Uri is empty.                |
        | java   | //                                                  | uri                      | False          | Uri is empty.                |
        | java   | /neelam                                             | uri                      | True           | none                         |
        | java   | neelam                                              | uri                      | False          | Uri is empty.                |
        | java   | /neelam//rpc.echo                                   | rpc_method               | True           | none                         |
        | java   | /neelam/echo                                        | rpc_method               | False          | Uri is empty.                |
        | java   | neelam                                              | rpc_method               | False          | Uri is empty.                |
        | java   | /neelam//rpc.response                               | rpc_response             | True           | none                         |
        | java   | neelam                                              | rpc_response             | False          | Uri is empty.                |
        | java   | /neelam//dummy.wrong                                | rpc_response             | False          | Invalid RPC response type.   |
        | java   | //VCU.MY_CAR_VIN/body.access/1/door.front_left#Door | uri                      | True           | none                         |
        | java   | //VCU.MY_CAR_VIN/body.access//door.front_left#Door  | uri                      | True           | none                         |
        | java   | /body.access/1/door.front_left#Door                 | uri                      | True           | none                         |
        | java   | /body.access//door.front_left#Door                  | uri                      | True           | none                         |
        | java   | :                                                   | uri                      | False          | none                         |
        | java   | /                                                   | uri                      | False          | none                         |
        | java   | //                                                  | uri                      | False          | none                         |
        | java   | ///body.access/1/door.front_left#Door               | uri                      | False          | none                         |
        | java   | //VCU.myvin///door.front_left#Door                  | uri                      | False          | none                         |
        | java   | /1/door.front_left#Door                             | uri                      | False          | none                         |
        | java   | //VCU.myvin//1                                      | uri                      | False          | none                         |
        | java   | //bo.cloud/petapp/1/rpc.response                    | rpc_method               | True           | none                         |
        | java   | //bo.cloud/petapp//rpc.response                     | rpc_method               | True           | none                         |
        | java   | /petapp/1/rpc.response                              | rpc_method               | True           | none                         |
        | java   | /petapp//rpc.response                               | rpc_method               | True           | none                         |
        | java   | :                                                   | rpc_method               | False          | none                         |
        | java   | /petapp/1/dog                                       | rpc_method               | False          | none                         |
        | java   | //petapp/1/dog                                      | rpc_method               | False          | none                         |
        | java   | //                                                  | rpc_method               | False          | none                         |
        | java   | ///body.access/1                                    | rpc_method               | False          | none                         |
        | java   | //VCU.myvin                                         | rpc_method               | False          | none                         |
        | java   | /1                                                  | rpc_method               | False          | none                         |
        | java   | //VCU.myvin//1                                      | rpc_method               | False          | none                         |
        | java   | //VCU.myvin/body.access/1/rpc.UpdateDoor            | rpc_method               | True           | none                         |
        | java   | //VCU.myvin/body.access//rpc.UpdateDoor             | rpc_method               | True           | none                         |
        | java   | /body.access/1/rpc.UpdateDoor                       | rpc_method               | True           | none                         |
        | java   | /body.access//rpc.UpdateDoor                        | rpc_method               | True           | none                         |
        | java   | ///body.access/1/rpc.UpdateDoor                     | rpc_method               | False          | none                         |
        | java   | /1/rpc.UpdateDoor                                   | rpc_method               | False          | none                         |
        | java   | //VCU.myvin//1/rpc.UpdateDoor                       | rpc_method               | False          | none                         |
        | java   | /hartley                                            | uri                      | True           | none                         |
        | java   | /hartley//                                          | uri                      | True           | none                         |
        | java   | /hartley/0                                          | uri                      | True           | none                         |
        | java   | /1                                                  | uri                      | True           | none                         |
        | java   | /body.access/1                                      | uri                      | True           | none                         |
        | java   | /body.access/1/door.front_left#Door                 | uri                      | True           | none                         |
        | java   | //vcu.vin/body.access/1/door.front_left#Door        | uri                      | True           | none                         |
        | java   | /body.access/1/rpc.OpenWindow                       | uri                      | True           | none                         |
        | java   | /body.access/1/rpc.response                         | uri                      | True           | none                         |
        | java   |                                                     | uri                      | False          | Uri is empty.                |
        | java   | :                                                   | uri                      | False          | Uri is empty.                |
        | java   | ///                                                 | uri                      | False          | Uri is empty.                |
        | java   | ////                                                | uri                      | False          | Uri is empty.                |
        | java   | 1                                                   | uri                      | False          | Uri is empty.                |
        | java   | a                                                   | uri                      | False          | Uri is empty.                |
        | java   | /petapp/1/rpc.OpenWindow                            | rpc_method               | True           | none                         |
        | java   | /petapp/1/rpc.response                              | rpc_method               | True           | none                         |
        | java   | /petapp/1/rpc.response                              | rpc_response             | True           | none                         |
        | java   | /petapp/1/rpc.OpenWindow                            | rpc_response             | False          | none                         |
        | java   | /petapp//                                           | rpc_method               | False          | none                         |
        | java   | /petapp                                             | rpc_method               | False          | none                         |
        | java   | /petapp/1/                                          | rpc_method               | False          | none                         |
        | java   | /petapp/1/rpc                                       | rpc_method               | False          | none                         |
        | java   | /petapp/1/dummy                                     | rpc_method               | False          | none                         |
        | java   | /petapp/1/rpc_dummy                                 | rpc_method               | False          | none                         |
        | java   |                                                     | is_empty                 | True           | none                         |
        | java   | /hartley/23/rpc.echo                                | is_resolved              | False          | none                         |
        | java   |                                                     | is_micro_form            | False          | none                         |
        | java   | /hartley/23/                                        | is_micro_form            | False          | none                         |
        | java   |                                                     | is_long_form_uuri        | False          | none                         |
        | java   |                                                     | is_long_form_uauthority  | False          | none                         |
        | java   | /hartley/23/                                        | is_long_form_uuri        | False          | none                         |
        | java   | //vcu.veh.gm.com/hartley/23/                        | is_long_form_uuri        | False          | none                         |
        | java   | ///hartley/23/                                      | is_long_form_uuri        | False          | none                         |
        | java   | ///hartley/23/                                      | is_long_form_uauthority  | False          | none                         |
        | java   |                                                     | is_micro_form            | False          | none                         |
        | java   | ///hartley/23/                                      | is_micro_form            | False          | none                         |
        | python |                                                     | uri                      | False          | Uri is empty.                |
        | python | //                                                  | uri                      | False          | Uri is empty.                |
        | python | /neelam                                             | uri                      | True           | none                         |
        | python | neelam                                              | uri                      | False          | Uri is empty.                |
        | python | /neelam//rpc.echo                                   | rpc_method               | True           | none                         |
        | python | /neelam/echo                                        | rpc_method               | False          | Uri is empty.                |
        | python | neelam                                              | rpc_method               | False          | Uri is empty.                |
        | python | /neelam//rpc.response                               | rpc_response             | True           | none                         |
        | python | neelam                                              | rpc_response             | False          | Uri is empty.                |
        | python | /neelam//dummy.wrong                                | rpc_response             | False          | Invalid RPC response type.   |
        | python | //VCU.MY_CAR_VIN/body.access/1/door.front_left#Door | uri                      | True           | none                         |
        | python | //VCU.MY_CAR_VIN/body.access//door.front_left#Door  | uri                      | True           | none                         |
        | python | /body.access/1/door.front_left#Door                 | uri                      | True           | none                         |
        | python | /body.access//door.front_left#Door                  | uri                      | True           | none                         |
        | python | :                                                   | uri                      | False          | none                         |
        | python | /                                                   | uri                      | False          | none                         |
        | python | //                                                  | uri                      | False          | none                         |
        | python | ///body.access/1/door.front_left#Door               | uri                      | False          | none                         |
        | python | //VCU.myvin///door.front_left#Door                  | uri                      | False          | none                         |
        | python | /1/door.front_left#Door                             | uri                      | False          | none                         |
        | python | //VCU.myvin//1                                      | uri                      | False          | none                         |
        | python | //bo.cloud/petapp/1/rpc.response                    | rpc_method               | True           | none                         |
        | python | //bo.cloud/petapp//rpc.response                     | rpc_method               | True           | none                         |
        | python | /petapp/1/rpc.response                              | rpc_method               | True           | none                         |
        | python | /petapp//rpc.response                               | rpc_method               | True           | none                         |
        | python | :                                                   | rpc_method               | False          | none                         |
        | python | /petapp/1/dog                                       | rpc_method               | False          | none                         |
        | python | //petapp/1/dog                                      | rpc_method               | False          | none                         |
        | python | //                                                  | rpc_method               | False          | none                         |
        | python | ///body.access/1                                    | rpc_method               | False          | none                         |
        | python | //VCU.myvin                                         | rpc_method               | False          | none                         |
        | python | /1                                                  | rpc_method               | False          | none                         |
        | python | //VCU.myvin//1                                      | rpc_method               | False          | none                         |
        | python | //VCU.myvin/body.access/1/rpc.UpdateDoor            | rpc_method               | True           | none                         |
        | python | //VCU.myvin/body.access//rpc.UpdateDoor             | rpc_method               | True           | none                         |
        | python | /body.access/1/rpc.UpdateDoor                       | rpc_method               | True           | none                         |
        | python | /body.access//rpc.UpdateDoor                        | rpc_method               | True           | none                         |
        | python | ///body.access/1/rpc.UpdateDoor                     | rpc_method               | False          | none                         |
        | python | /1/rpc.UpdateDoor                                   | rpc_method               | False          | none                         |
        | python | //VCU.myvin//1/rpc.UpdateDoor                       | rpc_method               | False          | none                         |
        | python | /hartley                                            | uri                      | True           | none                         |
        | python | /hartley//                                          | uri                      | True           | none                         |
        | python | /hartley/0                                          | uri                      | True           | none                         |
        | python | /1                                                  | uri                      | True           | none                         |
        | python | /body.access/1                                      | uri                      | True           | none                         |
        | python | /body.access/1/door.front_left#Door                 | uri                      | True           | none                         |
        | python | //vcu.vin/body.access/1/door.front_left#Door        | uri                      | True           | none                         |
        | python | /body.access/1/rpc.OpenWindow                       | uri                      | True           | none                         |
        | python | /body.access/1/rpc.response                         | uri                      | True           | none                         |
        | python |                                                     | uri                      | False          | Uri is empty.                |
        | python | :                                                   | uri                      | False          | Uri is empty.                |
        | python | ///                                                 | uri                      | False          | Uri is empty.                |
        | python | ////                                                | uri                      | False          | Uri is empty.                |
        | python | 1                                                   | uri                      | False          | Uri is empty.                |
        | python | a                                                   | uri                      | False          | Uri is empty.                |
        | python | /petapp/1/rpc.OpenWindow                            | rpc_method               | True           | none                         |
        | python | /petapp/1/rpc.response                              | rpc_method               | True           | none                         |
        | python | /petapp/1/rpc.response                              | rpc_response             | True           | none                         |
        | python | /petapp/1/rpc.OpenWindow                            | rpc_response             | False          | none                         |
        | python | /petapp//                                           | rpc_method               | False          | none                         |
        | python | /petapp                                             | rpc_method               | False          | none                         |
        | python | /petapp/1/                                          | rpc_method               | False          | none                         |
        | python | /petapp/1/rpc                                       | rpc_method               | False          | none                         |
        | python | /petapp/1/dummy                                     | rpc_method               | False          | none                         |
        | python | /petapp/1/rpc_dummy                                 | rpc_method               | False          | none                         |
        | python |                                                     | is_empty                 | True           | none                         |
        | python | /hartley/23/rpc.echo                                | is_resolved              | False          | none                         |
        | python |                                                     | is_micro_form            | False          | none                         |
        | python | /hartley/23/                                        | is_micro_form            | False          | none                         |
        | python |                                                     | is_long_form_uuri        | False          | none                         |
        | python |                                                     | is_long_form_uauthority  | False          | none                         |
        | python | /hartley/23/                                        | is_long_form_uuri        | False          | none                         |
        | python | //vcu.veh.gm.com/hartley/23/                        | is_long_form_uuri        | False          | none                         |
        | python | ///hartley/23/                                      | is_long_form_uuri        | False          | none                         |
        | python | ///hartley/23/                                      | is_long_form_uauthority  | False          | none                         |
        | python |                                                     | is_micro_form            | False          | none                         |
        | python | ///hartley/23/                                      | is_micro_form            | False          | none                         |