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

#ifndef _TEST_AGENT_H_
#define _TEST_AGENT_H_

//#include <SocketUTransport.h>
//#include <up-client-zenoh-cpp/client/upZenohClient.h>
#include <APIWrapper.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <unistd.h>

using FunctionType =
    std::variant<std::function<uprotocol::v1::UStatus(rapidjson::Document&)>,
                 std::function<void(rapidjson::Document&)>>;

/// @class TestAgent
/// @brief Represents a test agent that communicates with a test manager.
///
/// The TestAgent class is responsible for connecting to a test manager, sending
/// and receiving messages, and handling various commands. It inherits from the
/// UListener class to handle incoming messages.

class TestAgent : public APIWrapper {
public:
	/// @brief Constructs a TestAgent object with the specified transport type.
	/// @param[in] transportType The type of transport to be used by the agent.
	TestAgent(const std::string transportType);

	/// @brief Destroys the TestAgent object.
	~TestAgent();

	/// @brief Connects the agent to the test manager.
	/// @return True if the connection is successful, false otherwise.
	bool socketConnect();

	/// @brief Receives data from the test manager.
	void receiveFromTM();

	/// @brief Sends a message to the test manager.
	/// @param[in] proto The message to be sent.
	/// @param[in] action The action associated with the message.
	/// @param[in] strTest_id The ID of the test (optional).
	void sendToTestManager(const uprotocol::v1::UMessage& proto,
	                       const std::string& action,
	                       const std::string& strTest_id = "") const override;

	/// @brief Sends a status update to the test manager.
	/// @param[in] status The status update to be sent.
	/// @param[in] action The action associated with the status update.
	/// @param[in] strTest_id The ID of the test associated with the status
	/// update (optional).
	void sendToTestManager(const uprotocol::v1::UStatus& status,
	                       const std::string& action,
	                       const std::string& strTest_id = "") const override;

	/// @brief Sends a message to the test manager.
	/// @param[in,out] doc The JSON document to be sent.
	/// @param[in,out] jsonVal The JSON value to be sent.
	/// @param[in] action The action associated with the message.
	/// @param[in] strTest_id The ID of the test (optional).
	void sendToTestManager(rapidjson::Document& doc, rapidjson::Value& jsonVal,
	                       const std::string action,
	                       const std::string& strTest_id = "") const override;

private:
	// The socket used for communication with the test manager.
	int clientSocket_;
	// The address of the test manager.
	struct sockaddr_in mServerAddress_;

	// The map of action handlers.
	std::unordered_map<std::string, FunctionType> actionHandlers_;

	/// @brief Processes the received message.
	/// @param[in,out] jsonData The JSON data of the received message.
	void processMessage(rapidjson::Document& jsonData);

	/// @brief Disconnects the agent from the test manager.
	/// @return The status of the disconnection.
	void socketDisconnect();

	/// @brief Writes data to the test manager socket.
	/// @param[in,out] responseDoc The JSON document containing the response
	/// data.
	/// @param[in] action The action associated with the response.
	void writeDataToTMSocket(rapidjson::Document& responseDoc) const;

	/// @brief Creates a string value for a RapidJSON document.
	/// @param[in,out] doc The RapidJSON document to which the string value will
	/// be added.
	/// @param[in] data The string data to be converted into a RapidJSON value.
	/// @return A rapidjson::Value object containing the string data.
	/// This function takes a RapidJSON document and a string as parameters,
	/// creates a RapidJSON value from the string, and returns it.
	/// The returned value can be added to a RapidJSON document as either a key
	/// or a value.
	rapidjson::Value createRapidJsonString(rapidjson::Document& doc,
	                                       const std::string& data) const;
};

#endif  //_TEST_AGENT_H_
