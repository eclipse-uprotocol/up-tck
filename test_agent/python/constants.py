"""
SPDX-FileCopyrightText: Copyright (c) 2024 Contributors to the Eclipse Foundation
See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
SPDX-FileType: SOURCE
SPDX-License-Identifier: Apache-2.0
"""

TEST_MANAGER_ADDR = ("127.0.0.5", 12345)
BYTES_MSG_LENGTH: int = 32767
SEND_COMMAND = "send"
REGISTER_LISTENER_COMMAND = "registerlistener"
UNREGISTER_LISTENER_COMMAND = "unregisterlistener"
INVOKE_METHOD_COMMAND = "invokemethod"
RESPONSE_ON_RECEIVE = "onreceive"
RESPONSE_RPC = "rpcresponse"
SERIALIZE_URI = "uri_serialize"
DESERIALIZE_URI = "uri_deserialize"
VALIDATE_URI = "uri_validate"
VALIDATE_UUID = "uuid_validate"
SERIALIZE_UUID = "uuid_serialize"
DESERIALIZE_UUID = "uuid_deserialize"
MICRO_SERIALIZE_URI = "micro_serialize_uri"
MICRO_DESERIALIZE_URI = "micro_deserialize_uri"