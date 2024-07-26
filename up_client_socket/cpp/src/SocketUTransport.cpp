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

#include <arpa/inet.h>
#include <spdlog/spdlog.h>
#include <sys/socket.h>
#include <up-cpp/datamodel/serializer/UUri.h>

#include <array>
#include <set>
#include <thread>
#include <cctype>
#include <type_traits>
#include <iostream>
#include <sstream>
#include <iomanip>
#include "SafeTupleMap.h"
#include "WakeFd.h"

using namespace uprotocol::v1;
using uprotocol::transport::UTransport;
using namespace std;

string repr(const string& input)
{
	stringstream ss;
	ss << "'" << setfill('0') << hex;
	for (auto c : input) {
		if (isgraph(c)) ss << c;
		else if (c == '\n') {
			ss << "\\n";
		}
		else {
			ss << "\\x" << setw(2) << (int(c) & 0xff);
		}
	}
	ss << "'";
	return ss.str();
}

struct SocketUTransport::Impl {
	struct CallbackData {
		mutex mtx;  // this is to protect set insertion and deletion
		set<CallableConn> listeners;
		optional<UUri> source_filter;
	};

	unique_ptr<WakeFd> wake_fd_;
	thread process_thread_;
	string buffer_;

	using UUriTuple = tuple<
		optional<string>,
		optional<uint32_t>,
	    optional<uint32_t>,
		optional<uint32_t>
		>;

	using CallbackKey = tuple_cat_t<UUriTuple, UUriTuple>;

	SafeTupleMap<CallbackKey, CallbackData> callback_data_;

	//
	// This function is going to map the protobuf fields for a uuri into a tuple suitable for compile time expansion
	//
	static CallbackKey makeCallbackKey(const optional<UUri>& left, const optional<UUri>& right) {
		CallbackKey key;
		if (left) {
			if (left->authority_name() != "*") {
				get<0>(key) = left->authority_name();
			}
			if (left->ue_id() != 0xff) {
				get<1>(key) = left->ue_id();
			}
			if (left->ue_version_major() != 0xffff) {
				get<2>(key) = left->ue_version_major();
			}
			if (left->resource_id() != 0xffff) {
				get<3>(key) = left->resource_id();
			}
		}
		if (right) {
			if (right->authority_name() != "*") {
				get<4>(key) = right->authority_name();
			}
			if (right->ue_id() != 0xff) {
				get<5>(key) = right->ue_id();
			}
			if (right->ue_version_major() != 0xffff) {
				get<6>(key) = right->ue_version_major();
			}
			if (right->resource_id() != 0xffff) {
				get<7>(key) = right->resource_id();
			}
		}
		return key;
	}

	Impl(const std::string& dispatcher_ip, int dispatcher_port) {
		struct sockaddr_in serv_addr;

		if (inet_pton(AF_INET, dispatcher_ip.c_str(), &serv_addr.sin_addr) <=
		    0) {
			spdlog::error(
			    "SocketUTransport::SocketUTransport():{}, Invalid address/ "
			    "Address not supported",
			    __LINE__);
			exit(EXIT_FAILURE);
		}

		int fd;
		if ((fd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
			spdlog::error(
			    "SocketUTransport::SocketUTransport():{}, Socket creation "
			    "error",
			    __LINE__);
			exit(EXIT_FAILURE);
		}

		wake_fd_ = make_unique<WakeFd>(fd);

		serv_addr.sin_family = AF_INET;
		serv_addr.sin_port = htons(dispatcher_port);

		if (wake_fd_->connect((struct sockaddr*)&serv_addr, sizeof(serv_addr)) <
		    0) {
			spdlog::error(
			    "SocketUTransport::SocketUTransport():{}, Socket connection "
			    "Failed",
			    __LINE__);
			exit(EXIT_FAILURE);
		}

		process_thread_ = thread([&]() { dispatcher(); });
	}

	~Impl() {
		wake_fd_->wake();
		process_thread_.join();
	}

	UStatus sendImpl(const UMessage& umsg) {
		cout << "inside sendImpl " << umsg.ShortDebugString() << endl;
		// spdlog::debug(
		//     "SocketUTransport::send():{}, UMessage in string format is : {}",
		//     __LINE__, umsg.DebugString());

		// size_t serializedSize = umsg.ByteSizeLong();
		// string umsgSerialized(serializedSize, '\0');
		// bool ret = umsg.SerializeToArray(umsgSerialized.data(), serializedSize);
		string buf;
		bool ret = umsg.SerializeToString(&buf);
		// spdlog::debug("SocketUTransport::send():{}, Serialized UMessage is {}",
		//               __LINE__, buf);

		UStatus status;
		status.set_code(UCode::OK);
		status.set_message("OK");

		// cout << "sending " << repr(buf) << endl;
		if (wake_fd_->send(buf.c_str(), buf.size(), 0) < 0) {
			spdlog::error("SocketUTransport::send():{}, Error sending UMessage",
			              __LINE__);
			status.set_code(UCode::INTERNAL);
			status.set_message("Sending data in socket failed.");
			return status;
		}

		return status;
	}

	void dispatcher() {
		while (true) {
			try {
				if (wake_fd_->read(buffer_) == false)
					break;

				// cout << "dispatcher received " << repr(buffer_) << endl;
				UMessage umsg;
				try {
					if (!umsg.ParseFromString(buffer_)) {
						spdlog::error(
						    "SocketUTransport::listen():{}, Error parsing "
						    "UMessage",
						    __LINE__);
						continue;
					}
				} catch (const google::protobuf::FatalException& e) {
					spdlog::error(
					    "SocketUTransport::listen():{}, Protobuf exception: {}",
					    __LINE__, e.what());
					continue;
				}

				spdlog::debug(
				    "SocketUTransport::listen():{}, Received uMessage:{}",
				    __LINE__, umsg.DebugString());

				auto& attributes = umsg.attributes();
				auto key = makeCallbackKey(attributes.source(), attributes.sink());
				auto patterns = generateOptionals(key);
				for (const auto& pattern : patterns) {
					// cout << "looking up " << pattern << endl;
					auto ptr = callback_data_.find(pattern);
					if (ptr != nullptr) {
						cout << "matched " << key << endl;
						cout << "to      " << pattern << endl << endl;
						unique_lock<mutex> lock(ptr->mtx);
						for (auto callback : ptr->listeners) {
							callback(umsg);
						}
					}
				}

			} catch (const system_error& e) {
				if (e.code() == errc::io_error) {
					spdlog::error(
					    "SocketUTransport::listen():{}, I/O error: {}",
					    __LINE__, e.what());
				} else {
					throw;  // rethrow the exception if it's not an I/O error
				}
			}
		}
	}

	UStatus registerListenerImpl(const UUri& sink_filter,
	                             CallableConn& listener,
	                             optional<UUri>& source_filter) {
		UStatus retval;
		retval.set_code(UCode::OK);
		auto key = makeCallbackKey(sink_filter, source_filter);
		cout << "inserting " << key << endl;
		auto ptr = callback_data_.find(key, true);
		unique_lock<mutex> lock(ptr->mtx);
		ptr->listeners.insert(listener);
		return retval;
	}

	void cleanupListener(CallableConn listener) {
		callback_data_.erase([&](shared_ptr<CallbackData> ptr) {
			unique_lock<mutex> lock(ptr->mtx);
			ptr->listeners.erase(listener);
		});
	}
};

SocketUTransport::SocketUTransport(const UUri& uuri,
                                   const std::string& dispatcher_ip,
                                   int dispatcher_port)
    : UTransport(uuri), pImpl(new Impl(dispatcher_ip, dispatcher_port)) {}

UStatus SocketUTransport::sendImpl(const UMessage& umsg) {
	return pImpl->sendImpl(umsg);
}

UStatus SocketUTransport::registerListenerImpl(const UUri& sink_filter,
                                               CallableConn&& listener,
                                               optional<UUri>&& source_filter) {
	return pImpl->registerListenerImpl(sink_filter, listener, source_filter);
}

void SocketUTransport::cleanupListener(CallableConn listener) {
	pImpl->cleanupListener(listener);
}
