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

#ifndef _PROTO_CONVERTER_H_
#define _PROTO_CONVERTER_H_

#include <google/protobuf/any.pb.h>
#include <google/protobuf/descriptor.h>
#include <google/protobuf/message.h>
#include <google/protobuf/util/json_util.h>
#include <google/protobuf/wrappers.pb.h>
#include <rapidjson/document.h>
#include "rapidjson/stringbuffer.h"
#include "rapidjson/writer.h"
#include <string>

using namespace google::protobuf;
using namespace rapidjson;

/**
 * @class ProtoConverter
 * @brief This class provides methods to convert between protobuf messages and JSON.
 */
class ProtoConverter {
public:
	/**
	 * @brief Convert a JSON object to a protobuf message.
	 *
	 * @param [in] parentJsonObj The JSON object to convert.
	 * @param [in/out] parentProtoObj The protobuf message to populate with data from the JSON object.
	 * @param [in] allocator The allocator to use for the conversion.
	 */
	static void dictToProto(Value &parentJsonObj, Message &parentProtoObj, Document::AllocatorType &allocator);

	/**
	 * @brief Convert a protobuf message to a JSON object.
	 *
	 * @param [in] message The protobuf message to convert.
	 * @param [in] doc The JSON document to populate with data from the protobuf message.
	 * @return The populated JSON value.
	 */
	static Value convertMessageToJson(const Message &message, Document &doc);

private:
	/**
	 * @brief Process nested JSON objects.
	 *
	 * @param [in/out] parentJsonObj The JSON object to process.
	 * @param [in] allocator The allocator to use for the processing.
	 */
	static void processNested(Value &parentJsonObj, Document::AllocatorType &allocator);
};

#endif /* _PROTO_CONVERTER_H_ */
