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

#include "SocketUTransport.h"
#include <spdlog/spdlog.h>
#include <up-cpp/uri/validator/UriValidator.h>
#include <up-cpp/uuid/factory/Uuidv8Factory.h>

const UUri SocketUTransport::RESPONSE_URI =
    BuildUUri()
        .setEntity(
            BuildUEntity().setName("test_agent_cpp").setMajorVersion(1).build())
        .setResource(BuildUResource().setRpcResponse().build())
        .build();

SocketUTransport::SocketUTransport() {
  struct sockaddr_in serv_addr;
  if ((socketFd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
    spdlog::error(
        "SocketUTransport::SocketUTransport():{}, Socket creation error",
        __LINE__);
    exit(EXIT_FAILURE);
  }

  serv_addr.sin_family = AF_INET;
  serv_addr.sin_port = htons(DISPATCHER_PORT);

  if (inet_pton(AF_INET, DISPATCHER_IP, &serv_addr.sin_addr) <= 0) {
    spdlog::error("SocketUTransport::SocketUTransport():{}, Invalid address/ "
                  "Address not supported",
                  __LINE__);
    exit(EXIT_FAILURE);
  }

  if (connect(socketFd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
    spdlog::error(
        "SocketUTransport::SocketUTransport():{}, Socket connection Failed",
        __LINE__);
    exit(EXIT_FAILURE);
  }

  processThread = std::thread(&SocketUTransport::listen, this);
}

SocketUTransport::~SocketUTransport() {}

void SocketUTransport::listen() {
  while (true) {
    try {
      char buffer[BYTES_MSG_LENGTH];
      int readSize = read(socketFd, buffer, sizeof(buffer));
      if (readSize < 0) {
        spdlog::error("SocketUTransport::listen():{}, Read error", __LINE__);
        close(socketFd);
        return;
      } else if (readSize == 0) {
        spdlog::warn("SocketUTransport::listen():{}, Received zero bytes",
                     __LINE__);
        continue;
      }

      UMessage umsg;
      if (!umsg.ParseFromArray(buffer, readSize)) {
        spdlog::error("SocketUTransport::listen():{}, Error parsing UMessage",
                      __LINE__);
        continue;
      }

      spdlog::debug(
          "SocketUTransport::listen():{}, Received uMessage:{}, size is {}",
          __LINE__, umsg.DebugString(), readSize);

      auto attributes = umsg.attributes();
      if (attributes.type() ==
          uprotocol::v1::UMessageType::UMESSAGE_TYPE_PUBLISH)
        handlePublishMessage(umsg);
      else if (attributes.type() ==
               uprotocol::v1::UMessageType::UMESSAGE_TYPE_REQUEST)
        handleRequestMessage(umsg);
      else if (attributes.type() ==
               uprotocol::v1::UMessageType::UMESSAGE_TYPE_RESPONSE)
        handleResponseMessage(umsg);

    } catch (const std::exception &e) {
      spdlog::error("SocketUTransport::listen():{}, Exception: {}", __LINE__,
                    e.what());
    }
  }
}

UStatus SocketUTransport::send(
    const uprotocol::utransport::UMessage &transportUMessage) {
  uprotocol::v1::UPayload payV1;
  payV1.set_value(transportUMessage.payload().data(),
                  transportUMessage.payload().size());
  payV1.set_format(
      (uprotocol::v1::UPayloadFormat)transportUMessage.payload().format());

  UMessage umsg;
  umsg.mutable_payload()->CopyFrom(payV1);
  umsg.mutable_attributes()->CopyFrom(transportUMessage.attributes());

  spdlog::debug(
      "SocketUTransport::send():{}, UMessage in string format is : {}",
      __LINE__, umsg.DebugString());

  size_t serializedSize = umsg.ByteSizeLong();
  std::string umsgSerialized(serializedSize, '\0');
  bool ret = umsg.SerializeToArray(umsgSerialized.data(), serializedSize);
  spdlog::debug("SocketUTransport::send():{}, Serialized UMessage is {}",
                __LINE__, umsgSerialized);

  UStatus status;
  status.set_code(UCode::OK);
  status.set_message("OK");

  if (::send(socketFd, umsgSerialized.c_str(), serializedSize, 0) < 0) {
    spdlog::error("SocketUTransport::send():{}, Error sending UMessage",
                  __LINE__);
    status.set_code(UCode::INTERNAL);
    status.set_message("Sending data in socket failed.");
    return status;
  }

  return status;
}

UStatus SocketUTransport::registerListener(
    const UUri &topic, const uprotocol::utransport::UListener &listener) {
  UStatus status;
  status.set_code(UCode::INTERNAL);

  if (valid_uri(LongUriSerializer::serialize(topic))) {
    spdlog::debug("SocketUTransport::registerListener():{}, found valid_uri",
                  __LINE__);
    status.set_code(UCode::OK);
    status.set_message("OK");
    auto uriHash =
        std::hash<std::string>{}(LongUriSerializer::serialize(topic));
    std::vector<const uprotocol::utransport::UListener *> &vec =
        uriToListener[uriHash];
    if (!vec.empty())
      vec.push_back(&listener);
    else {
      std::vector<const uprotocol::utransport::UListener *> vec1;
      vec1.push_back(&listener);
      uriToListener[uriHash] = vec1;
    }
  } else {
    spdlog::warn(
        "SocketUTransport::registerListener():{}, Received invalid URI",
        __LINE__);
    status.set_message("Received invalid URI");
  }

  return status;
}

UStatus SocketUTransport::unregisterListener(
    const UUri &topic, const uprotocol::utransport::UListener &listener) {
  UStatus status;
  status.set_code(UCode::INTERNAL);

  if (valid_uri(LongUriSerializer::serialize(topic))) {
    auto uriHash =
        std::hash<std::string>{}(LongUriSerializer::serialize(topic));
    std::vector<const uprotocol::utransport::UListener *> &vec =
        uriToListener[uriHash];

    auto it = std::find_if(vec.begin(), vec.end(),
                           [&](const uprotocol::utransport::UListener *item) {
                             return item == &listener;
                           });
    if (it != vec.end()) {
      spdlog::debug("SocketUTransport::unregisterListener():{}, found listner "
                    "and removing the same.",
                    __LINE__);
      vec.erase(it);
      status.set_code(UCode::OK);
      status.set_message("OK");
    } else {
      status.set_code(UCode::NOT_FOUND);
      status.set_message("Listener not found for the given UUri");
      spdlog::warn("SocketUTransport::unregisterListener():{}, Listener not "
                   "found for the given UUri",
                   __LINE__);
    }
  } else {
    status.set_message("Received invalid URI");
    spdlog::warn(
        "SocketUTransport::unregisterListener():{}, Received invalid URI",
        __LINE__);
  }
  return status;
}

void SocketUTransport::timeout_counter(
    const UUID &req_id,
    const std::future<uprotocol::rpc::RpcResponse> &resFuture,
    std::promise<uprotocol::rpc::RpcResponse> &promise, const int timeout) {
  try {
    int timeinsecs = timeout / 1000;
    // std::cout << "SocketUTransport::timeout_counter(),  going to sleep for "
    // << timeinsecs << " seconds" << std::endl;
    std::this_thread::sleep_for(std::chrono::seconds(timeinsecs));
    // std::cout << "SocketUTransport::timeout_counter(),  sleep is done" <<
    // std::endl;
    std::lock_guard<std::mutex> lock(mutex_promise);
    if (!resFuture.valid()) {
      auto uuidStr = UuidSerializer::serializeToString(req_id);
      promise.set_exception(std::make_exception_ptr(
          std::runtime_error("Not received response for request " + uuidStr +
                             " within " + std::to_string(timeout) + " ms")));
    } else {
      spdlog::debug(
          "SocketUTransport::timeout_counter():{}, response future is valid",
          __LINE__);
    }
  } catch (const std::exception &e) {
    spdlog::error("SocketUTransport::timeout_counter():{}, Exception received "
                  "in thread: {}",
                  __LINE__, e.what());
  }
}

std::future<uprotocol::rpc::RpcResponse>
SocketUTransport::invokeMethod(const UUri &topic,
                               const uprotocol::utransport::UPayload &payload,
                               const CallOptions &options) {
  spdlog::debug("SocketUTransport::invokeMethod():{}, called", __LINE__);
  std::promise<uprotocol::rpc::RpcResponse> promise;
  std::future<uprotocol::rpc::RpcResponse> responseFuture =
      promise.get_future();

  int timeout = options.ttl();
  auto attr = uprotocol::utransport::UAttributesBuilder::request(
                  RESPONSE_URI, topic, UPriority::UPRIORITY_CS4, timeout)
                  .build();
  auto requestId = attr.id();
  auto uuidStr = UuidSerializer::serializeToString(requestId);
  reqidToFutureUMessage[uuidStr] = std::move(promise);

  std::thread timeoutThread(std::bind(&SocketUTransport::timeout_counter, this,
                                      requestId, std::ref(responseFuture),
                                      std::ref(reqidToFutureUMessage[uuidStr]),
                                      timeout));
  timeoutThread.detach();

  auto reqPaylod = payload;
  uprotocol::utransport::UMessage transportUMessage(reqPaylod, attr);
  send(transportUMessage);

  return responseFuture;
}

uprotocol::v1::UStatus SocketUTransport::invokeMethod(
    const UUri &topic, const uprotocol::utransport::UPayload &payload,
    const CallOptions &options,
    const uprotocol::utransport::UListener &callback) {
  UStatus status;
  status.set_code(UCode::UNIMPLEMENTED);
  status.set_message("Not Implemented");

  return status;
}

void SocketUTransport::handlePublishMessage(const UMessage umsg) {
  UUri uri = umsg.attributes().source();
  notifyListeners(uri, umsg);
}

void SocketUTransport::handleRequestMessage(const UMessage umsg) {
  UUri uri = umsg.attributes().sink();
  notifyListeners(uri, umsg);
}

void SocketUTransport::handleResponseMessage(const UMessage umsg) {
  UUID requestId = umsg.attributes().reqid();
  auto uuidStr = UuidSerializer::serializeToString(requestId);
  auto it = reqidToFutureUMessage.find(uuidStr);
  if (it != reqidToFutureUMessage.end()) {
    uprotocol::v1::UPayload pay = umsg.payload();
    string str = pay.value();
    spdlog::debug("SocketUTransport::handleResponseMessage():{}, payload is {}",
                  __LINE__, str);
    uprotocol::utransport::UPayload payload(
        (const unsigned char *)str.c_str(), str.length(),
        uprotocol::utransport::UPayloadType::VALUE);
    payload.setFormat((uprotocol::utransport::UPayloadFormat)pay.format());

    std::lock_guard<std::mutex> lock(mutex_promise);
    uprotocol::rpc::RpcResponse rpcResponse;
    rpcResponse.message.setPayload(payload);
    auto reqAttributes = umsg.attributes();
    rpcResponse.message.setAttributes(reqAttributes);
    rpcResponse.status.set_code(UCode::OK);

    it->second.set_value(rpcResponse);
    reqidToFutureUMessage.erase(it);
  } else {
    spdlog::error("SocketUTransport::handleResponseMessage():{}, Request ID {} "
                  "not found.",
                  __LINE__, uuidStr);
  }
}

void SocketUTransport::notifyListeners(const UUri uri, const UMessage umsg) {
  std::lock_guard<std::mutex> lock(mutex_);
  auto uriHash = std::hash<std::string>{}(LongUriSerializer::serialize(uri));
  std::vector<const uprotocol::utransport::UListener *> &listeners =
      uriToListener[uriHash];
  if (!listeners.empty()) {
    for (const auto listener : listeners) {
      uprotocol::v1::UPayload pay = umsg.payload();
      string str = pay.value();
      spdlog::debug("SocketUTransport::notifyListeners():{}, payload is {}",
                    __LINE__, str);
      uprotocol::utransport::UPayload payload(
          (const unsigned char *)str.c_str(), str.length(),
          uprotocol::utransport::UPayloadType::VALUE);
      payload.setFormat((uprotocol::utransport::UPayloadFormat)pay.format());

      auto reqAttributes = umsg.attributes();
      uprotocol::utransport::UMessage transportUMessage(payload, reqAttributes);
      listener->onReceive(transportUMessage);
    }
  } else {
    spdlog::warn("SocketUTransport::notifyListeners():{}, Uri not found in "
                 "Listener Map, discarding...",
                 __LINE__);
  }
}
