#include <iostream>
#include <thread>
#include <functional>
#include "constants.h"
#include <tckUE1.h>


using namespace std;
using namespace google::protobuf;
//using namespace uprotocol::proto;
//using namespace uprotocol::uri::serializer;
//using namespace uprotocol::uri::validator;
//using namespace uprotocol::uuid::serializer;

template <typename T>
ZenohClientTestAgent<T>::ZenohClientTestAgent() 
    : transport_(uprotocol::client::UpZenohClient::instance()),
      is_running_(true),
      ta_socket_(io_context_),
      resolver_(io_context_) 
{
    boost::asio::connect(ta_socket_, resolver_.resolve("127.0.0.5", "12345"));
}

template <typename T>
ZenohClientTestAgent<T>::~ZenohClientTestAgent() {
    cleanup();
}

template <typename T>
void ZenohClientTestAgent<T>::cleanup() {
    spdlog::info("{}", __FUNCTION__);
    stop_receive_from_tm();
    ta_socket_.close();
}

template <typename T>
rapidjson::Document ZenohClientTestAgent<T>::createJSONDocument(const std::string& key, const std::string& value) {
    rapidjson::Document doc;
    doc.SetObject();
    rapidjson::Document::AllocatorType& allocator = doc.GetAllocator();
    doc.AddMember(rapidjson::Value(key.c_str(), allocator), rapidjson::Value(value.c_str(), allocator), allocator);
    return doc;
}

template <typename T>
uprotocol::v1::UStatus ZenohClientTestAgent<T>::onReceive(uprotocol::utransport::UMessage &message) const {
    spdlog::info("{}", __FUNCTION__);

    auto payloadData = reinterpret_cast<const char *>(message.payload().data());

    spdlog::info("dataPayload = {}",
            payloadData);

    std::string payloadDataStr(payloadData);
    if (payloadDataStr == "012345678"){
        auto response = const_cast<ZenohClientTestAgent*>(this)->createJSONDocument("payload", "012345678");
        const_cast<ZenohClientTestAgent*>(this)->send_to_test_manager(response, REGISTER_LISTENER_COMMAND);
    }

    uprotocol::v1::UStatus status;
    status.set_code(uprotocol::v1::UCode::OK);

    return status;
}

template <typename T>
void ZenohClientTestAgent<T>::process_message(const rapidjson::Document& json_data) {
    spdlog::info("{}", __FUNCTION__);
    jsonParser_.setJSONValue(json_data);
    auto action = jsonParser_.getValueString(json_data, "action");

    if (action == SEND_COMMAND) {
        handle_send_command();
    } else if (action == REGISTER_LISTENER_COMMAND) {
        handle_register_listener_command();
    }
}

template <typename T>
void ZenohClientTestAgent<T>::handle_send_command() {
    spdlog::info("{}", __FUNCTION__);
    const uprotocol::utransport::UMessage umsg = jsonParser_.parseToUMessage();
    //spdlog::info("UMESSAGE_IP {}", umsg.attributes().source().authority().ip());
    //static case umsg.attributes().type() to int
    spdlog::info("UMESSAGE_TYPE {}", static_cast<int>(umsg.attributes().type()));

    auto status = transport_->send(umsg);
    auto status_str = jsonParser_.convertUStatusToString(status);
    auto response = createJSONDocument("code", status_str);
    
    send_to_test_manager(response, SEND_COMMAND);
}

template <typename T>
void ZenohClientTestAgent<T>::handle_register_listener_command() {
    spdlog::info("{}", __FUNCTION__);
    auto umsg = jsonParser_.parseToUMessage();
    auto uri = umsg.attributes().source();
    auto strURI = uprotocol::uri::LongUriSerializer::serialize(uri);
    spdlog::info("Sending register listener on URI = {}", strURI);
    uprotocol::v1::UStatus status = transport_->registerListener(uri, *this);
    auto status_str = jsonParser_.convertUStatusToString(status);
    auto response = createJSONDocument("code", status_str);

    send_to_test_manager(response, REGISTER_LISTENER_COMMAND);
}

template <typename T>
void ZenohClientTestAgent<T>::send_to_test_manager(const rapidjson::Document& response, const string& action) {
    rapidjson::Document response_dict;
    response_dict.SetObject();
    rapidjson::Document::AllocatorType& allocator = response_dict.GetAllocator();
    response_dict.AddMember("data", rapidjson::Value(response, allocator).Move(), allocator);
    response_dict.AddMember("action", rapidjson::Value(action.c_str(), allocator).Move(), allocator);
    response_dict.AddMember("ue", rapidjson::Value("ue1", allocator).Move(), allocator);

    rapidjson::StringBuffer buffer;
    rapidjson::Writer<rapidjson::StringBuffer> writer(buffer);
    response_dict.Accept(writer);

    std::string response_str = buffer.GetString();

    boost::system::error_code error;
    boost::asio::write(ta_socket_, boost::asio::buffer(response_str), error);
    if (error) {
        std::cout << "Failed to send response_str" << std::endl;
    }
}

template <typename T>
void ZenohClientTestAgent<T>::receive_from_tm() {
    spdlog::info("{}", __FUNCTION__);
    std::string recv_data;

    while (is_running_) {
        boost::asio::streambuf buf;
        boost::system::error_code error;
        boost::asio::read(ta_socket_, buf, boost::asio::transfer_at_least(1), error);
        if (error) {
            std::cout << "Failed to read data" << std::endl;
            break;
        }

        std::istream is(&buf);
        std::string packet;
        std::getline(is, packet);

        recv_data += packet;

        // Try to parse the accumulated data
        rapidjson::Document json_data;
        //TODO this is not very good need to ensure full data is recived in different way
        if (json_data.Parse(recv_data.c_str()).HasParseError()) {
            spdlog::info("File: {}, waiting for all the packets to receive", __FILE__);
            continue; 
        } else {
            // If parsing was successful, clear the accumulated data
            spdlog::info("Received data from test manager: {}", recv_data);
            recv_data.clear();
            process_message(json_data);
        }
    }
}

template <typename T>
void ZenohClientTestAgent<T>::stop_receive_from_tm() {
    is_running_ = false;
}

std::atomic<int> exitSignal = 0;
void handle_signal(int signal) {
    spdlog::info("Received signal to terminate {}", signal);
    exitSignal = signal;
}

template <typename T>
ZenohClientTestAgent<T> createTestAgent() {
    return ZenohClientTestAgent<T>();
}

template <typename T>
void runTestAgent(ZenohClientTestAgent<T>& testAgent) {
    std::thread receive_thread(&ZenohClientTestAgent<T>::receive_from_tm, &testAgent);
    receive_thread.detach();    

    auto sdk_name = testAgent.createJSONDocument("SDK_name", "ue1");

    testAgent.send_to_test_manager(sdk_name, "initialize");

    //add wait for the receive thread to finish 3 minutes
    while (exitSignal == 0) {
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }

    spdlog::info("Exiting the test agent");
}

int main(int argc, char* argv[]) {
    // Register signal handlers
    std::signal(SIGTERM, handle_signal);
    std::signal(SIGINT, handle_signal);

    spdlog::info("Starting the test agent");
    if (argc < 2){
        spdlog::error("Incorrect input prams: {} ", argv[0]);
        return 1;
    }

    std::string transportType = argv[1];

    if (transportType == "zenoh") {
        spdlog::info("Starting the test agent with zenoh transport");
        auto testAgent = createTestAgent<uprotocol::client::UpZenohClient>();
        runTestAgent(testAgent);
    } else if (transportType == "socket") {
        spdlog::info("Starting the test agent with socket transport");
        //Sample code
        //auto testAgent = createTestAgent<UpSocketClient>();
        //runTestAgent(testAgent);
    } else {
        spdlog::error("Invalid transport type: {}", transportType);
        spdlog::error("Please specify the transport type as 'zenoh' or 'socket'");
        return 1;
    } 

    std::exit(exitSignal);
    return 0;
}





//Some code which may be useful 

// void ZenohClientTestAgent<T>::handle_unregister_listener_command(const rapidjson::Document& json_data) {
//     uprotocol::v1::UUri uri;
//     rapidjson::Document data_doc;
//     data_doc.CopyFrom(json_msg["data"], data_doc.GetAllocator());
//    // dict_to_proto(data_doc, dynamic_cast<google::protobuf::Message*>(&uri));
//     transport_->unregisterListener(uri, listener_);
// }

// void ZenohClientTestAgent<T>::handle_invoke_method_command(const rapidjson::Value& json_msg) {
//     uprotocol::v1::UUri uri;
//     rapidjson::Document data_doc;
//     data_doc.CopyFrom(json_msg["data"], data_doc.GetAllocator());
//     //dict_to_proto(data_doc, dynamic_cast<google::protobuf::Message*>(&uri));

//     rapidjson::Document data_doc2;
//     data_doc2.CopyFrom(json_msg["data"]["payload"], data_doc.GetAllocator());
//     uprotocol::v1::UPayload payload;
//    // dict_to_proto(data_doc2, dynamic_cast<google::protobuf::Message*>(&payload));

//     std::future<uprotocol::rpc::RpcResponse> result transport_->invokeMethod(uri, payload, CallOptions(ttl=10000));
//     if (false == result.valid()) {
//         spdlog::error("future is invalid");
//         uprotocol::rpc::RpcResponse response;
//         return response;
//     }
//     result.wait();
//     auto response = reinterpret_cast<const char *>(result.get().message.payload().data());

//     rapidjson::Document result_json;
//     result_json.Parse(response);
//     send_to_test_manager(result_json(response), RESPONSE_RPC);
// }

// void ZenohClientTestAgent<T>::handle_uri_serialize_command(const rapidjson::Document& json_msg) {
//     uprotocol::v1::UUri uri;
//     dict_to_proto(json_msg["data"], &uri);

//     uprotocol::v1::LongUriSerializer serializer;
//     string serialized_uri = serializer.serialize(uri);

//     send_to_test_manager(serialized_uri, SERIALIZE_URI);
// }

// void ZenohClientTestAgent<T>::handle_uri_deserialize_command(const rapidjson::Document& json_msg) {
//     string serialized_uri = json_msg["data"].asString();

//     uprotocol::v1::LongUriSerializer serializer;
//     uprotocol::v1::UUri uri = serializer.deserialize(serialized_uri);

//     send_to_test_manager(uri, DESERIALIZE_URI);
// }

// void ZenohClientTestAgent<T>::handle_uri_validate_command(const rapidjson::Document& json_msg) {
//     string val_type = json_msg["data"]["type"].asString();
//     string uri_str = json_msg["data"].get("uri", "").asString();

//     UriValidator validator;
//     ValidationResult status;

//     if (val_type == "uri") {
//         status = validator.validate(uri_str);
//     } else if (val_type == "rpc_response") {
//         status = validator.validate_rpc_response(uri_str);
//     }
//     // ...

//     ZenohClientTestAgent<T>::send_to_test_manager(status, VALIDATE_URI);
// }

// void ZenohClientTestAgent<T>::handle_uuid_deserialize_command(const rapidjson::Document& json_msg) {
//     string serialized_uuid = json_msg["data"].asString();

//     LongUuidSerializer serializer;
//     UUID uuid = serializer.deserialize(serialized_uuid);

//     send_to_test_manager(uuid, DESERIALIZE_UUID);
// }

// void ZenohClientTestAgent<T>::handle_uuid_serialize_command(const rapidjson::Document& json_msg) {
//     UUID uuid;
//     dict_to_proto(json_msg["data"], &uuid);

//     LongUuidSerializer serializer;
//     string serialized_uuid = serializer.serialize(uuid);

//     ZenohClientTestAgent<T>::send_to_test_manager(serialized_uuid, SERIALIZE_UUID);
// }