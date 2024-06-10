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

#include <TestAgent.h>
#include <google/protobuf/any.pb.h>

TestAgent::TestAgent(const std::string transportType) {
	spdlog::info(
	    "TestAgent::TestAgent(), Creating TestAgent with transport type: {}",
	    transportType);
	transportPtr_ = createTransport(transportType);
	if (nullptr == transportPtr_) {
		spdlog::error("TestAgent::TestAgent(), Failed to create transport");
		exit(1);
	}

	clientSocket_ = 0;
	actionHandlers_ = {
	    {string(Constants::SEND_COMMAND),
	     std::function<UStatus(Document&)>(
	         [this](Document& doc) { return this->handleSendCommand(doc); })},
	    {string(Constants::REGISTER_LISTENER_COMMAND),
	     std::function<UStatus(Document&)>([this](Document& doc) {
		     return this->handleRegisterListenerCommand(doc);
	     })},
	    {string(Constants::UNREGISTER_LISTENER_COMMAND),
	     std::function<UStatus(Document&)>([this](Document& doc) {
		     return this->handleUnregisterListenerCommand(doc);
	     })},
	    {string(Constants::INVOKE_METHOD_COMMAND),
	     std::function<void(Document&)>(
	         [this](Document& doc) { this->handleInvokeMethodCommand(doc); })},
	    {string(Constants::SERIALIZE_URI),
	     std::function<void(Document&)>(
	         [this](Document& doc) { this->handleSerializeUriCommand(doc); })},
	    {string(Constants::DESERIALIZE_URI),
	     std::function<void(Document&)>([this](Document& doc) {
		     this->handleDeserializeUriCommand(doc);
	     })}};
}

TestAgent::~TestAgent() {}

UStatus TestAgent::onReceive(
    uprotocol::utransport::UMessage& transportUMessage) const {
	spdlog::info("TestAgent::onReceive(), received.");
	uprotocol::v1::UPayload payV1;
	payV1.set_format(
	    (uprotocol::v1::UPayloadFormat)transportUMessage.payload().format());

	UMessage umsg;
	UStatus ustatus;

	if (transportUMessage.attributes().type() ==
	    uprotocol::v1::UMessageType::UMESSAGE_TYPE_REQUEST) {
		google::protobuf::StringValue string_value;
		string_value.set_value("SuccessRPCResponse");
		Any any_message;
		any_message.PackFrom(string_value);
		string serialized_message;
		any_message.SerializeToString(&serialized_message);
		uprotocol::utransport::UPayload payload1(
		    (const unsigned char*)serialized_message.c_str(),
		    serialized_message.length(),
		    uprotocol::utransport::UPayloadType::VALUE);
		payload1.setFormat(
		    uprotocol::utransport::UPayloadFormat::PROTOBUF_WRAPPED_IN_ANY);

		auto attr =
		    uprotocol::utransport::UAttributesBuilder::response(
		        transportUMessage.attributes().sink(),
		        transportUMessage.attributes().source(),
		        UPriority::UPRIORITY_CS4, transportUMessage.attributes().id())
		        .build();
		uprotocol::utransport::UMessage respTransportUMessage(payload1, attr);
		ustatus = transportPtr_->send(respTransportUMessage);
	} else {
		payV1.set_value(transportUMessage.payload().data(),
		                transportUMessage.payload().size());

		umsg.mutable_payload()->CopyFrom(payV1);
		umsg.mutable_attributes()->CopyFrom(transportUMessage.attributes());

		sendToTestManager(umsg,
		                  (const string)string(Constants::RESPONSE_ON_RECEIVE));
	}

	return ustatus;
}

std::shared_ptr<uprotocol::utransport::UTransport> TestAgent::createTransport(
    const std::string& transportType) {
	if (transportType == "socket") {
		return std::make_shared<SocketUTransport>();
	} else if (transportType == "zenoh") {
		return uprotocol::client::UpZenohClient::instance(
		    BuildUAuthority().setName("cpp").build(), BuildUEntity()
		                                                  .setName("rpc.client")
		                                                  .setMajorVersion(1)
		                                                  .setId(1)
		                                                  .build());
	} else {
		spdlog::error("Invalid transport type: {}", transportType);
		return nullptr;
	}
}

Value TestAgent::createRapidJsonStringValue(Document& doc,
                                            const std::string& data) const {
	Value stringValue(rapidjson::kStringType);
	stringValue.SetString(data.c_str(), doc.GetAllocator());
	return stringValue;
}

void TestAgent::writeDataToTMSocket(Document& responseDoc,
                                    const std::string action) const {
	rapidjson::Value keyAction =
	    createRapidJsonStringValue(responseDoc, Constants::ACTION);
	rapidjson::Value valAction(action.c_str(), responseDoc.GetAllocator());
	responseDoc.AddMember(keyAction, valAction, responseDoc.GetAllocator());

	rapidjson::Value keyUE =
	    createRapidJsonStringValue(responseDoc, Constants::UE);
	rapidjson::Value valUE(Constants::TEST_AGENT, responseDoc.GetAllocator());
	responseDoc.AddMember(keyUE, valUE, responseDoc.GetAllocator());

	rapidjson::StringBuffer buffer;
	Writer<rapidjson::StringBuffer> writer(buffer);

	responseDoc.Accept(writer);

	// Get the JSON data as a C++ string
	std::string json = buffer.GetString();
	spdlog::info("TestAgent::writeDataToTMSocket(), Sent to TM : {}", json);

	if (send(clientSocket_, json.c_str(), strlen(json.c_str()), 0) == -1) {
		spdlog::error(
		    "TestAgent::writeDataToTMSocket(), Error sending data to TM ");
	}
}

void TestAgent::sendToTestManager(const Message& proto, const string& action,
                                  const string& strTest_id) const {
	Document responseDict;
	responseDict.SetObject();
	Value dataValue = ProtoConverter::convertMessageToJson(proto, responseDict);
	spdlog::info("TestAgent::sendToTestManager(), dataValue is : {}",
	             dataValue.GetString());

	rapidjson::Value keyData =
	    createRapidJsonStringValue(responseDict, Constants::DATA);
	responseDict.AddMember(keyData, dataValue, responseDict.GetAllocator());

	rapidjson::Value keyTestID =
	    createRapidJsonStringValue(responseDict, Constants::TEST_ID);

	if (!strTest_id.empty()) {
		Value jsonStrValue(rapidjson::kStringType);
		jsonStrValue.SetString(
		    strTest_id.c_str(),
		    static_cast<rapidjson::SizeType>(strTest_id.length()),
		    responseDict.GetAllocator());
		responseDict.AddMember(keyTestID, jsonStrValue,
		                       responseDict.GetAllocator());
	} else {
		responseDict.AddMember(keyTestID, "", responseDict.GetAllocator());
	}

	writeDataToTMSocket(responseDict, action);
}

void TestAgent::sendToTestManager(Document& document, Value& jsonData,
                                  const string action,
                                  const string& strTest_id) const {
	Value keyData = createRapidJsonStringValue(document, Constants::DATA);
	document.AddMember(keyData, jsonData, document.GetAllocator());
	rapidjson::Value keyTestID =
	    createRapidJsonStringValue(document, Constants::TEST_ID);
	if (!strTest_id.empty()) {
		Value jsonStrValue(rapidjson::kStringType);
		jsonStrValue.SetString(
		    strTest_id.c_str(),
		    static_cast<rapidjson::SizeType>(strTest_id.length()),
		    document.GetAllocator());
		document.AddMember(keyTestID, jsonStrValue, document.GetAllocator());
	} else {
		document.AddMember(keyTestID, "", document.GetAllocator());
	}

	writeDataToTMSocket(document, action);
}

UStatus TestAgent::handleSendCommand(Document& jsonData) {
	UMessage umsg;
	ProtoConverter::dictToProto(jsonData[Constants::DATA], umsg,
	                            jsonData.GetAllocator());
	spdlog::info("TestAgent::handleSendCommand(), umsg string is: {}",
	             umsg.DebugString());

	auto payloadData = umsg.payload();
	std::string payloadString = payloadData.value();
	spdlog::debug(
	    "TestAgent::handleSendCommand(), payload in string format is: {}",
	    payloadString);

	uprotocol::utransport::UPayload payload(
	    reinterpret_cast<const unsigned char*>(payloadString.data()),
	    payloadString.size(), uprotocol::utransport::UPayloadType::VALUE);
	payload.setFormat(static_cast<uprotocol::utransport::UPayloadFormat>(
	    payloadData.format()));

	auto id = uprotocol::uuid::Uuidv8Factory::create();
	auto uAttributesWithId =
	    uprotocol::utransport::UAttributesBuilder(umsg.attributes().source(),
	                                              id, umsg.attributes().type(),
	                                              umsg.attributes().priority())
	        .build();

	uprotocol::utransport::UMessage transportUMessage(payload,
	                                                  uAttributesWithId);
	return transportPtr_->send(transportUMessage);
}

UStatus TestAgent::handleRegisterListenerCommand(Document& jsonData) {
	UUri uri;
	ProtoConverter::dictToProto(jsonData[Constants::DATA], uri,
	                            jsonData.GetAllocator());
	return transportPtr_->registerListener(uri, *this);
}

UStatus TestAgent::handleUnregisterListenerCommand(Document& jsonData) {
	UUri uri;
	ProtoConverter::dictToProto(jsonData[Constants::DATA], uri,
	                            jsonData.GetAllocator());
	return transportPtr_->unregisterListener(uri, *this);
}

void TestAgent::handleInvokeMethodCommand(Document& jsonData) {
	Value& data = jsonData[Constants::DATA];
	std::string strTest_id = jsonData[Constants::TEST_ID].GetString();

	// Convert data and payload to protocol buffers
	UPayload upPay;
	ProtoConverter::dictToProto(data[Constants::PAYLOAD], upPay,
	                            jsonData.GetAllocator());
	string str = upPay.value();
	spdlog::debug(
	    "TestAgent::handleInvokeMethodCommand(), payload in string format is : "
	    " {}",
	    str);
	uprotocol::utransport::UPayload payload(
	    (const unsigned char*)str.c_str(), str.length(),
	    uprotocol::utransport::UPayloadType::VALUE);
	payload.setFormat((uprotocol::utransport::UPayloadFormat)upPay.format());

	data.RemoveMember("payload");  // removing payload to make it proper  uuri
	UUri uri;
	ProtoConverter::dictToProto(data, uri, jsonData.GetAllocator());
	spdlog::debug(
	    "TestAgent::handleInvokeMethodCommand(), UUri in string format is :  "
	    "{}",
	    uri.DebugString());

	CallOptions options;
	options.set_ttl(10000);
	options.set_priority(UPriority::UPRIORITY_CS4);

	auto rpc_ptr =
	    dynamic_cast<uprotocol::rpc::RpcClient*>(transportPtr_.get());
	std::future<uprotocol::rpc::RpcResponse> responseFuture =
	    rpc_ptr->invokeMethod(uri, payload, options);

	try {
		spdlog::debug(
		    "handleInvokeMethodCommand(), waiting for payload from "
		    "responseFuture ");
		responseFuture.wait();
		spdlog::debug(
		    "TestAgent::handleInvokeMethodCommand(), getting payload from "
		    "responseFuture ");
		uprotocol::rpc::RpcResponse rpcResponse = responseFuture.get();
		uprotocol::utransport::UPayload pay2 = rpcResponse.message.payload();
		spdlog::debug(
		    "TestAgent::handleInvokeMethodCommand(), payload size from "
		    "responseFuture is : {}",
		    pay2.size());
		string strPayload = std::string(
		    reinterpret_cast<const char*>(pay2.data()), pay2.size());
		spdlog::info(
		    "TestAgent::handleInvokeMethodCommand(), payload got from "
		    "responseFuture is : {}",
		    strPayload);

		uprotocol::v1::UPayload payV1;
		payV1.set_format((uprotocol::v1::UPayloadFormat)pay2.format());
		payV1.set_value(pay2.data(), pay2.size());

		// Create v1 UMessage from transport UMessage
		UMessage umsg;
		umsg.mutable_payload()->CopyFrom(payV1);
		umsg.mutable_attributes()->CopyFrom(rpcResponse.message.attributes());

		sendToTestManager(umsg, Constants::INVOKE_METHOD_COMMAND, strTest_id);

	} catch (const std::exception& e) {
		spdlog::error(
		    "TestAgent::handleInvokeMethodCommand(), Exception received while "
		    "getting payload: {}",
		    e.what());
	}
	return;
}

void TestAgent::handleSerializeUriCommand(Document& jsonData) {
	UUri uri;
	ProtoConverter::dictToProto(jsonData[Constants::DATA], uri,
	                            jsonData.GetAllocator());

	Document document;
	document.SetObject();

	Value jsonValue(rapidjson::kStringType);
	string strUri = LongUriSerializer::serialize(uri);
	jsonValue.SetString(strUri.c_str(),
	                    static_cast<rapidjson::SizeType>(strUri.length()),
	                    document.GetAllocator());

	std::string strTest_id = jsonData[Constants::TEST_ID].GetString();

	sendToTestManager(document, jsonValue, Constants::SERIALIZE_URI,
	                  strTest_id);
	return;
}

void TestAgent::handleDeserializeUriCommand(Document& jsonData) {
	Document document;
	document.SetObject();

	Value jsonValue(rapidjson::kStringType);
	string strUri = LongUriSerializer::serialize(
	    LongUriSerializer::deserialize(jsonData["data"].GetString()));
	jsonValue.SetString(strUri.c_str(),
	                    static_cast<rapidjson::SizeType>(strUri.length()),
	                    document.GetAllocator());

	std::string strTest_id = jsonData[Constants::TEST_ID].GetString();

	sendToTestManager(document, jsonValue, Constants::DESERIALIZE_URI,
	                  strTest_id);

	return;
}

void TestAgent::processMessage(Document& json_msg) {
	std::string action = json_msg[Constants::ACTION].GetString();
	std::string strTest_id = json_msg[Constants::TEST_ID].GetString();

	spdlog::info("TestAgent::processMessage(), Received action : {}", action);

	auto it = actionHandlers_.find(action);
	if (it != actionHandlers_.end()) {
		const auto& function = it->second;
		spdlog::debug(
		    "TestAgent::processMessage(), Found respective function and "
		    "calling the same. ");
		if (std::holds_alternative<std::function<UStatus(Document&)>>(
		        function)) {
			auto result =
			    std::get<std::function<UStatus(Document&)>>(function)(json_msg);
			spdlog::info("TestAgent::processMessage(), received result is : {}",
			             result.message());
			Document document;
			document.SetObject();

			Value statusObj(rapidjson::kObjectType);

			Value strValMsg;
			strValMsg.SetString(result.message().c_str(),
			                    document.GetAllocator());
			rapidjson::Value keyMessage =
			    createRapidJsonStringValue(document, Constants::MESSAGE);
			statusObj.AddMember(keyMessage, strValMsg, document.GetAllocator());

			rapidjson::Value keyCode =
			    createRapidJsonStringValue(document, Constants::CODE);
			statusObj.AddMember(keyCode, result.code(),
			                    document.GetAllocator());

			rapidjson::Value keyDetails =
			    createRapidJsonStringValue(document, Constants::DETAILS);
			rapidjson::Value detailsArray(rapidjson::kArrayType);
			statusObj.AddMember(keyDetails, detailsArray,
			                    document.GetAllocator());

			sendToTestManager(document, statusObj, action, strTest_id);
		} else {
			std::get<std::function<void(Document&)>>(function)(json_msg);
			spdlog::warn("TestAgent::processMessage(), Received no result");
		}
	} else {
		spdlog::warn("TestAgent::processMessage(), action '{}' not found.",
		             action);
	}
}

void TestAgent::receiveFromTM() {
	char recv_data[Constants::BYTES_MSG_LENGTH];
	try {
		while (true) {
			ssize_t bytes_received =
			    recv(clientSocket_, recv_data, Constants::BYTES_MSG_LENGTH, 0);
			if (bytes_received < 1) {
				spdlog::warn(
				    "TestAgent::receiveFromTM(), no data received, exiting the "
				    "CPP Test Agent ...");
				socketDisconnect();
				break;
			}

			recv_data[bytes_received] = '\0';
			std::string json_str(recv_data);
			spdlog::info(
			    "TestAgent::receiveFromTM(), Received data from test manager: "
			    "{}",
			    json_str);

			Document json_msg;
			json_msg.Parse(json_str.c_str());
			if (json_msg.HasParseError()) {
				// Handle parsing error
				spdlog::error(
				    "TestAgent::receiveFromTM(), Failed to parse JSON data: {}",
				    json_str);
				continue;
			}

			processMessage(json_msg);
		}
	} catch (std::exception& e) {
		spdlog::error(
		    "TestAgent::receiveFromTM(), Exception occurred due to {}",
		    e.what());
	}
}

bool TestAgent::socketConnect() {
	clientSocket_ = socket(AF_INET, SOCK_STREAM, 0);
	if (clientSocket_ == -1) {
		spdlog::error("TestAgent::socketConnect(), Error creating socket");
		return false;
	}

	mServerAddress_.sin_family = AF_INET;
	mServerAddress_.sin_port = htons(Constants::TEST_MANAGER_PORT);
	inet_pton(AF_INET, Constants::TEST_MANAGER_IP, &(mServerAddress_.sin_addr));

	if (connect(clientSocket_, (struct sockaddr*)&mServerAddress_,
	            sizeof(mServerAddress_)) == -1) {
		spdlog::error("TestAgent::socketConnect(), Error connecting to server");
		return false;
	}

	return true;
}

void TestAgent::socketDisconnect() { close(clientSocket_); }

int main(int argc, char* argv[]) {
	// uncomment this line to set log level to debug
	// spdlog::set_level(spdlog::level::level_enum::debug);
	spdlog::info(" *** Starting CPP Test Agent *** ");
	if (argc < 3) {
		spdlog::error("Incorrect input params: {} ", argv[0]);
		return 1;
	}

	std::string transportType;
	std::vector<std::string> args(argv + 1, argv + argc);

	for (auto it = args.begin(); it != args.end(); ++it) {
		if (*it == "--transport" && (it + 1) != args.end()) {
			transportType = *(it + 1);
			break;
		}
	}

	if (transportType.empty()) {
		spdlog::error("Transport type not specified");
		return 1;
	}

	TestAgent testAgent = TestAgent(transportType);
	if (testAgent.socketConnect()) {
		std::thread receiveThread =
		    std::thread(&TestAgent::receiveFromTM, &testAgent);

		Document document;
		document.SetObject();

		Value sdkName(kObjectType);  // Create an empty object
		sdkName.AddMember("SDK_name", "cpp", document.GetAllocator());

		testAgent.sendToTestManager(document, sdkName, "initialize");
		receiveThread.join();
	}

	return 0;
}
