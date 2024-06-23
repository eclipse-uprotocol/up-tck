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

#ifndef _SOCKET_UTRANSPORT_H_
#define _SOCKET_UTRANSPORT_H_

#include <unistd.h>
#include <up-core-api/umessage.pb.h>
#include <up-cpp/rpc/RpcClient.h>
#include <up-cpp/transport/UTransport.h>
#include <up-cpp/transport/builder/UAttributesBuilder.h>
#include <up-cpp/uri/builder/BuildUUri.h>
#include <up-cpp/utils/ThreadPool.h>
#include <up-cpp/uuid/factory/Uuidv8Factory.h>
#include <up-cpp/uuid/serializer/UuidSerializer.h>

/// @class SocketUTransport
/// @brief Represents a socket-based implementation of the UTransport interface
/// and RpcClient interface.
///
/// The SocketUTransport class provides functionality for sending messages,
/// registering and unregistering listeners, and invoking remote methods over a
/// socket connection. It inherits from the UTransport and RpcClient classes.
class SocketUTransport : public uprotocol::utransport::UTransport,
                         public uprotocol::rpc::RpcClient {
public:
	/// @brief Constructs a SocketUTransport object.
	SocketUTransport();

	/// @brief Destroys the SocketUTransport object.
	~SocketUTransport();

	/// UTransport API's

	/// @brief Sends a UMessage over the transport.
	/// @param[in] transportUMessage The UMessage to send.
	/// @return The status of the send operation.
	uprotocol::v1::UStatus send(
	    const uprotocol::utransport::UMessage& transportUMessage) override;

	/// @brief Registers a listener for a specific topic.
	/// @param[in] topic The topic to register the listener for.
	/// @param[in] listener The listener to register.
	/// @return The status of the registration operation.
	uprotocol::v1::UStatus registerListener(
	    const uprotocol::v1::UUri& topic,
	    const uprotocol::utransport::UListener& listener) override;

	/// @brief Unregisters a listener for a specific topic.
	/// @param[in] topic The topic to unregister the listener from.
	/// @param[in] listener The listener to unregister.
	/// @return The status of the unregistration operation.
	uprotocol::v1::UStatus unregisterListener(
	    const uprotocol::v1::UUri& topic,
	    const uprotocol::utransport::UListener& listener) override;

	/// @brief Invokes a remote method asynchronously and returns a future for
	/// the response.
	/// @param[in] topic The topic of the remote method.
	/// @param[in] payload The payload of the remote method.
	/// @param[in] options The call options for the remote method.
	/// @return A future for the response of the remote method.
	std::future<uprotocol::rpc::RpcResponse> invokeMethod(
	    const uprotocol::v1::UUri& topic,
	    const uprotocol::utransport::UPayload& payload,
	    const uprotocol::v1::CallOptions& options) override;

	/// @brief Invokes a remote method asynchronously and registers a callback
	/// for the response.
	/// @param[in] topic The topic of the remote method.
	/// @param[in] payload The payload of the remote method.
	/// @param[in] options The call options for the remote method.
	/// @param[in] callback The callback to be invoked when the response is
	/// received.
	/// @return The status of the invocation operation.
	uprotocol::v1::UStatus invokeMethod(
	    const uprotocol::v1::UUri& topic,
	    const uprotocol::utransport::UPayload& payload,
	    const uprotocol::v1::CallOptions& options,
	    const uprotocol::utransport::UListener& callback) override;

private:
	// The IP address of the dispatcher.
	constexpr static const char* DISPATCHER_IP = "127.0.0.1";
	// The port number of the dispatcher.
	constexpr static const int DISPATCHER_PORT = 44444;
	// The maximum length of a message in bytes.
	constexpr static const int BYTES_MSG_LENGTH = 32767;

	static const uprotocol::v1::UUri RESPONSE_URI;  // The URI for responses.
	std::thread processThread;  // The thread for processing messages.
	std::thread timeoutThread;  // The thread for handling timeouts.
	int socketFd;               // The file descriptor for the socket.
	std::mutex mutex_;          // A mutex for thread synchronization.
	std::mutex mutex_promise;   // A mutex for synchronizing access to promises.

	// A type alias for the key used in the uriToListener map.
	using uuriKey = size_t;
	// A type alias for the key used in the reqidToFutureUMessage map.
	using uuidStr = std::string;

	// A map from URIs to listeners. Each URI can have multiple listeners.
	std::unordered_map<uuriKey,
	                   std::vector<const uprotocol::utransport::UListener*>>
	    uriToListener;

	// A map from request IDs to futures. Each request ID corresponds to a
	// future for a UMessage.
	std::unordered_map<uuidStr, std::promise<uprotocol::rpc::RpcResponse>>
	    reqidToFutureUMessage;

	/// @brief Listens for incoming messages on the socket.
	void listen();

	/// @brief Handles a publish message received on the socket.
	/// @param[in] umsg The UMessage representing the publish message.
	void handlePublishMessage(const uprotocol::v1::UMessage umsg);

	/// @brief Handles a request message received on the socket.
	/// @param[in] umsg The UMessage representing the request message.
	void handleRequestMessage(const uprotocol::v1::UMessage umsg);

	/// @brief Handles a response message received on the socket.
	/// @param[in] umsg The UMessage representing the response message.
	void handleResponseMessage(const uprotocol::v1::UMessage umsg);

	/// @brief Notifies the registered listeners for a specific URI about a
	/// received message.
	/// @param[in] uri The URI of the received message.
	/// @param[in] umsg The UMessage representing the received message.
	void notifyListeners(const uprotocol::v1::UUri uri,
	                     const uprotocol::v1::UMessage umsg);

	/// @brief Counts the timeout for a request and handles the future and
	/// promise accordingly.
	/// @param[in] req_id The UUID of the request.
	/// @param[in] resFuture The future for the response.
	/// @param[in,out] promise The promise for the response.
	/// @param[in] timeout The timeout value in milliseconds.
	void timeout_counter(
	    const uprotocol::uuid::UUID& req_id,
	    const std::future<uprotocol::rpc::RpcResponse>& resFuture,
	    std::promise<uprotocol::rpc::RpcResponse>& promise,
	    const std::chrono::milliseconds timeout);
};

#endif  // _SOCKET_UTRANSPORT_H_
