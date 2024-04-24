#include <string>
#include <rapidjson/document.h>
#include <vector>
#include "up-cpp/uri/builder/BuildUUri.h"
#include "up-cpp/uri/builder/BuildEntity.h"
#include "up-cpp/uri/builder/BuildUResource.h"
#include "up-cpp/uri/builder/BuildUAuthority.h"
#include "up-cpp/transport/builder/UAttributesBuilder.h"
#include <up-cpp/transport/UTransport.h>
#include <spdlog/spdlog.h>



//using namespace uprotocol::v1;

/**
 * @class JsonParser
 * @brief A class for parsing JSON files using the rapidjson library.
 */
class JsonParser {
public:

    /**
     * @brief Retrieves the value of a member in the JSON document as a string.
     * @param member The JSON member to retrieve the value from.
     * @param memberName The name of the member.
     * @return The value of the member as a string.
     */
    std::string getValueString(const rapidjson::Value& member, const std::string& memberName);

    std::string convertUStatusToString(uprotocol::v1::UStatus status);

    /**
     * Retrieves a list of URIs for a given service type.
     *
     * @param serviceType The service type for which to retrieve the URIs.
     * @return A shared pointer to a vector of shared pointers to UUri objects representing the URIs.
     */
    uprotocol::v1::UUri parseUri(rapidjson::Value const &jsonUri);

    /**
     * @brief Represents a UMessage in the uprotocol::v1 namespace.
     * 
     * The UMessage class is responsible for representing a UMessage, which is used in the uprotocol::v1 namespace.
     * It provides functionality for parsing JSON data into a UMessage object.
     */
    uprotocol::utransport::UMessage parseToUMessage();

    void setJSONValue(const rapidjson::Document& jsonValue) {
        if (jsonValue.HasMember("data")) {
            documentObj_.CopyFrom(jsonValue["data"], documentObj_.GetAllocator());
        } else {
            spdlog::error("JSON data does not contain a 'data' member.");
        }
    }

private:

    /**
     * @brief Retrieves the value of a member in the JSON document and converts it to the specified type.
     * @tparam T The type to convert the value to.
     * @param member The JSON member to retrieve the value from.
     * @param memberName The name of the member.
     * @param numBase The number base to use for conversion (e.g., 10 for decimal, 16 for hexadecimal).
     * @return The converted value of the member.
     */
    template<typename T>
    T getValue(const rapidjson::Value& member, const std::string& memberName, int8_t numBase);

    /**
     * @brief Converts the value of a member in the JSON document from hexadecimal to uint32_t.
     * @param member The JSON member to convert the value from.
     * @param memberName The name of the member.
     * @return The converted value as uint32_t.
     */
    uint32_t convertStrToUint32(const rapidjson::Value& member, const std::string& memberName);

    /**
     * @brief Converts the value of a member in the JSON document from hexadecimal to uint16_t.
     * @param member The JSON member to convert the value from.
     * @param memberName The name of the member.
     * @return The converted value as uint16_t.
     */
    uint16_t convertStrToUint16(const rapidjson::Value& member, const std::string& memberName);
    
    uint8_t convertStrToUint8(const rapidjson::Value& member, const std::string& memberName);

    uprotocol::v1::UMessageType convertStrToUMessageType(const std::string& valueStr);

    uprotocol::v1::UPriority convertStrToUPriority(const std::string& valueStr);

    uprotocol::utransport::UPayloadFormat convertStrToUPayloadFormat(const std::string& valueStr);

    rapidjson::Document documentObj_;       ///< The rapidjson::Document object used for parsing.
    //uprotocol::v1::UMessage message_;       ///< The UMessage object used for parsing.

};
