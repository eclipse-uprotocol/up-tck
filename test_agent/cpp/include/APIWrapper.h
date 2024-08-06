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

#ifndef _API_WRAPPER_H_
#define _API_WRAPPER_H_

#include <SocketUTransport.h>
#include <up-transport-zenoh-cpp/ZenohUTransport.h>

#include "ProtoConverter.h"
#include "utils.h"

/// @class APIWrapper
/// @brief Represents a wrapper class to execute up-cpp L1 and L2 apis.
///
/// The APIWrapper class is responsible providing inteface for cpp test agent to
/// invoke up-cpp L1 and L2 apis.

class APIWrapper {
public:
	/// @brief Constructs an APIWrapper object with the specified transport
	/// type.
	/// @param[in] transportType The type of transport to be used by the agent.
	APIWrapper(const std::string transportType);

	/// @brief Destroys the APIWrapper object
	virtual ~APIWrapper();

	/// @brief Sends a message to the test manager.
	/// @param[in] proto The message to be sent.
	/// @param[in] action The action associated with the message.
	/// @param[in] strTest_id The ID of the test (optional).
	virtual void sendToTestManager(const uprotocol::v1::UMessage& proto,
	                               const std::string& action,
	                               const std::string& strTest_id = "") const;

	/// @brief Sends a status update to the test manager.
	/// @param[in] status The status to be sent.
	/// @param[in] action The action associated with the status.
	/// @param[in] strTest_id The ID of the test (optional).
	virtual void sendToTestManager(const uprotocol::v1::UStatus& status,
	                               const std::string& action,
	                               const std::string& strTest_id = "") const;

	/// @brief Sends a JSON message to the test manager.
	/// @param[in,out] doc The JSON document to be sent.
	/// @param[in,out] jsonVal The JSON value to be sent.
	/// @param[in] action The action associated with the message.
	/// @param[in] strTest_id The ID of the test (optional).
	virtual void sendToTestManager(rapidjson::Document& doc,
	                               rapidjson::Value& jsonVal,
	                               const std::string action,
	                               const std::string& strTest_id = "") const;

	/// @brief Attempts to remove a handle based on JSON data or provide an
	/// error if unsuccessful.
	/// @param[in] jsonData The JSON data containing the URI of the handle to be
	/// removed.
	/// @return UStatus indicating success or failure of the operation.
	uprotocol::v1::UStatus removeHandleOrProvideError(
	    rapidjson::Document& jsonData);

	/// @brief Attempts to remove a handle based on a URI or provide an error if
	/// unsuccessful.
	/// @param[in] uri The URI of the handle to be removed.
	/// @return UStatus indicating success or failure of the operation.
	uprotocol::v1::UStatus removeHandleOrProvideError(
	    const uprotocol::v1::UUri& uri);

	/// @brief Handles the "initialize_transport" command received from the test
	/// manager to address multiple uEs.
	/// @param[in,out] jsonData The JSON data of the command.
	/// @return The status of the command handling.
	uprotocol::v1::UStatus handleCreateTransportCommand(
	    rapidjson::Document& jsonData);

	/// @brief Handles the "sendCommand" command received from the test manager.
	/// @param[in,out] jsonData The JSON data of the command.
	/// @return The status of the command handling.
	uprotocol::v1::UStatus handleSendCommand(rapidjson::Document& jsonData);

	/// @brief Handles the "registerListener" command received from the test
	/// manager.
	/// @param[in,out] jsonData The JSON data of the command.
	/// @return The status of the command handling.
	uprotocol::v1::UStatus handleRegisterListenerCommand(
	    rapidjson::Document& jsonData);

	/// @brief Handles the "invokeMethod" command received from the test
	/// manager.
	/// @param[in,out] jsonData A rapidjson::Document object containing the
	/// command's JSON data. The JSON structure should include attributes.sink,
	/// attributes.payload_format, and the payload.
	/// @return uprotocol::v1::UStatus The status of the operation, indicating
	/// success or failure.
	uprotocol::v1::UStatus handleInvokeMethodCommand(
	    rapidjson::Document& jsonData);

	/// @brief Handles the "rpcserver" command received from the test
	/// manager.
	/// @param[in,out] jsonData A rapidjson::Document object containing the
	/// command's JSON data. The JSON structure should include attributes.sink,
	/// attributes.payload_format, and the payload.
	/// @return uprotocol::v1::UStatus The status of the operation, indicating
	/// success or failure.
	uprotocol::v1::UStatus handleRpcServerCommand(
	    rapidjson::Document& jsonData);

	/// @brief Handles the "publisher" command received from the test
	/// manager.
	/// @param[in,out] jsonData A rapidjson::Document object containing the
	/// command's JSON data. The JSON structure should include attributes.sink,
	/// attributes.payload_format, and the payload.
	/// @return uprotocol::v1::UStatus The status of the operation, indicating
	/// success or failure.
	uprotocol::v1::UStatus handlePublisherCommand(
	    rapidjson::Document& jsonData);

	/// @brief Handles the "subscribe" command received from the test manager.
	/// @param[in,out] jsonData A rapidjson::Document object containing the
	/// command's JSON data. The JSON structure should include uri.
	/// @return uprotocol::v1::UStatus The status of the operation, indicating
	/// success or failure.
	uprotocol::v1::UStatus handleSubscriberCommand(
	    rapidjson::Document& jsonData);

	/// @brief Handles the "notificationsource" command received from the test
	/// manager. uses default uri from tranport
	/// @param[in,out] jsonData A rapidjson::Document object containing the
	/// command's JSON data. The JSON structure should include attributes.sink,
	/// attributes.payload_format, and the payload.
	/// @return uprotocol::v1::UStatus The status of the operation, indicating
	/// success or failure.
	uprotocol::v1::UStatus handleNotificationSourceCommand(
	    rapidjson::Document& jsonData);

	/// @brief Handles the "notificationsink" command received from the test
	/// manager. uses default uri from tranport
	/// @param[in,out] jsonData A rapidjson::Document object containing the
	/// command's JSON data. The JSON structure should include uri.
	/// @return uprotocol::v1::UStatus The status of the operation, indicating
	/// success or failure.
	uprotocol::v1::UStatus handleNotificationSinkCommand(
	    rapidjson::Document& jsonData);

private:
	// Default source uri for transport
	uprotocol::v1::UUri def_src_uuri_;

	// Transport type
	std::string transportType_;

	// The transport layer used for communication.
	std::shared_ptr<uprotocol::transport::UTransport> transportPtr_;

	// The map of uri to callback handle
	std::unordered_multimap<std::string, CommunicationVariantType>
	    uriCallbackMap_;

	// The vector of RpcClient::InvokeHandle
	std::vector<uprotocol::communication::RpcClient::InvokeHandle>
	    rpcClientHandles_;

	/// @brief add communatication handle to uriCallbackMap_.
	/// @param handel A rvalue reference to a variant type representing the
	/// callback handle.
	/// @param uri A constant reference to a UUri object representing the URI
	/// for which the callback is being registered.
	/// @return Returns a UStatus object indicating the success or failure of
	/// adding the handle to the URI callback map.
	uprotocol::v1::UStatus addHandleToUriCallbackMap(
	    CommunicationVariantType&& handel, const uprotocol::v1::UUri& uri);

	/// @brief Creates a transport layer object based on the specified transport
	/// type.
	/// @param[in] uri The default uri for transport.
	/// @return A shared pointer to the created transport layer object.
	std::shared_ptr<uprotocol::transport::UTransport> createTransport(
	    const uprotocol::v1::UUri& uri);
};

#endif  //_API_WRAPPER_H_
