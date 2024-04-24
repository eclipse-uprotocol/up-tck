#ifndef CONSTANTS_H
#define CONSTANTS_H

#include <string>
#include <tuple>

const std::tuple<std::string, std::string> TEST_MANAGER_ADDR = {"127.0.0.5", "12345"};
const int BYTES_MSG_LENGTH = 32767;
const std::string SEND_COMMAND = "send";
const std::string REGISTER_LISTENER_COMMAND = "registerlistener";
const std::string UNREGISTER_LISTENER_COMMAND = "unregisterlistener";
const std::string INVOKE_METHOD_COMMAND = "invokemethod";
const std::string RESPONSE_ON_RECEIVE = "onreceive";
const std::string RESPONSE_RPC = "rpcresponse";
const std::string SERIALIZE_URI = "uri_serialize";
const std::string DESERIALIZE_URI = "uri_deserialize";
const std::string VALIDATE_URI = "uri_validate";
const std::string SERIALIZE_UUID = "uuid_serialize";
const std::string DESERIALIZE_UUID = "uuid_deserialize";

#endif // CONSTANTS_H

