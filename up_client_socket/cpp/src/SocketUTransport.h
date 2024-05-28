/*
 * Copyright (c) 2023 General Motors GTO LLC
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
 * SPDX-FileCopyrightText: 2023 General Motors GTO LLC
 * SPDX-License-Identifier: Apache-2.0
 */

#ifndef _SOCKET_UTRANSPORT_H_
#define _SOCKET_UTRANSPORT_H_

#include <algorithm>
#include <arpa/inet.h>
#include <cstring>
#include <future>
#include <iostream>
#include <mutex>
#include <netinet/in.h>
#include <optional>
#include <sys/socket.h>
#include <thread>
#include <unistd.h>
#include <unordered_map>
#include <vector>

#include <up-core-api/umessage.pb.h>
#include <up-cpp/rpc/RpcClient.h>
#include <up-cpp/transport/UTransport.h>
#include <up-cpp/transport/builder/UAttributesBuilder.h>
#include <up-cpp/transport/datamodel/UMessage.h>
#include <up-cpp/uri/builder/BuildEntity.h>
#include <up-cpp/uri/builder/BuildUAuthority.h>
#include <up-cpp/uri/builder/BuildUResource.h>
#include <up-cpp/uri/builder/BuildUUri.h>
#include <up-cpp/uri/serializer/LongUriSerializer.h>
#include <up-cpp/utils/ThreadPool.h>
#include <up-cpp/uuid/serializer/UuidSerializer.h>

using namespace std;
using namespace uprotocol::v1;
using namespace uprotocol::uri;
using namespace uprotocol::uuid;
using namespace uprotocol::utils;

/**
 * @class SocketUTransport
 * @brief Represents a socket-based implementation of the UTransport interface
 * and RpcClient interface.
 *
 * The SocketUTransport class provides functionality for sending messages,
 * registering and unregistering listeners, and invoking remote methods over a
 * socket connection. It inherits from the UTransport and RpcClient classes.
 */
class SocketUTransport : public uprotocol::utransport::UTransport,
                         public uprotocol::rpc::RpcClient {
public:
  /**
   * @brief Constructs a SocketUTransport object.
   */
  SocketUTransport();

  /**
   * @brief Destroys the SocketUTransport object.
   */
  ~SocketUTransport();

  // UTransport API's

  /**
   * @brief Sends a UMessage over the transport.
   * @param transportUMessage The UMessage to send.
   * @return The status of the send operation.
   */
  UStatus
  send(const uprotocol::utransport::UMessage &transportUMessage) override;

  /**
   * @brief Registers a listener for a specific topic.
   * @param topic The topic to register the listener for.
   * @param listener The listener to register.
   * @return The status of the registration operation.
   */
  UStatus
  registerListener(const UUri &topic,
                   const uprotocol::utransport::UListener &listener) override;

  /**
   * @brief Unregisters a listener for a specific topic.
   * @param topic The topic to unregister the listener from.
   * @param listener The listener to unregister.
   * @return The status of the unregistration operation.
   */
  UStatus
  unregisterListener(const UUri &topic,
                     const uprotocol::utransport::UListener &listener) override;

  // RpcClient API's

  /**
   * @brief Invokes a remote method asynchronously and returns a future for the
   * response.
   * @param topic The topic of the remote method.
   * @param payload The payload of the remote method.
   * @param options The call options for the remote method.
   * @return A future for the response of the remote method.
   */
  std::future<uprotocol::rpc::RpcResponse>
  invokeMethod(const UUri &topic,
               const uprotocol::utransport::UPayload &payload,
               const CallOptions &options) override;

  /**
   * @brief Invokes a remote method asynchronously and registers a callback for
   * the response.
   * @param topic The topic of the remote method.
   * @param payload The payload of the remote method.
   * @param options The call options for the remote method.
   * @param callback The callback to be invoked when the response is received.
   * @return The status of the invocation operation.
   */
  uprotocol::v1::UStatus
  invokeMethod(const UUri &topic,
               const uprotocol::utransport::UPayload &payload,
               const CallOptions &options,
               const uprotocol::utransport::UListener &callback) override;

private:
  constexpr static const char *DISPATCHER_IP = "127.0.0.1";
  constexpr static const int DISPATCHER_PORT = 44444;
  constexpr static const int BYTES_MSG_LENGTH = 32767;

  static const UUri RESPONSE_URI;

  // static constexpr auto queueSize_ = size_t(20);
  // static constexpr auto maxNumOfCuncurrentRequests_ = size_t(2);
  // std::shared_ptr<ThreadPool> threadPool_;
  std::thread processThread;
  int socketFd;
  std::mutex mutex_;
  std::mutex mutex_promise;

  using uuriKey = size_t;
  using uuidStr = std::string;

  std::unordered_map<uuriKey,
                     std::vector<const uprotocol::utransport::UListener *>>
      uriToListener;
  std::unordered_map<uuidStr, std::promise<uprotocol::rpc::RpcResponse>>
      reqidToFutureUMessage;

  /**
   * @brief Listens for incoming messages on the socket.
   */
  void listen();

  /**
   * @brief Handles a publish message received on the socket.
   * @param umsg The UMessage representing the publish message.
   */
  void handlePublishMessage(UMessage umsg);

  /**
   * @brief Handles a request message received on the socket.
   * @param umsg The UMessage representing the request message.
   */
  void handleRequestMessage(UMessage umsg);

  /**
   * @brief Handles a response message received on the socket.
   * @param umsg The UMessage representing the response message.
   */
  void handleResponseMessage(UMessage umsg);

  /**
   * @brief Notifies the registered listeners for a specific URI about a
   * received message.
   * @param uri The URI of the received message.
   * @param umsg The UMessage representing the received message.
   */
  void notifyListeners(UUri uri, UMessage umsg);

  /**
   * @brief Counts the timeout for a request and handles the future and promise
   * accordingly.
   * @param req_id The UUID of the request.
   * @param resFuture The future for the response.
   * @param promise The promise for the response.
   * @param timeout The timeout value in milliseconds.
   */
  void timeout_counter(UUID &req_id,
                       std::future<uprotocol::rpc::RpcResponse> &resFuture,
                       std::promise<uprotocol::rpc::RpcResponse> &promise,
                       int timeout);
};

#endif /* _SOCKET_UTRANSPORT_H_ */
