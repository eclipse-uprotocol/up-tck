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

SEND_COMMAND: str = "send"
REGISTER_LISTENER_COMMAND: str = "registerlistener"
UNREGISTER_LISTENER_COMMAND: str = "unregisterlistener"
INVOKE_METHOD_COMMAND: str = "invokemethod"
COMMANDS = set([SEND_COMMAND, REGISTER_LISTENER_COMMAND, UNREGISTER_LISTENER_COMMAND, INVOKE_METHOD_COMMAND])

DISPATCHER_ADDR: tuple = ("127.0.0.1", 44444)
TEST_MANAGER_ADDR: tuple = ("127.0.0.5", 12345)
BYTES_MSG_LENGTH: int = 32767

LONG_URI_SERIALIZE: str = "longuriserialize"
LONG_URI_DESERIALIZE: str = "longurideserialize"
MICRO_URI_SERIALIZE: str = "microuriserialize"
MICRO_URI_DESERIALIZE: str = "microurideserialize"
SERIALIZERS = set([LONG_URI_SERIALIZE, LONG_URI_DESERIALIZE, MICRO_URI_SERIALIZE, MICRO_URI_DESERIALIZE])

LONG_URI_SERIALIZE_RESPONSE: str = "longuriserialize_response"
LONG_URI_DESERIALIZE_RESPONSE: str = "longurideserialize_response"
MICRO_URI_SERIALIZE_RESPONSE: str = "microuriserialize_response"
MICRO_URI_DESERIALIZE_RESPONSE: str = "microurideserialize_response"