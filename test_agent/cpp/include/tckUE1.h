#ifndef ZENOH_CLIENT_TEST_AGENT_H
#define ZENOH_CLIENT_TEST_AGENT_H

#include <string>
#include <google/protobuf/message.h>
#include <google/protobuf/descriptor.h>
#include <google/protobuf/any.pb.h>
#include <google/protobuf/wrappers.pb.h>
#include <google/protobuf/util/json_util.h>
#include <up-core-api/uattributes.pb.h>
#include <up-core-api/umessage.pb.h>
#include <up-core-api/upayload.pb.h>
#include <up-core-api/uri.pb.h>
#include <up-core-api/uuid.pb.h>
#include <up-cpp/transport/UListener.h>
#include <up-cpp/uri/serializer/LongUriSerializer.h>
#include <up-cpp/uri/serializer/MicroUriSerializer.h>
#include <up-cpp/uri/validator/UriValidator.h>
#include <up-client-zenoh-cpp/client/upZenohClient.h>
#include <up-cpp/transport/UTransport.h>
#include "rapidjson/document.h"
#include "rapidjson/writer.h"
#include "rapidjson/stringbuffer.h"
#include <utils/JsonParser.hpp>

#include <boost/asio.hpp>
using namespace std;
using namespace uprotocol::utransport;
using namespace uprotocol::v1;
//using namespace google::protobuf;
//using namespace google::protobuf::util;


/**
 * @class ZenohClientTestAgent
 * @brief Represents a test agent for the Zenoh client.
 * 
 * This class provides functionality for sending and receiving messages using the Zenoh client.
 * It also handles the registration and processing of listener commands.
 */
template <typename T>
class ZenohClientTestAgent : public uprotocol::utransport::UListener {
public:
    /**
     * \brief Constructs a ZenohClientTestAgent object.
     */
    ZenohClientTestAgent();

    /**
     * \brief Destructor for the ZenohClientTestAgent class.
     */
    ~ZenohClientTestAgent();

    /**
     * @brief Cleans up any resources used by the program.
     * 
     * This function is responsible for releasing any resources that were acquired during the execution of the program.
     * It should be called before the program terminates to ensure proper cleanup.
     */
    void cleanUp();

    /**
     * \brief Callback function called when a message is received.
     * \param message The received message.
     * \return The status of the message processing.
     */
    uprotocol::v1::UStatus onReceive(uprotocol::utransport::UMessage &message) const;

    /**
     * \brief Creates a JSON document with the given key and value.
     * \param key The key for the JSON document.
     * \param value The value for the JSON document.
     * \return The created JSON document.
     */
    rapidjson::Document createJSONDocument(const std::string& key, const std::string& value);

    /**
     * \brief Sends the given JSON document to the test manager.
     * \param response The JSON document to send.
     * \param action The action to perform.
     */
    void sendToTestMananger(const rapidjson::Document& response, const string& action);

    /**
     * \brief Receives data from the test manager.
     */
    void receiveFromTM();

    /**
     * \brief Stops receiving data from the test manager.
     */
    void stopReceiveFromTM();
    
    /**
     * \brief Returns the TCP socket used by the test agent.
     * \return The TCP socket.
     */
    boost::asio::ip::tcp::socket& getTASocket(){
        return ta_socket_;
    }

private:
    /**
     * \brief Handles the register listener command.
     */
    void handleRegisterListener();

    //void handle_unregister_listener_command(const rapidjson::Document& json_data);

    /**
     * \brief Processes the received message.
     * \param json_data The JSON document containing the message data.
     */
    void processMessage(const rapidjson::Document& json_data);

    /**
     * \brief Handles the send command.
     */
    void handleSendCommand();

    std::shared_ptr<T> transport_;
    atomic<bool> isRunning_;
    boost::asio::io_context io_context_;
    boost::asio::ip::tcp::socket ta_socket_;
    boost::asio::ip::tcp::resolver resolver_;
    JsonParser jsonParser_;

};
#endif // ZENOH_CLIENT_TEST_AGENT_H