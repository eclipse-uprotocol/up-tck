
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

class TestAgent {
public:
	TestAgent();
	~TestAgent();
	static int Connect();
	static int DisConnect();
	static void receiveFromTM();
	static void processMessage(Document &jsonData);
    static void sendToTestManager(const Message &proto, const string &action, const string& strTest_id="");
    static void sendToTestManager(Document &doc, Value &jsonVal, string action, const string& strTest_id="");
    static std::unordered_map<std::string, FunctionType> actionHandlers;
    static const uprotocol::utransport::UListener *listener;

	static UStatus handleSendCommand(Document &jsonData);
	static UStatus handleRegisterListenerCommand(Document &jsonData);
	static UStatus handleUnregisterListenerCommand(Document &jsonData);
	static void handleInvokeMethodCommand(Document &jsonData);
	static void handleSerializeUriCommand(Document &jsonData);
	static void handleDeserializeUriCommand(Document &jsonData);

private:
	static int clientSocket;
	static struct sockaddr_in mServerAddress;
    static SocketUTransport *transport;

    static void writeDataToTMSocket(Document &responseDoc, string action) ;
};

class SocketUListener : public uprotocol::utransport::UListener
{
public:
	SocketUListener(SocketUTransport *transport)
	{
		m_transport = transport;
	}

	UStatus onReceive(uprotocol::utransport::UMessage &transportUMessage) const
	{
		std::cout << "SocketUListener::onReceive(), received." << std::endl;
		uprotocol::v1::UPayload payV1;
    		payV1.set_format((uprotocol::v1::UPayloadFormat)transportUMessage.payload().format());

		UMessage umsg;
		UStatus ustatus;

        if (transportUMessage.attributes().type() == uprotocol::v1::UMessageType::UMESSAGE_TYPE_REQUEST)
        {
        	google::protobuf::StringValue string_value;
        	string_value.set_value("SuccessRPCResponse");
        	Any any_message;
        	any_message.PackFrom(string_value);
        	string serialized_message;
        	any_message.SerializeToString(&serialized_message);
        	uprotocol::utransport::UPayload payload1((const unsigned char *)serialized_message.c_str(), serialized_message.length(), uprotocol::utransport::UPayloadType::VALUE);
        	payload1.setFormat(uprotocol::utransport::UPayloadFormat::PROTOBUF_WRAPPED_IN_ANY);

        	auto attr  = uprotocol::utransport::UAttributesBuilder::response(transportUMessage.attributes().sink(), 
					transportUMessage.attributes().source(),
					UPriority::UPRIORITY_CS4, transportUMessage.attributes().id()).build();
		uprotocol::utransport::UMessage respTransportUMessage(payload1,attr);
        	ustatus = m_transport->send(respTransportUMessage);
        }
        else
        {
    		payV1.set_value(transportUMessage.payload().data(), transportUMessage.payload().size());    		

    		umsg.mutable_payload()->CopyFrom(payV1);
    		umsg.mutable_attributes()->CopyFrom(transportUMessage.attributes());

        	TestAgent::sendToTestManager(umsg, (const string)string(Constants::RESPONSE_ON_RECEIVE));
        }

        return ustatus;
	}

private:
	SocketUTransport *m_transport;
};

#endif /*_TEST_AGENT_H_*/
