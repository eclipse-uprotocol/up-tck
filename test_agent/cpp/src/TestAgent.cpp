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

using namespace rapidjson;
using namespace uprotocol::v1;
using namespace std;

TestAgent::TestAgent(const std::string transportType, const std::string uEName)
    : APIWrapper(transportType), uEName_(uEName) {
	// Initialize the client socket
	clientSocket_ = 0;

	// Initialize the action handlers
	actionHandlers_ = {

	    // Handle the "initialize_transport" action
	    {string(Constants::CREATE_TRANSPORT_COMMAND),
	     std::function<UStatus(Document&)>([this](Document& doc) {
		     return this->handleCreateTransportCommand(doc);
	     })},

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
		     return this->removeHandleOrProvideError(doc);
	     })},

	    // Handle the "rpcclient" action
	    {string(Constants::INVOKE_METHOD_COMMAND),
	     std::function<UStatus(Document&)>([this](Document& doc) {
		     return this->handleInvokeMethodCommand(doc);
	     })},

	    // Handle the "rpcserver" action
	    {string(Constants::RPC_SERVER_COMMAND),
	     std::function<UStatus(Document&)>([this](Document& doc) {
		     return this->handleRpcServerCommand(doc);
	     })},

	    // Handle the "removehandle" action
	    {string(Constants::REMOVE_HANDLE_COMMAND),
	     std::function<UStatus(Document&)>([this](Document& doc) {
		     return this->removeHandleOrProvideError(doc);
	     })},

	    // Handle the "notificationsource" action
	    {string(Constants::NOTIFICATION_SOURCE_COMMAND),
	     std::function<UStatus(Document&)>([this](Document& doc) {
		     return this->handleNotificationSourceCommand(doc);
	     })},

	    // Handle the "notificationsink" action
	    {string(Constants::NOTIFICATION_SINK_COMMAND),
	     std::function<UStatus(Document&)>([this](Document& doc) {
		     return this->handleNotificationSinkCommand(doc);
	     })},

	    // Handle the "publisher" action
	    {string(Constants::PUBLISHER_COMMAND),
	     std::function<UStatus(Document&)>([this](Document& doc) {
		     return this->handlePublisherCommand(doc);
	     })},

	    // Handle the "subscriber" action
	    {string(Constants::SUBSCRIBER_COMMAND),
	     std::function<UStatus(Document&)>([this](Document& doc) {
		     return this->handleSubscriberCommand(doc);
	     })}};
}

TestAgent::~TestAgent() {}

Value TestAgent::createRapidJsonString(Document& doc,
                                       const std::string& data) const {
	// Create a RapidJSON value of string type.
	Value stringValue(rapidjson::kStringType);
	// Set the string value with the provided data using the document's
	// allocator.
	stringValue.SetString(data.c_str(), doc.GetAllocator());
	// Return the created RapidJSON string value.
	return stringValue;
}

void TestAgent::writeDataToTMSocket(Document& responseDoc) const {
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

void TestAgent::sendToTestManager(const UMessage& proto, const string& action,
                                  const string& strTest_id) const {
	// Create a RapidJSON document and set it as an object.
	Document responseDict;
	responseDict.SetObject();

	// Convert the proto message to a RapidJSON value.
	Value dataValue = ProtoConverter::convertMessageToJson(proto, responseDict);

	// Log the converted data value.
	spdlog::info("TestAgent::sendToTestManager(), dataValue is : {}",
	             dataValue.GetString());

	sendToTestManager(responseDict, dataValue, action, strTest_id);
}

void TestAgent::sendToTestManager(const UStatus& status, const string& action,
                                  const string& strTest_id) const {
	// Log the received status.
	spdlog::info("TestAgent::processMessage(), received status is : {}",
	             status.message());

	// Create a new JSON document and status object.
	Document document;
	document.SetObject();

	Value statusObj(rapidjson::kObjectType);

	// Add the status message to the status object.
	Value uStatusMessage = createRapidJsonString(document, status.message());
	rapidjson::Value keyMessage =
	    createRapidJsonString(document, Constants::MESSAGE);

	statusObj.AddMember(keyMessage, uStatusMessage, document.GetAllocator());

	// Add the status ucode to the status object.
	rapidjson::Value keyCode = createRapidJsonString(document, Constants::CODE);
	statusObj.AddMember(keyCode, status.code(), document.GetAllocator());

	// Add an empty details array to the status object.
	rapidjson::Value keyDetails =
	    createRapidJsonString(document, Constants::DETAILS);
	rapidjson::Value detailsArray(rapidjson::kArrayType);
	statusObj.AddMember(keyDetails, detailsArray, document.GetAllocator());

	// Send the status object to the Test Manager.
	sendToTestManager(document, statusObj, action, strTest_id);
}

void TestAgent::sendToTestManager(Document& document, Value& jsonData,
                                  const string action,
                                  const string& strTest_id) const {
	// Create a RapidJSON string value for the data key.
	Value keyData = createRapidJsonString(document, Constants::DATA);
	// Add the data key-value pair to the document.
	document.AddMember(keyData, jsonData, document.GetAllocator());

	// Create a RapidJSON string value for the test ID key.
	rapidjson::Value keyTestID =
	    createRapidJsonString(document, Constants::TEST_ID);

	// If the test ID string is not empty, create a RapidJSON string value for
	// it and add it to the document.
	if (!strTest_id.empty()) {
		Value testIdJson = createRapidJsonString(document, strTest_id);
		document.AddMember(keyTestID, testIdJson, document.GetAllocator());
	} else {
		// If the test ID string is empty, add an empty string to the document.
		document.AddMember(keyTestID, "", document.GetAllocator());
	}

	// Create a RapidJSON string value for the action key.
	rapidjson::Value keyAction =
	    createRapidJsonString(document, Constants::ACTION);
	// Create a RapidJSON string value for the action value.
	rapidjson::Value valAction(action.c_str(), document.GetAllocator());
	// Add the action key-value pair to the response document.
	document.AddMember(keyAction, valAction, document.GetAllocator());

	// Create a RapidJSON string value for the UE key.
	rapidjson::Value keyUE = createRapidJsonString(document, Constants::UE);
	// Create a RapidJSON string value for the UE value.
	rapidjson::Value valUE = createRapidJsonString(document, uEName_);
	// Add the UE key-value pair to the response document.
	document.AddMember(keyUE, valUE, document.GetAllocator());

	// Write the document to the TM socket.
	writeDataToTMSocket(document);
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

			// Send the status object to the Test Manager.
			sendToTestManager(result, action, strTest_id);
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
	//spdlog::set_level(spdlog::level::level_enum::debug);

	// Log the start of the Test Agent
	spdlog::info(" *** Starting CPP Test Agent *** ");

	// Check if the correct number of command line arguments were provided
	if (argc < 5) {
		spdlog::error("Incorrect input params: {} ", argv[0]);
		return 1;
	}

	// Initialize transport type and command line arguments
	std::string transportType;
	std::string sdkNameValue;
	std::vector<std::string> args(argv + 1, argv + argc);

	// Iterate over command line arguments to find the transport type
	for (auto it = args.begin(); it != args.end(); ++it) {
		if ((*it == "--transport") && ((it + 1) != args.end())) {
			transportType = *(it + 1);
			it++;
		} else if ((*it == "--sdkname") && ((it + 1) != args.end())) {
			sdkNameValue = *(it + 1);
			it++;
		}
	}

	// If no transport type was specified, log an error and exit
	if (transportType.empty()) {
		spdlog::error("Transport type not specified");
		return 1;
	}

	// If no SDK name was specified, log an error and exit
	if (sdkNameValue.empty()) {
		spdlog::error("SDK name not specified");
		return 1;
	}

	// Create a new TestAgent with the specified transport type
	TestAgent testAgent = TestAgent(transportType, sdkNameValue);

	// If the TestAgent successfully connects to the server
	if (testAgent.socketConnect()) {
		// Create a new thread to receive data from the Test Manager
		std::thread receiveThread =
		    std::thread(&TestAgent::receiveFromTM, &testAgent);

		// Create a JSON document and add the SDK name to it
		Document document;
		document.SetObject();
		Value sdkName(kObjectType);  // Create an empty object
		sdkName.AddMember("SDK_name",
		                  Value(sdkNameValue.c_str(), document.GetAllocator()),
		                  document.GetAllocator());

		// Send the JSON document to the Test Manager to initialize the test
		testAgent.sendToTestManager(document, sdkName, "initialize");

		// Wait for the receive thread to finish
		receiveThread.join();
	}

	// Exit the program
	return 0;
}
