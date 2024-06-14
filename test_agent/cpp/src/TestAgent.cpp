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

using namespace google::protobuf;
using namespace rapidjson;
using namespace uprotocol::uri;
using namespace uprotocol::v1;

TestAgent::TestAgent(const std::string transportType) {
	// Log the creation of the TestAgent with the specified transport type
	spdlog::info(
	    "TestAgent::TestAgent(), Creating TestAgent with transport type: {}",
	    transportType);

	// Create the transport with the specified type
	transportPtr_ = createTransport(transportType);

	// If the transport creation failed, log an error and exit
	if (nullptr == transportPtr_) {
		spdlog::error("TestAgent::TestAgent(), Failed to create transport");
		exit(1);
	}

	// Initialize the client socket
	clientSocket_ = 0;

	// Initialize the action handlers
	actionHandlers_ = {
	    // Handle the "sendCommand" action
	    {string(Constants::SEND_COMMAND),
	     std::function<UStatus(Document&)>(
	         [this](Document& doc) { return this->handleSendCommand(doc); })},

	    // Handle the "registerListener" action
	    {string(Constants::REGISTER_LISTENER_COMMAND),
	     std::function<UStatus(Document&)>([this](Document& doc) {
		     return this->handleRegisterListenerCommand(doc);
	     })},

	    // Handle the "unregisterListener" action
	    {string(Constants::UNREGISTER_LISTENER_COMMAND),
	     std::function<UStatus(Document&)>([this](Document& doc) {
		     return this->handleUnregisterListenerCommand(doc);
	     })},

	    // Handle the "invokeMethod" action
	    {string(Constants::INVOKE_METHOD_COMMAND),
	     std::function<void(Document&)>(
	         [this](Document& doc) { this->handleInvokeMethodCommand(doc); })},

	    // Handle the "serializeUri" action
	    {string(Constants::SERIALIZE_URI),
	     std::function<void(Document&)>(
	         [this](Document& doc) { this->handleSerializeUriCommand(doc); })},

	    // Handle the "deserializeUri" action
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

	// Cast the format from transport to v1
	payV1.set_format(static_cast<uprotocol::v1::UPayloadFormat>(
	    transportUMessage.payload().format()));

	// UMesssage to be sent to Test Manager
	UMessage umsg;
	UStatus ustatus;

	// If the message is a request, send a response
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
		// If the message is a response, send it to the Test Manager
		payV1.set_value(transportUMessage.payload().data(),
		                transportUMessage.payload().size());

		umsg.mutable_payload()->CopyFrom(payV1);
		umsg.mutable_attributes()->CopyFrom(transportUMessage.attributes());
		// Send the message to the Test Manager
		sendToTestManager(umsg,
		                  (const string)string(Constants::RESPONSE_ON_RECEIVE));
	}

	return ustatus;
}

std::shared_ptr<uprotocol::utransport::UTransport> TestAgent::createTransport(
    const std::string& transportType) {
	// If the transport type is "socket", create a new SocketUTransport.
	if (transportType == "socket") {
		return std::make_shared<SocketUTransport>();
	}
	// If the transport type is "zenoh", create a new UpZenohClient.
	else if (transportType == "zenoh") {
		return uprotocol::client::UpZenohClient::instance(
		    BuildUAuthority().setName("cpp").build(), BuildUEntity()
		                                                  .setName("rpc.client")
		                                                  .setMajorVersion(1)
		                                                  .setId(1)
		                                                  .build());
	} else {
		// If the transport type is neither "socket" nor "zenoh", log an error
		// and return null.
		spdlog::error("Invalid transport type: {}", transportType);
		return nullptr;
	}
}

Value TestAgent::createRapidJsonStringValue(Document& doc,
                                            const std::string& data) const {
	// Create a RapidJSON value of string type.
	Value stringValue(rapidjson::kStringType);
	// Set the string value with the provided data using the document's
	// allocator.
	stringValue.SetString(data.c_str(), doc.GetAllocator());
	// Return the created RapidJSON string value.
	return stringValue;
}

void TestAgent::writeDataToTMSocket(Document& responseDoc,
                                    const std::string action) const {
	// Create a RapidJSON string value for the action key.
	rapidjson::Value keyAction =
	    createRapidJsonStringValue(responseDoc, Constants::ACTION);
	// Create a RapidJSON string value for the action value.
	rapidjson::Value valAction(action.c_str(), responseDoc.GetAllocator());
	// Add the action key-value pair to the response document.
	responseDoc.AddMember(keyAction, valAction, responseDoc.GetAllocator());

	// Create a RapidJSON string value for the UE key.
	rapidjson::Value keyUE =
	    createRapidJsonStringValue(responseDoc, Constants::UE);
	// Create a RapidJSON string value for the UE value.
	rapidjson::Value valUE(Constants::TEST_AGENT, responseDoc.GetAllocator());
	// Add the UE key-value pair to the response document.
	responseDoc.AddMember(keyUE, valUE, responseDoc.GetAllocator());

	// Create a RapidJSON string buffer and a writer.
	rapidjson::StringBuffer buffer;
	Writer<rapidjson::StringBuffer> writer(buffer);

	// Write the response document to the buffer.
	responseDoc.Accept(writer);

	// Get the JSON data as a C++ string.
	std::string json = buffer.GetString();
	// Log the sent data.
	spdlog::info("TestAgent::writeDataToTMSocket(), Sent to TM : {}", json);

	// Send the JSON data to the TM socket. If there is an error, log it.
	if (send(clientSocket_, json.c_str(), strlen(json.c_str()), 0) == -1) {
		spdlog::error(
		    "TestAgent::writeDataToTMSocket(), Error sending data to TM ");
	}
}

void TestAgent::sendToTestManager(const Message& proto, const string& action,
                                  const string& strTest_id) const {
	// Create a RapidJSON document and set it as an object.
	Document responseDict;
	responseDict.SetObject();

	// Convert the proto message to a RapidJSON value.
	Value dataValue = ProtoConverter::convertMessageToJson(proto, responseDict);

	// Log the converted data value.
	spdlog::info("TestAgent::sendToTestManager(), dataValue is : {}",
	             dataValue.GetString());

	// Create a RapidJSON string value for the data key.
	rapidjson::Value keyData =
	    createRapidJsonStringValue(responseDict, Constants::DATA);

	// Add the data key-value pair to the response document.
	responseDict.AddMember(keyData, dataValue, responseDict.GetAllocator());

	// Create a RapidJSON string value for the test ID key.
	rapidjson::Value keyTestID =
	    createRapidJsonStringValue(responseDict, Constants::TEST_ID);

	// If the test ID string is not empty, create a RapidJSON string value for
	// it and add it to the response document.
	if (!strTest_id.empty()) {
		Value jsonStrValue(rapidjson::kStringType);
		jsonStrValue.SetString(
		    strTest_id.c_str(),
		    static_cast<rapidjson::SizeType>(strTest_id.length()),
		    responseDict.GetAllocator());
		responseDict.AddMember(keyTestID, jsonStrValue,
		                       responseDict.GetAllocator());
	} else {
		// If the test ID string is empty, add an empty string to the response
		// document.
		responseDict.AddMember(keyTestID, "", responseDict.GetAllocator());
	}

	// Write the response document to the TM socket.
	writeDataToTMSocket(responseDict, action);
}

void TestAgent::sendToTestManager(Document& document, Value& jsonData,
                                  const string action,
                                  const string& strTest_id) const {
	// Create a RapidJSON string value for the data key.
	Value keyData = createRapidJsonStringValue(document, Constants::DATA);
	// Add the data key-value pair to the document.
	document.AddMember(keyData, jsonData, document.GetAllocator());

	// Create a RapidJSON string value for the test ID key.
	rapidjson::Value keyTestID =
	    createRapidJsonStringValue(document, Constants::TEST_ID);

	// If the test ID string is not empty, create a RapidJSON string value for
	// it and add it to the document.
	if (!strTest_id.empty()) {
		Value jsonStrValue(rapidjson::kStringType);
		jsonStrValue.SetString(
		    strTest_id.c_str(),
		    static_cast<rapidjson::SizeType>(strTest_id.length()),
		    document.GetAllocator());
		document.AddMember(keyTestID, jsonStrValue, document.GetAllocator());
	} else {
		// If the test ID string is empty, add an empty string to the document.
		document.AddMember(keyTestID, "", document.GetAllocator());
	}

	// Write the document to the TM socket.
	writeDataToTMSocket(document, action);
}

UStatus TestAgent::handleSendCommand(Document& jsonData) {
	// Create a v1 UMessage object.
	UMessage umsg;
	// Convert the jsonData to a proto message.
	ProtoConverter::dictToProto(jsonData[Constants::DATA], umsg,
	                            jsonData.GetAllocator());
	// Log the UMessage string.
	spdlog::info("TestAgent::handleSendCommand(), umsg string is: {}",
	             umsg.DebugString());

	// Get the payload data from the UMessage.
	auto payloadData = umsg.payload();
	// Convert the payload data to a string.
	std::string payloadString = payloadData.value();
	// Log the payload string.
	spdlog::debug(
	    "TestAgent::handleSendCommand(), payload in string format is: {}",
	    payloadString);

	// Create a utransport payload object with the payload string, its size, and
	// its type.
	uprotocol::utransport::UPayload payload(
	    reinterpret_cast<const unsigned char*>(payloadString.data()),
	    payloadString.size(), uprotocol::utransport::UPayloadType::VALUE);
	// Set the format of the payload.
	payload.setFormat(static_cast<uprotocol::utransport::UPayloadFormat>(
	    payloadData.format()));

	// Create a UUID.
	auto id = uprotocol::uuid::Uuidv8Factory::create();
	// Create utransport attributes from the v1 UMessage.
	auto uAttributesWithId =
	    uprotocol::utransport::UAttributesBuilder(umsg.attributes().source(),
	                                              id, umsg.attributes().type(),
	                                              umsg.attributes().priority())
	        .build();

	// Create a utransport message with the payload and the UAttributes.
	uprotocol::utransport::UMessage transportUMessage(payload,
	                                                  uAttributesWithId);
	// Send the UMessage and return the status.
	return transportPtr_->send(transportUMessage);
}

UStatus TestAgent::handleRegisterListenerCommand(Document& jsonData) {
	// Create a v1 UUri object.
	UUri uri;
	// Convert the jsonData to a proto message.
	ProtoConverter::dictToProto(jsonData[Constants::DATA], uri,
	                            jsonData.GetAllocator());
	// Register this TestAgent as a listener for the given URI and return the
	// status.
	return transportPtr_->registerListener(uri, *this);
}

UStatus TestAgent::handleUnregisterListenerCommand(Document& jsonData) {
	// Create a v1 UUri object.
	UUri uri;
	// Convert the jsonData to a proto message.
	ProtoConverter::dictToProto(jsonData[Constants::DATA], uri,
	                            jsonData.GetAllocator());
	// Unregister this TestAgent as a listener for the given URI and return the
	// status.
	return transportPtr_->unregisterListener(uri, *this);
}

void TestAgent::handleInvokeMethodCommand(Document& jsonData) {
	// Get the data and test ID from the JSON document.
	Value& data = jsonData[Constants::DATA];
	std::string strTest_id = jsonData[Constants::TEST_ID].GetString();

	// Convert data and payload to protocol buffers
	UPayload upPay;
	// Convert the payload data to a proto message.
	ProtoConverter::dictToProto(data[Constants::PAYLOAD], upPay,
	                            jsonData.GetAllocator());
	// Convert the payload data to a string.
	string str = upPay.value();
	// Log the payload string.
	spdlog::debug(
	    "TestAgent::handleInvokeMethodCommand(), payload in string format is : "
	    " {}",
	    str);
	// Create a utransport payload object.
	uprotocol::utransport::UPayload payload(
	    (const unsigned char*)str.c_str(), str.length(),
	    uprotocol::utransport::UPayloadType::VALUE);
	// Set the format of the payload.
	payload.setFormat(
	    static_cast<uprotocol::utransport::UPayloadFormat>(upPay.format()));

	// Remove the payload from the data to make it a proper UUri.
	data.RemoveMember("payload");
	UUri uri;
	// Convert the data to a proto message.
	ProtoConverter::dictToProto(data, uri, jsonData.GetAllocator());
	// Log the UUri string.
	spdlog::debug(
	    "TestAgent::handleInvokeMethodCommand(), UUri in string format is :  "
	    "{}",
	    uri.DebugString());

	// Create CallOptions with a TTL and a priority.
	CallOptions options;
	options.set_ttl(10000);
	options.set_priority(UPriority::UPRIORITY_CS4);

	// Cast the transport pointer to an RpcClient pointer.
	auto rpc_ptr =
	    dynamic_cast<uprotocol::rpc::RpcClient*>(transportPtr_.get());
	// Invoke the method and get a future for the response.
	std::future<uprotocol::rpc::RpcResponse> responseFuture =
	    rpc_ptr->invokeMethod(uri, payload, options);

	try {
		// Wait for the response.
		spdlog::debug(
		    "handleInvokeMethodCommand(), waiting for payload from "
		    "responseFuture ");
		responseFuture.wait();

		// Get the response.
		spdlog::debug(
		    "TestAgent::handleInvokeMethodCommand(), getting payload from "
		    "responseFuture ");
		uprotocol::rpc::RpcResponse rpcResponse = responseFuture.get();

		// Get the payload from the response.
		uprotocol::utransport::UPayload pay2 = rpcResponse.message.payload();

		// Log the size of the payload.
		spdlog::debug(
		    "TestAgent::handleInvokeMethodCommand(), payload size from "
		    "responseFuture is : {}",
		    pay2.size());

		// Convert the payload data to a string.
		string strPayload = std::string(
		    reinterpret_cast<const char*>(pay2.data()), pay2.size());

		// Log the payload string.
		spdlog::info(
		    "TestAgent::handleInvokeMethodCommand(), payload got from "
		    "responseFuture is : {}",
		    strPayload);

		// Create a v1 UPayload with the format and value from the payload.
		uprotocol::v1::UPayload payV1;
		payV1.set_format(
		    static_cast<uprotocol::v1::UPayloadFormat>(pay2.format()));
		payV1.set_value(pay2.data(), pay2.size());

		// Create v1 UMessage from transport UMessage
		UMessage umsg;

		// Copy the payload and attributes from the response to the UMessage.
		umsg.mutable_payload()->CopyFrom(payV1);
		umsg.mutable_attributes()->CopyFrom(rpcResponse.message.attributes());

		// Send the UMessage to the Test Manager.
		sendToTestManager(umsg, Constants::INVOKE_METHOD_COMMAND, strTest_id);

	} catch (const std::future_error& e) {
		spdlog::error(
		    "TestAgent::handleInvokeMethodCommand(), Future error exception "
		    "received while getting payload: {}",
		    e.what());
	} catch (const std::exception& e) {
		spdlog::error(
		    "TestAgent::handleInvokeMethodCommand(), General exception "
		    "received while getting payload: {}",
		    e.what());
	} catch (...) {
		spdlog::error(
		    "TestAgent::handleInvokeMethodCommand(), Unknown exception "
		    "received while getting payload.");
	}
	return;
}
void TestAgent::handleSerializeUriCommand(Document& jsonData) {
	// Create a UUri object.
	UUri uri;

	// Convert the JSON data to a UUri object.
	ProtoConverter::dictToProto(jsonData[Constants::DATA], uri,
	                            jsonData.GetAllocator());

	// Create a new JSON document.
	Document document;
	document.SetObject();

	// Create a JSON value to hold the serialized URI.
	Value jsonValue(rapidjson::kStringType);

	// Serialize the URI to a string.
	string strUri = LongUriSerializer::serialize(uri);

	// Set the JSON value to the serialized URI string.
	jsonValue.SetString(strUri.c_str(),
	                    static_cast<rapidjson::SizeType>(strUri.length()),
	                    document.GetAllocator());

	// Get the test ID from the JSON data.
	std::string strTest_id = jsonData[Constants::TEST_ID].GetString();

	// Send the serialized URI to the Test Manager.
	sendToTestManager(document, jsonValue, Constants::SERIALIZE_URI,
	                  strTest_id);

	return;
}

void TestAgent::handleDeserializeUriCommand(Document& jsonData) {
	// Create a new JSON document.
	Document document;
	document.SetObject();

	// Create a JSON value to hold the serialized URI.
	Value jsonValue(rapidjson::kStringType);

	// Deserialize the URI from the JSON data, then serialize it back to a
	// string.
	string strUri = LongUriSerializer::serialize(
	    LongUriSerializer::deserialize(jsonData["data"].GetString()));

	// Set the JSON value to the serialized URI string.
	jsonValue.SetString(strUri.c_str(),
	                    static_cast<rapidjson::SizeType>(strUri.length()),
	                    document.GetAllocator());

	// Get the test ID from the JSON data.
	std::string strTest_id = jsonData[Constants::TEST_ID].GetString();

	// Send the serialized URI to the Test Manager.
	sendToTestManager(document, jsonValue, Constants::DESERIALIZE_URI,
	                  strTest_id);

	return;
}

void TestAgent::processMessage(Document& json_msg) {
	// Get the action and test ID from the JSON message.
	std::string action = json_msg[Constants::ACTION].GetString();
	std::string strTest_id = json_msg[Constants::TEST_ID].GetString();

	// Log the received action.
	spdlog::info("TestAgent::processMessage(), Received action : {}", action);

	// Find the action in the action handlers map.
	auto it = actionHandlers_.find(action);
	if (it != actionHandlers_.end()) {
		// If the action is found, get the corresponding function.
		const auto& function = it->second;
		spdlog::debug(
		    "TestAgent::processMessage(), Found respective function and "
		    "calling the same. ");

		// Check if the function returns a UStatus.
		if (std::holds_alternative<std::function<UStatus(Document&)>>(
		        function)) {
			// If it does, call the function and get the result.
			auto result =
			    std::get<std::function<UStatus(Document&)>>(function)(json_msg);

			// Log the received result.
			spdlog::info("TestAgent::processMessage(), received result is : {}",
			             result.message());

			// Create a new JSON document and status object.
			Document document;
			document.SetObject();

			Value statusObj(rapidjson::kObjectType);

			// Add the result message to the status object.
			Value strValMsg;
			strValMsg.SetString(result.message().c_str(),
			                    document.GetAllocator());
			rapidjson::Value keyMessage =
			    createRapidJsonStringValue(document, Constants::MESSAGE);
			statusObj.AddMember(keyMessage, strValMsg, document.GetAllocator());

			// Add the result code to the status object.
			rapidjson::Value keyCode =
			    createRapidJsonStringValue(document, Constants::CODE);
			statusObj.AddMember(keyCode, result.code(),
			                    document.GetAllocator());

			// Add an empty details array to the status object.
			rapidjson::Value keyDetails =
			    createRapidJsonStringValue(document, Constants::DETAILS);
			rapidjson::Value detailsArray(rapidjson::kArrayType);
			statusObj.AddMember(keyDetails, detailsArray,
			                    document.GetAllocator());

			// Send the status object to the Test Manager.
			sendToTestManager(document, statusObj, action, strTest_id);
		} else {
			// If the function does not return a UStatus, call it without
			// getting a result.
			std::get<std::function<void(Document&)>>(function)(json_msg);
			spdlog::warn("TestAgent::processMessage(), Received no result");
		}
	} else {
		// If the action is not found in the action handlers map, log a warning.
		spdlog::warn("TestAgent::processMessage(), action '{}' not found.",
		             action);
	}
}

void TestAgent::receiveFromTM() {
	// Buffer to hold received data
	char recv_data[Constants::BYTES_MSG_LENGTH];

	try {
		// Continuously listen for incoming data
		while (true) {
			// Receive data from the socket
			ssize_t bytes_received =
			    recv(clientSocket_, recv_data, Constants::BYTES_MSG_LENGTH, 0);

			// If no data is received, log a warning, disconnect the socket, and
			// break the loop
			if (bytes_received < 1) {
				spdlog::warn(
				    "TestAgent::receiveFromTM(), no data received, exiting the "
				    "CPP Test Agent ...");
				socketDisconnect();
				break;
			}

			// Null-terminate the received data
			recv_data[bytes_received] = '\0';

			// Convert the received data to a string
			std::string json_str(recv_data);

			// Log the received data
			spdlog::info(
			    "TestAgent::receiveFromTM(), Received data from test manager: "
			    "{}",
			    json_str);

			// Parse the received data as a JSON document
			Document json_msg;
			json_msg.Parse(json_str.c_str());

			// If there is a parse error, log an error and continue to the next
			// iteration
			if (json_msg.HasParseError()) {
				spdlog::error(
				    "TestAgent::receiveFromTM(), Failed to parse JSON data: {}",
				    json_str);
				continue;
			}

			// Process the received message
			processMessage(json_msg);
		}
	} catch (const std::runtime_error& e) {
		// If a runtime error occurs, log an error
		spdlog::error(
		    "TestAgent::receiveFromTM(), Runtime error occurred due to {}",
		    e.what());
	} catch (const std::exception& e) {
		// If a general exception occurs, log an error
		spdlog::error(
		    "TestAgent::receiveFromTM(), Exception occurred due to {}",
		    e.what());
	} catch (...) {
		// If an unknown exception occurs, log an error
		spdlog::error(
		    "TestAgent::receiveFromTM(), Unknown exception occurred.");
	}
}

bool TestAgent::socketConnect() {
	// Create a new socket and store the socket descriptor
	clientSocket_ = socket(AF_INET, SOCK_STREAM, 0);

	// If the socket descriptor is -1, an error occurred
	if (clientSocket_ == -1) {
		spdlog::error("TestAgent::socketConnect(), Error creating socket");
		return false;
	}

	// Set the server address structure
	// Address family (IPv4)
	mServerAddress_.sin_family = AF_INET;
	// Port number, converted to network byte order
	mServerAddress_.sin_port = htons(Constants::TEST_MANAGER_PORT);
	// IP address
	inet_pton(AF_INET, Constants::TEST_MANAGER_IP, &(mServerAddress_.sin_addr));

	// Attempt to connect to the server
	if (connect(clientSocket_, (struct sockaddr*)&mServerAddress_,
	            sizeof(mServerAddress_)) == -1) {
		spdlog::error("TestAgent::socketConnect(), Error connecting to server");
		return false;
	}

	// If we reach this point, the connection was successful
	return true;
}

void TestAgent::socketDisconnect() {
	// Close the client socket
	close(clientSocket_);
}

int main(int argc, char* argv[]) {
	// Uncomment this line to set log level to debug
	// spdlog::set_level(spdlog::level::level_enum::debug);

	// Log the start of the Test Agent
	spdlog::info(" *** Starting CPP Test Agent *** ");

	// Check if the correct number of command line arguments were provided
	if (argc < 3) {
		spdlog::error("Incorrect input params: {} ", argv[0]);
		return 1;
	}

	// Initialize transport type and command line arguments
	std::string transportType;
	std::vector<std::string> args(argv + 1, argv + argc);

	// Iterate over command line arguments to find the transport type
	for (auto it = args.begin(); it != args.end(); ++it) {
		if (*it == "--transport" && (it + 1) != args.end()) {
			transportType = *(it + 1);
			break;
		}
	}

	// If no transport type was specified, log an error and exit
	if (transportType.empty()) {
		spdlog::error("Transport type not specified");
		return 1;
	}

	// Create a new TestAgent with the specified transport type
	TestAgent testAgent = TestAgent(transportType);

	// If the TestAgent successfully connects to the server
	if (testAgent.socketConnect()) {
		// Create a new thread to receive data from the Test Manager
		std::thread receiveThread =
		    std::thread(&TestAgent::receiveFromTM, &testAgent);

		// Create a JSON document and add the SDK name to it
		Document document;
		document.SetObject();
		Value sdkName(kObjectType);  // Create an empty object
		sdkName.AddMember("SDK_name", "cpp", document.GetAllocator());

		// Send the JSON document to the Test Manager to initialize the test
		testAgent.sendToTestManager(document, sdkName, "initialize");

		// Wait for the receive thread to finish
		receiveThread.join();
	}

	// Exit the program
	return 0;
}
