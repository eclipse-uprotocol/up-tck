#include "utils/JsonParser.hpp"
#include <fstream>
#include <filesystem>
#include <rapidjson/istreamwrapper.h>
//#include <uStreamer/utils/Logger.hpp>


/**
 * @brief @see @ref JsonParser::getValueString
 * @param @return value string - @see @ref JsonParser::getValueString
 */
std::string JsonParser::getValueString(const rapidjson::Value& member, const std::string& memberName) {
    if (member.HasMember(memberName.c_str()) && member[memberName.c_str()].IsString()) {
        return member[memberName.c_str()].GetString();
    } else {
        spdlog::error("Failed to parse " + memberName);
        return "";
    }
}

/**
 * @brief @see @ref JsonParser::getValue
 * @tparam T The type to which the value should be converted.
 * @param @return The converted value if successful, otherwise 0 - @see @ref JsonParser::getValue
 */
template<typename T>
T JsonParser::getValue(const rapidjson::Value& member, const std::string& memberName, int8_t numBase) {
    if (member.HasMember(memberName.c_str()) && member[memberName.c_str()].IsString()) {
        return static_cast<T>(std::stoul(member[memberName.c_str()].GetString(), nullptr, numBase));
    } else {
        spdlog::warn("Failed to parse " + memberName);
        return 0;
    }
}

/**
 * Converts a string value from a JSON member to an unsigned 32-bit integer.
 *
 * @param member The JSON member containing the string value.
 * @param memberName The name of the JSON member.
 * @return The converted unsigned 32-bit integer value.
 */
uint32_t JsonParser::convertStrToUint32(const rapidjson::Value& member, const std::string& memberName) {
    std::string valueStr = getValueString(member, memberName);
    int8_t NUM_BASE = (valueStr.size() > 2 && (valueStr.substr(0, 2) == "0x" || valueStr.substr(0, 2) == "0X")) ? 16 : 10;
    return getValue<uint32_t>(member, memberName, NUM_BASE);
}

/**
 * @brief @see @ref JsonParser::convertStrToUint16
 * @param @return value uint16 - @see @ref JsonParser::convertStrToUint16
 */
uint16_t JsonParser::convertStrToUint16(const rapidjson::Value& member, const std::string& memberName) {
    std::string valueStr = getValueString(member, memberName);
    int8_t NUM_BASE = (valueStr.size() > 2 && (valueStr.substr(0, 2) == "0x" || valueStr.substr(0, 2) == "0X")) ? 16 : 10;
    return getValue<uint16_t>(member, memberName, NUM_BASE);
}

/**
 * @brief @see @ref JsonParser::convertStrToUint8
 * @param @return value uint16 - @see @ref JsonParser::convertStrToUint8
 */
uint8_t JsonParser::convertStrToUint8(const rapidjson::Value& member, const std::string& memberName) {
    std::string valueStr = getValueString(member, memberName);
    int8_t NUM_BASE = (valueStr.size() > 2 && (valueStr.substr(0, 2) == "0x" || valueStr.substr(0, 2) == "0X")) ? 16 : 10;
    return getValue<uint8_t>(member, memberName, NUM_BASE);
}

/**
 * @brief @see @ref JsonParser::getUriList
 * @param @return value pointer uriList vector - @see @ref JsonParser::getUriList
 */
uprotocol::v1::UUri JsonParser::parseUri(rapidjson::Value const &jsonUri) {

    spdlog::info("{}", __FUNCTION__);

    auto uAuthority = uprotocol::uri::BuildUAuthority();
    auto uEntity = uprotocol::uri::BuildUEntity();
    auto uResource = uprotocol::uri::BuildUResource();
         
    for (auto& member : jsonUri.GetObject()) {
        if (member.name == "authority") {
            const auto& authority = member.value;
            uAuthority.setName(getValueString(authority, "name"));
            uAuthority.setIp(getValueString(authority, "ip"));
            uAuthority.setId(getValueString(authority, "id"));
            
        } else if (member.name == "entity") {
            const auto& entity = member.value;
            uEntity.setName(getValueString(entity, "name"));
            uEntity.setId(convertStrToUint16(entity, "id"));
            uEntity.setMajorVersion(convertStrToUint32(entity, "version_major"));
            uEntity.setMinorVersion(convertStrToUint32(entity, "version_minor"));
        } else if (member.name == "resource") {
            const auto& resource = member.value;
            uResource.setID(convertStrToUint16(resource, "id"));
            uResource.setName(getValueString(resource, "name"));
            uResource.setInstance(getValueString(resource, "instance"));
        }
    }   
    //build uri
    auto uri = uprotocol::uri::BuildUUri().setAutority(uAuthority.build()).setEntity(uEntity.build()).setResource(uResource.build()).build();
    return uri;

}

std::string JsonParser::convertUStatusToString(uprotocol::v1::UStatus status) {
    std::string status_str;
    switch (status.code()) {
        case uprotocol::v1::UCode::OK:
            status_str = "OK";
            break;
        case uprotocol::v1::UCode::NOT_FOUND:
            status_str = "NOT_FOUND";
            break;
        case uprotocol::v1::UCode::INVALID_ARGUMENT:
            status_str = "INVALID_ARGUMENT";
            break;
        case uprotocol::v1::UCode::ALREADY_EXISTS:
            status_str = "ALREADY_EXISTS";
            break;
        case uprotocol::v1::UCode::PERMISSION_DENIED:
            status_str = "PERMISSION_DENIED";
            break;
        case uprotocol::v1::UCode::UNAUTHENTICATED:
            status_str = "UNAUTHENTICATED";
            break;
        case uprotocol::v1::UCode::UNIMPLEMENTED:
            status_str = "UNIMPLEMENTED";
            break;
        case uprotocol::v1::UCode::UNAVAILABLE:
            status_str = "UNAVAILABLE";
            break;
        case uprotocol::v1::UCode::INTERNAL:
            status_str = "INTERNAL";
            break;
        case uprotocol::v1::UCode::DEADLINE_EXCEEDED:
            status_str = "DEADLINE_EXCEEDED";
            break;
        case uprotocol::v1::UCode::RESOURCE_EXHAUSTED:
            status_str = "RESOURCE_EXHAUSTED";
            break;
        case uprotocol::v1::UCode::CANCELLED:
            status_str = "CANCELLED";
            break;
        case uprotocol::v1::UCode::UNKNOWN:
            status_str = "UNKNOWN";
            break;
        default:
            status_str = "UNKNOWN";
            break;
    }
    return status_str;
}

/**
 * @brief @see @ref JsonParser::convertStrToUMessageType
 * @param @return value UMessageType - @see @ref JsonParser::convertStrToUMessageType
 */
uprotocol::v1::UMessageType JsonParser::convertStrToUMessageType(const std::string& valueStr) {
    if (valueStr == "UMESSAGE_TYPE_PUBLISH") {
        return uprotocol::v1::UMessageType::UMESSAGE_TYPE_PUBLISH;
    } else if (valueStr == "UMESSAGE_TYPE_REQUEST") {
        return uprotocol::v1::UMessageType::UMESSAGE_TYPE_REQUEST;
    } else if (valueStr == "UMESSAGE_TYPE_RESPONSE") {
        return uprotocol::v1::UMessageType::UMESSAGE_TYPE_RESPONSE;
    } else {
       spdlog::warn("Failed to parse " + valueStr);
        return uprotocol::v1::UMessageType::UMESSAGE_TYPE_UNSPECIFIED;
    }
}

uprotocol::v1::UPriority JsonParser::convertStrToUPriority(const std::string& valueStr) {
    if (valueStr == "UPRIORITY_CS0") {
        return uprotocol::v1::UPriority::UPRIORITY_CS0;
    } else if (valueStr == "UPRIORITY_CS1") {
        return uprotocol::v1::UPriority::UPRIORITY_CS1;
    } else if (valueStr == "UPRIORITY_CS2") {
        return uprotocol::v1::UPriority::UPRIORITY_CS2;
    } else if (valueStr == "UPRIORITY_CS3") {
        return uprotocol::v1::UPriority::UPRIORITY_CS3;
    } else if (valueStr == "UPRIORITY_CS4") {
        return uprotocol::v1::UPriority::UPRIORITY_CS4;
    } else if (valueStr == "UPRIORITY_CS5") {
        return uprotocol::v1::UPriority::UPRIORITY_CS5;
    } else if (valueStr == "UPRIORITY_CS6") {
        return uprotocol::v1::UPriority::UPRIORITY_CS6;
    } else {
        spdlog::warn("Failed to parse " + valueStr);
        return uprotocol::v1::UPriority::UPRIORITY_UNSPECIFIED;
    }
}

uprotocol::utransport::UPayloadFormat JsonParser::convertStrToUPayloadFormat(const std::string& valueStr) {
    if (valueStr == "UPAYLOAD_FORMAT_PROTOBUF_WRAPPED_IN_ANY") {
        return uprotocol::utransport::UPayloadFormat::PROTOBUF_WRAPPED_IN_ANY;
    } else if (valueStr == "UPAYLOAD_FORMAT_PROTOBUF") {
        return uprotocol::utransport::UPayloadFormat::PROTOBUF;
    } else if (valueStr == "UPAYLOAD_FORMAT_JSON") {
        return uprotocol::utransport::UPayloadFormat::JSON;
    } else if (valueStr == "UPAYLOAD_FORMAT_SOMEIP") {
        return uprotocol::utransport::UPayloadFormat::SOMEIP;
    } else if (valueStr == "UPAYLOAD_FORMAT_SOMEIP_TLV") {
        return uprotocol::utransport::UPayloadFormat::SOMEIP_TLV;
    } else if (valueStr == "UPAYLOAD_FORMAT_RAW") {
        return uprotocol::utransport::UPayloadFormat::RAW;
    } else if (valueStr == "UPAYLOAD_FORMAT_TEXT") {
        return uprotocol::utransport::UPayloadFormat::TEXT;
    } else {
       spdlog::warn("Failed to parse " + valueStr);
        return uprotocol::utransport::UPayloadFormat::UNSPECIFIED;
    }
}

/**
 * @brief @see @ref JsonParser::parseJSONToUMessage
 * @param @return value UMessage - @see @ref JsonParser::parseJSONToUMessage
 */
uprotocol::utransport::UMessage JsonParser::parseToUMessage() {

   spdlog::info("{}", __FUNCTION__);

    auto uAttributes = uprotocol::utransport::UAttributesBuilder();
    uprotocol::v1::UUri sourceUri;
    uprotocol::v1::UUri sinkUri;
    uprotocol::v1::UUID reqId;
    uprotocol::v1::UMessageType type;
    uprotocol::v1::UPriority priority;
    uprotocol::utransport::UMessage uMessage;

    auto const& uuid = uprotocol::uuid::Uuidv8Factory::create();
    uAttributes.setId(uuid);

    for (auto& member : documentObj_.GetObject()) {
        if (member.name == "attributes") {
            const auto& attributes = member.value;
            //Parse attributes
            for (auto& attr : attributes.GetObject()) {
                if (attr.name == "type") {
                    type = convertStrToUMessageType(attr.value.GetString());
                    uAttributes.setType(type);
                } else if (attr.name == "source") {
                    const auto& sourceObj = attr.value;
                    sourceUri = parseUri(sourceObj);
                    uAttributes.setSource(sourceUri);
                } else if (attr.name == "sink") {
                    const auto& sinkObj = attr.value;
                    sinkUri = parseUri(sinkObj);
                    uAttributes.setSink(sinkUri);
                } else if (attr.name == "priority") {
                    priority = convertStrToUPriority(attr.value.GetString());
                    uAttributes.setPriority(priority);
                } else if (attr.name == "reqid") {
                    const auto& reqIdObj = attr.value;
                    reqId.set_msb(convertStrToUint32(reqIdObj, "msb"));
                    reqId.set_lsb(convertStrToUint32(reqIdObj, "lsb"));
                    uAttributes.setReqid(reqId);
                }
            }
        }
        //Parse payload
        if (member.name == "payload") {
            const auto& payload = member;
            uprotocol::utransport::UPayloadFormat format;
            format = convertStrToUPayloadFormat(getValueString(payload.value, "format"));
            uint8_t value = convertStrToUint8(payload.value, "value");
            auto uPayload = uprotocol::utransport::UPayload(&value, 1, uprotocol::utransport::UPayloadType::VALUE);
            uPayload.setFormat(format);
            uMessage.setPayload(uPayload);
        }
    }
    auto builtUAttributes = uAttributes.build();
    uMessage.setAttributes(builtUAttributes);
    
    return uMessage;

}   