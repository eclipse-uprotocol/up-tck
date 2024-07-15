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

#ifndef _PROTO_CONVERTER_H_
#define _PROTO_CONVERTER_H_

#include <UTransportMock.h>
#include <google/protobuf/util/json_util.h>
#include <google/protobuf/wrappers.pb.h>
#include <rapidjson/document.h>
#include <spdlog/spdlog.h>
#include <uprotocol/v1/uattributes.pb.h>
#include <uprotocol/v1/umessage.pb.h>

#include "rapidjson/stringbuffer.h"
#include "rapidjson/writer.h"

/// @class ProtoConverter
/// @brief This class provides methods to convert between protobuf messages and
/// JSON.
class ProtoConverter {
public:
	/// @brief Convert a JSON object to a protobuf message.
	///
	/// @param [in,out] parentJsonObj The JSON object to convert.
	/// @param [in,out] parentProtoObj The protobuf message to populate with
	/// data from the JSON object.
	/// @param [in,out] allocator The allocator to use for the conversion.
	static void dictToProto(rapidjson::Value& parentJsonObj,
	                        google::protobuf::Message& parentProtoObj,
	                        rapidjson::Document::AllocatorType& allocator);

	static uprotocol::v1::UUri distToUri(
	    rapidjson::Value& parentJsonObj,
	    rapidjson::Document::AllocatorType& allocator);

	static std::optional<uprotocol::v1::UPayloadFormat> distToUPayFormat(
	    const rapidjson::Value& formatStrValue);
	/// @brief Convert a protobuf message to a JSON object.
	///
	/// @param [in] message The protobuf message to convert.
	/// @param [in,out] doc The JSON document to populate with data from the
	/// protobuf message.
	/// @return The populated JSON value.
	static rapidjson::Value convertMessageToJson(
	    const google::protobuf::Message& message, rapidjson::Document& doc);

private:
	/// @brief Process nested JSON objects.
	///
	/// @param [in,out] parentJsonObj The JSON object to process.
	/// @param [in,out] allocator The allocator to use for the processing.
	static void processNested(rapidjson::Value& parentJsonObj,
	                          rapidjson::Document::AllocatorType& allocator);
};

#endif  // _PROTO_CONVERTER_H_
