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

#include <up-cpp/transport/UTransport.h>

#include <memory>
#include <string>

/// @class SocketUTransport
/// @brief Represents a socket-based implementation of the UTransport interface
/// and RpcClient interface.
///
/// The SocketUTransport class provides functionality for sending messages,
/// registering and unregistering listeners, and invoking remote methods over a
/// socket connection. It inherits from the UTransport and RpcClient classes.
class SocketUTransport : public uprotocol::transport::UTransport {
public:
	/// @brief Constructs a SocketUTransport object.
	SocketUTransport(const uprotocol::v1::UUri&);

private:
	[[nodiscard]] uprotocol::v1::UStatus sendImpl(
	    const uprotocol::v1::UMessage& message) override;

	[[nodiscard]] uprotocol::v1::UStatus registerListenerImpl(
	    const uprotocol::v1::UUri& sink_filter, CallableConn&& listener,
	    std::optional<uprotocol::v1::UUri>&& source_filter) override;

	void cleanupListener(CallableConn listener) override;

	struct Impl;
	std::shared_ptr<Impl> pImpl;
};

#endif  // _SOCKET_UTRANSPORT_H_
