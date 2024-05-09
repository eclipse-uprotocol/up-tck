
/*
 * Copyright (c) 2024 General Motors GTO LLC
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
 * SPDX-FileCopyrightText: 2024 General Motors GTO LLC
 * SPDX-License-Identifier: Apache-2.0
 */

#ifndef _TEST_AGENT_H_
#define _TEST_AGENT_H_

#include <iostream>
#include <unistd.h>
#include <string>
#include <thread>
#include <optional>
#include <map>
#include <variant>

#include <Constants.h>
#include <spdlog/spdlog.h>
#include <up-client-zenoh-cpp/client/upZenohClient.h>
#include <up-cpp/uri/serializer/LongUriSerializer.h>
#include <up-cpp/uuid/factory/Uuidv8Factory.h>
#include <up-cpp/transport/UTransport.h>
#include <up-core-api/uri.pb.h>
#include <up-core-api/umessage.pb.h>

#include <netinet/in.h>
#include <arpa/inet.h>

#include <SocketUTransport.h>
#include "ProtoConverter.h"

#include "rapidjson/document.h"
#include "rapidjson/writer.h"
#include "rapidjson/stringbuffer.h"

#include <google/protobuf/any.pb.h>
#include <google/protobuf/util/message_differencer.h>

using namespace google::protobuf;
using namespace std;
using namespace rapidjson;

using FunctionType = std::variant<std::function<UStatus(Document&)>, std::function<void(Document&)>>;

class TestAgent : public uprotocol::utransport::UListener {
public:
	TestAgent(std::string transportType);
	~TestAgent();
	UStatus onReceive(uprotocol::utransport::UMessage &transportUMessage) const;
	bool Connect();
	int DisConnect();
	void receiveFromTM();
	void processMessage(Document &jsonData);
    void sendToTestManager(const Message &proto, const string &action, const string& strTest_id="") const;
    void sendToTestManager(Document &doc, Value &jsonVal, string action, const string& strTest_id="") const;
	UStatus handleSendCommand(Document &jsonData);
	UStatus handleRegisterListenerCommand(Document &jsonData);
	UStatus handleUnregisterListenerCommand(Document &jsonData);
	void handleInvokeMethodCommand(Document &jsonData);
	void handleSerializeUriCommand(Document &jsonData);
	void handleDeserializeUriCommand(Document &jsonData);

private:
	int clientSocket_;
	struct sockaddr_in mServerAddress_;
	std::shared_ptr<uprotocol::utransport::UTransport> transportPtr_;
    std::unordered_map<std::string, FunctionType> actionHandlers_;

    std::shared_ptr<uprotocol::utransport::UTransport> createTransport(const std::string& transportType);
    void writeDataToTMSocket(Document &responseDoc, string action) const;
};

#endif /*_TEST_AGENT_H_*/
