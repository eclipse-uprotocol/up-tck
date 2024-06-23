// SPDX-FileCopyrightText: 2024 Contributors to the Eclipse Foundation
//
// See the NOTICE file(s) distributed with this work for additional
// information regarding copyright ownership.
//
// This program and the accompanying materials are made available under the
// terms of the Apache License Version 2.0 which is available at
// https://www.apache.org/licenses/LICENSE-2.0
//
// SPDX-License-Identifier: Apache-2.0

#ifndef _CONSTANTS_H_
#define _CONSTANTS_H_

#include <iostream>
#include <string>

namespace Constants {
constexpr static const char* TEST_MANAGER_IP = "127.0.0.5";
constexpr static const int TEST_MANAGER_PORT = 12345;
constexpr static const int BYTES_MSG_LENGTH = 32767;
constexpr static const char* SEND_COMMAND = "send";
constexpr static const char* REGISTER_LISTENER_COMMAND = "registerlistener";
constexpr static const char* UNREGISTER_LISTENER_COMMAND = "unregisterlistener";
constexpr static const char* INVOKE_METHOD_COMMAND = "invokemethod";
constexpr static const char* RESPONSE_ON_RECEIVE = "onreceive";
constexpr static const char* RESPONSE_RPC = "rpcresponse";

constexpr static const char* SERIALIZE_URI = "uri_serialize";
constexpr static const char* DESERIALIZE_URI = "uri_deserialize";

constexpr static const char* TOPIC = "topic";
constexpr static const char* TOPICS = "topics";
constexpr static const char* EVENTS = "events";
constexpr static const char* TIMEOUT = "timeout";

constexpr static const char* ID = "id";
constexpr static const char* CODE = "code";
constexpr static const char* UUID = "uuid";
constexpr static const char* STATUS = "status";
constexpr static const char* ULTIFI = "ultifi";
constexpr static const char* COLON = ":";
constexpr static const char* FORWARD_SLASH = "/";
constexpr static const char* EMPTY = " ";
constexpr static const char* COMPLETED = "COMPLETED";
constexpr static const char* IP_ADDRESS = "ip-address";
constexpr static const char* ACTION = "action";
constexpr static const char* TEST_AGENT = "cpp";
constexpr static const char* UE = "ue";
constexpr static const char* DATA = "data";
constexpr static const char* TEST_ID = "test_id";
constexpr static const char* PAYLOAD = "payload";
constexpr static const char* MESSAGE = "message";
constexpr static const char* DETAILS = "details";
};  // namespace Constants

#endif  // _CONSTANTS_H_
