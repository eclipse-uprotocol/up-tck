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

#include <iostream>
#include <thread>
#include <cstring>
#include <unistd.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <mutex>
#include <optional>
#include <future>
#include <unordered_map>
#include <vector>
#include <algorithm>

#include <up-cpp/transport/UTransport.h>
#include <up-cpp/transport/datamodel/UMessage.h>
#include <up-cpp/rpc/RpcClient.h>
#include <up-cpp/uri/builder/BuildUUri.h>
#include <up-cpp/transport/builder/UAttributesBuilder.h>
#include <up-cpp/uri/builder/BuildEntity.h>
#include <up-cpp/uri/builder/BuildUResource.h>
#include <up-cpp/uri/builder/BuildUAuthority.h>
#include <up-cpp/uri/serializer/LongUriSerializer.h>
#include <up-cpp/uuid/serializer/UuidSerializer.h>
#include <up-cpp/utils/ThreadPool.h>

#include <up-core-api/umessage.pb.h>

using namespace std;
using namespace uprotocol::v1;
using namespace uprotocol::uri;
using namespace uprotocol::uuid;
using namespace uprotocol::utils;

class SocketUTransport : public uprotocol::utransport::UTransport, public uprotocol::rpc::RpcClient {
 public:
  SocketUTransport();
  ~SocketUTransport();
  // UTransport API's
  UStatus send(const uprotocol::utransport::UMessage &transportUMessage) override;
  UStatus registerListener(const UUri& topic, const uprotocol::utransport::UListener& listener) override;
  UStatus unregisterListener(const UUri& topic, const uprotocol::utransport::UListener& listener) override;
  // RpcClient API's
  std::future<uprotocol::rpc::RpcResponse> invokeMethod(const UUri &topic, const uprotocol::utransport::UPayload &payload, 
                                                          const CallOptions &options) override;
  uprotocol::v1::UStatus invokeMethod(const UUri &topic, const uprotocol::utransport::UPayload &payload,
                                                        const CallOptions &options,
                                                        const uprotocol::utransport::UListener &callback) override;

 private:
  constexpr static const char * DISPATCHER_IP = "127.0.0.1";
  constexpr static const int DISPATCHER_PORT = 44444;
  constexpr static const int BYTES_MSG_LENGTH = 32767;
  
  static const UUri RESPONSE_URI ;

  //static constexpr auto queueSize_ = size_t(20);
  //static constexpr auto maxNumOfCuncurrentRequests_ = size_t(2);
  //std::shared_ptr<ThreadPool> threadPool_;
  std::thread processThread;
  int socketFd;
  std::mutex mutex_;
  std::mutex mutex_promise;

  using uuriKey = size_t;
  using uuidStr = std::string;

  std::unordered_map<uuriKey, std::vector<const uprotocol::utransport::UListener *>> uriToListener;
  std::unordered_map<uuidStr, std::promise<uprotocol::rpc::RpcResponse>> reqidToFutureUMessage;

  void listen();
  void handlePublishMessage(UMessage umsg);
  void handleRequestMessage(UMessage umsg);
  void handleResponseMessage(UMessage umsg);
  void notifyListeners(UUri uri, UMessage umsg);

  void timeout_counter(UUID &req_id, std::future<uprotocol::rpc::RpcResponse>& resFuture,
		  std::promise<uprotocol::rpc::RpcResponse>& promise, int timeout);
};


#endif /* _SOCKET_UTRANSPORT_H_ */
