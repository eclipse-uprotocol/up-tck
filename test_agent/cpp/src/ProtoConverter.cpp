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

#include "ProtoConverter.h"

#include <openssl/bio.h>
#include <openssl/buffer.h>
#include <openssl/evp.h>

#include <regex>

using namespace rapidjson;
using namespace google::protobuf;

std::string base64Encode(const std::string& in) {
	BIO* bio;
	BIO* b64;
	BUF_MEM* bufferPtr;

	b64 = BIO_new(BIO_f_base64());
	bio = BIO_new(BIO_s_mem());
	bio = BIO_push(b64, bio);

	// Ignore newlines - write everything in one line
	BIO_set_flags(bio, BIO_FLAGS_BASE64_NO_NL);
	BIO_write(bio, in.c_str(), in.length());
	BIO_flush(bio);
	BIO_get_mem_ptr(bio, &bufferPtr);
	BIO_set_close(bio, BIO_NOCLOSE);
	BIO_free_all(bio);

	std::string encoded(bufferPtr->data, bufferPtr->length);
	BUF_MEM_free(bufferPtr);
	return encoded;
}

std::string base64Decode(const std::string& in) {
	BIO* bio;
	BIO* b64;
	int decodeLen = in.length();
	char* decode = new char[decodeLen];

	bio = BIO_new_mem_buf(in.c_str(), -1);
	b64 = BIO_new(BIO_f_base64());
	bio = BIO_push(b64, bio);

	BIO_set_flags(
	    bio, BIO_FLAGS_BASE64_NO_NL);  // Do not use newlines to flush buffer
	decodeLen = BIO_read(bio, decode, decodeLen);
	decode[decodeLen] = '\0';

	BIO_free_all(bio);

	std::string decoded(decode, decodeLen);
	delete[] decode;
	return decoded;
}

void ProtoConverter::processNested(Value& parentJsonObj,
                                   Document::AllocatorType& allocator) {
	for (auto& m : parentJsonObj.GetObject()) {
		if (m.value.IsObject()) {
			// Recursively process nested object
			processNested(m.value, allocator);
		} else if (m.value.IsString() &&
		           std::string(m.value.GetString()).find("BYTES:") == 0) {
			std::string byteString = std::string(m.value.GetString())
			                             .substr(6);  // Remove 'BYTES:' prefix

			// TODO: Optimize this code to avoid unnecessary base64 encoding
			// Encode the byte string in base64
			std::string base64Encoded = base64Encode(byteString);
			m.value.SetString(
			    base64Encoded.c_str(),
			    static_cast<rapidjson::SizeType>(base64Encoded.length()),
			    allocator);
		}
	}
}

bool isValidBase64(const std::string& input) {
	std::regex base64Pattern("^[A-Za-z0-9+/]+={0,2}$");
	return std::regex_match(input, base64Pattern);
}

void ProtoConverter::dictToProto(Value& parentJsonObj, Message& parentProtoObj,
                                 Document::AllocatorType& allocator) {
	// Process JSON object members
	processNested(parentJsonObj, allocator);
	// Convert parentJsonObj value to string
	rapidjson::StringBuffer buffer;
	rapidjson::Writer<rapidjson::StringBuffer> writer(buffer);
	parentJsonObj.Accept(writer);
	std::string strBuf = buffer.GetString();

	google::protobuf::util::JsonParseOptions options;
	auto status = google::protobuf::util::JsonStringToMessage(
	    strBuf, &parentProtoObj, options);
	if (!status.ok()) {
		spdlog::error("Error during JSON to Message conversion: {}",
		              status.ToString());
	}
}

uprotocol::v1::UUri ProtoConverter::distToUri(
    rapidjson::Value& parentJsonObj,
    rapidjson::Document::AllocatorType& allocator) {
	uprotocol::v1::UUri uri;
	dictToProto(parentJsonObj, uri, allocator);
	return uri;
}

std::optional<uprotocol::v1::UPayloadFormat> ProtoConverter::distToUPayFormat(
    const rapidjson::Value& formatStrValue) {
	if (formatStrValue.IsString()) {
		const std::string formatStr = formatStrValue.GetString();
		const google::protobuf::EnumDescriptor* descriptor =
		    uprotocol::v1::UPayloadFormat_descriptor();
		const google::protobuf::EnumValueDescriptor* value =
		    descriptor->FindValueByName(formatStr);
		if (value) {
			return static_cast<uprotocol::v1::UPayloadFormat>(value->number());
		}
	}
	return std::nullopt;
}

Value ProtoConverter::convertMessageToJson(const Message& message,
                                           Document& doc) {
	std::string jsonString;
	util::JsonPrintOptions options;
	options.preserve_proto_field_names = true;
	util::MessageToJsonString(message, &jsonString, options);

	Document jsonDoc;
	jsonDoc.Parse(jsonString.c_str());

	// TODO: Optimize this code to avoid unnecessary base64 decoding
	if (jsonDoc.HasMember("payload") && jsonDoc["payload"].HasMember("value")) {
		std::string byteString = jsonDoc["payload"]["value"].GetString();
		if (isValidBase64(
		        byteString)) {  // Check if the string is base64 encoded
			std::string base64Decoded = base64Decode(byteString);
			jsonDoc["payload"]["value"].SetString(
			    base64Decoded.c_str(),
			    static_cast<rapidjson::SizeType>(base64Decoded.length()),
			    doc.GetAllocator());
		}
	}

	// Convert the modified JSON document back to a string
	rapidjson::StringBuffer buffer;
	rapidjson::Writer<rapidjson::StringBuffer> writer(buffer);
	jsonDoc.Accept(writer);
	jsonString = buffer.GetString();

	return Value(jsonString.c_str(), jsonString.length(), doc.GetAllocator());
}
