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

#ifndef UTILS_H
#define UTILS_H

#include <Constants.h>
#include <up-cpp/communication/NotificationSink.h>
#include <up-cpp/communication/NotificationSource.h>
#include <up-cpp/communication/Publisher.h>
#include <up-cpp/communication/RpcClient.h>
#include <up-cpp/communication/RpcServer.h>
#include <up-cpp/communication/Subscriber.h>

#include <variant>

/// @brief Alias for a variant type used in communication mechanisms.
/// This variant encompasses different types of communication handles and
/// objects, including listen handles, subscribers, RPC clients, publishers,
/// notification sources, notification sinks, and RPC servers.
using CommunicationVariantType =
    std::variant<uprotocol::transport::UTransport::ListenHandle,
                 std::unique_ptr<uprotocol::communication::Subscriber>,
                 uprotocol::communication::RpcClient,
                 uprotocol::communication::Publisher,
                 uprotocol::communication::NotificationSource,
                 std::unique_ptr<uprotocol::communication::NotificationSink>,
                 std::unique_ptr<uprotocol::communication::RpcServer>>;

/// Utility namespace for operations on a multimap that stores serialized URIs
/// and communication variant types.
namespace MultiMapUtils {

/// @brief Checks for the existence of a key-value pair in the multimap or adds
/// it if not present.
/// @details Iterates through the multimap to find an existing key-value pair
/// matching the specified key (serializedUri) and value type (T). If not found,
/// the new value (newClientOrSource) is added to the multimap under the given
/// key.
/// @param map The multimap to check or modify.
/// @param serializedUri The key under which to check or add the value.
/// @param newClientOrSource The value to add if no matching key-value pair is
/// found.
template <typename T>
void checkOrAdd(
    std::unordered_multimap<std::string, CommunicationVariantType>& map,
    const std::string& serializedUri, T newClientOrSource) {
	auto range = map.equal_range(serializedUri);
	for (auto it = range.first; it != range.second; ++it) {
		if (std::holds_alternative<T>(it->second)) {
			return;  // Found an existing client/source
		}
	}
	// Add the new handle to the map
	map.emplace(serializedUri, std::move(newClientOrSource));
}

/// @brief Checks if a specified key-value type pair exists in the multimap.
/// @details Iterates through the multimap to find a key-value pair matching the
/// specified key (serializedUri) and value type (T). Returns true if such a
/// pair is found, false otherwise.
/// @param map The multimap to search through.
/// @param serializedUri The key to search for in the multimap.
/// @return True if a matching key-value type pair is found, false otherwise.
template <typename T>
bool checkKeyValueType(
    std::unordered_multimap<std::string, CommunicationVariantType>& map,
    const std::string& serializedUri) {
	auto range = map.equal_range(serializedUri);

	if (range.first != map.end()) {
		for (auto it = range.first; it != range.second; ++it) {
			if (std::holds_alternative<T>(it->second)) {
				return true;  // Found the specified type
			}
		}
	}

	return false;
}

}  // namespace MultiMapUtils

#endif  // UTILS_H
