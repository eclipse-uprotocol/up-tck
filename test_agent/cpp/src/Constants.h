/*
 * Copyright (c) 2023 General Motors GTO LLC
 *
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 * SPDX-FileType: SOURCE
 * SPDX-FileCopyrightText: 2023 General Motors GTO LLC
 * SPDX-License-Identifier: Apache-2.0
 */

#ifndef _CONSTANTS_H_
#define _CONSTANTS_H_

#include <iostream>
#include <string>

using namespace std;

class Constants {
public:
	constexpr static const char * TEST_MANAGER_IP = "127.0.0.5";
	constexpr static const int TEST_MANAGER_PORT = 12345;
	constexpr static const int BYTES_MSG_LENGTH = 32767;
	constexpr static const char * SEND_COMMAND = "send";
	constexpr static const char * REGISTER_LISTENER_COMMAND = "registerlistener";
	constexpr static const char * UNREGISTER_LISTENER_COMMAND = "unregisterlistener";
	constexpr static const char * INVOKE_METHOD_COMMAND = "invokemethod";
	constexpr static const char * RESPONSE_ON_RECEIVE = "onreceive";
	constexpr static const char * RESPONSE_RPC = "rpcresponse";

	constexpr static const char * SERIALIZE_URI = "uri_serialize";
	constexpr static const char * DESERIALIZE_URI = "uri_deserialize";

	constexpr static const char * TOPIC = "topic";
	constexpr static const char * TOPICS = "topics";
	constexpr static const char * EVENTS = "events";
	constexpr static const char * TIMEOUT = "timeout";

	constexpr static const char * ID = "id";
	constexpr static const char * CODE = "code";
	constexpr static const char * UUID = "uuid";
	constexpr static const char * STATUS = "status";
	constexpr static const char * ULTIFI = "ultifi";
	constexpr static const char * COLON = ":";
	constexpr static const char * FORWARD_SLASH = "/";
	constexpr static const char * EMPTY = " ";
	constexpr static const char * COMPLETED = "COMPLETED";
	constexpr static const char * IP_ADDRESS = "ip-address";
};

#endif /* _CONSTANTS_H_ */
