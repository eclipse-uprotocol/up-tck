#include <TestAgent.h>
#include <google/protobuf/any.pb.h>

TestAgent::TestAgent(std::string transportType)
{
	transportPtr_ = createTransport(transportType);
	if (nullptr == transportPtr_) {
		spdlog::error("TestAgent::TestAgent(), Failed to create transport");
		exit(1);
	}

	clientSocket_ = 0;
    actionHandlers_ = {
        {string(Constants::SEND_COMMAND), std::function<UStatus(Document &)>([this](Document &doc) { return this->handleSendCommand(doc); })},
        {string(Constants::REGISTER_LISTENER_COMMAND), std::function<UStatus(Document &)>([this](Document &doc) { return this->handleRegisterListenerCommand(doc); })},
        {string(Constants::UNREGISTER_LISTENER_COMMAND), std::function<UStatus(Document &)>([this](Document &doc) { return this->handleUnregisterListenerCommand(doc); })},
        {string(Constants::INVOKE_METHOD_COMMAND), std::function<void(Document &)>([this](Document &doc) { this->handleInvokeMethodCommand(doc); })},
        {string(Constants::SERIALIZE_URI), std::function<void(Document &)>([this](Document &doc) { this->handleSerializeUriCommand(doc); })},
        {string(Constants::DESERIALIZE_URI), std::function<void(Document &)>([this](Document &doc) { this->handleDeserializeUriCommand(doc); })}
    };
}

TestAgent::~TestAgent()
{

}

UStatus TestAgent::onReceive(uprotocol::utransport::UMessage &transportUMessage) const
{
	std::cout << "TestAgent::onReceive(), received." << std::endl;
	uprotocol::v1::UPayload payV1;
		payV1.set_format((uprotocol::v1::UPayloadFormat)transportUMessage.payload().format());

	UMessage umsg;
	UStatus ustatus;

	if (transportUMessage.attributes().type() == uprotocol::v1::UMessageType::UMESSAGE_TYPE_REQUEST) {
		google::protobuf::StringValue string_value;
		string_value.set_value("SuccessRPCResponse");
		Any any_message;
		any_message.PackFrom(string_value);
		string serialized_message;
		any_message.SerializeToString(&serialized_message);
		uprotocol::utransport::UPayload payload1((const unsigned char *)serialized_message.c_str(), serialized_message.length(), uprotocol::utransport::UPayloadType::VALUE);
		payload1.setFormat(uprotocol::utransport::UPayloadFormat::PROTOBUF_WRAPPED_IN_ANY);

		auto attr  = uprotocol::utransport::UAttributesBuilder::response(transportUMessage.attributes().sink(), 
				transportUMessage.attributes().source(),
				UPriority::UPRIORITY_CS4, transportUMessage.attributes().id()).build();
		uprotocol::utransport::UMessage respTransportUMessage(payload1,attr);
		ustatus = transportPtr_->send(respTransportUMessage);
	} else {
		payV1.set_value(transportUMessage.payload().data(), transportUMessage.payload().size());    		

		umsg.mutable_payload()->CopyFrom(payV1);
		umsg.mutable_attributes()->CopyFrom(transportUMessage.attributes());

		sendToTestManager(umsg, (const string)string(Constants::RESPONSE_ON_RECEIVE));
	}

	return ustatus;
}

std::shared_ptr<uprotocol::utransport::UTransport> TestAgent::createTransport(const std::string& transportType) {
	if (transportType == "socket") {
		return std::make_shared<SocketUTransport>();
	} else if (transportType == "zenoh") {
		return uprotocol::client::UpZenohClient::instance(
			BuildUAuthority().setName("cpp").build(),
			BuildUEntity().setName("rpc.client").setMajorVersion(1).setId(1).build());
	} else {
		spdlog::error("Invalid transport type: {}", transportType);
		return nullptr;
	}
}

void TestAgent::writeDataToTMSocket(Document & responseDoc, string action) const
{
	Value valAction(action.c_str(), responseDoc.GetAllocator());
	responseDoc.AddMember("action", valAction, responseDoc.GetAllocator());
	Value valUE("cpp", responseDoc.GetAllocator());
	responseDoc.AddMember("ue", valUE, responseDoc.GetAllocator());

	rapidjson::StringBuffer buffer;
	Writer<rapidjson::StringBuffer> writer(buffer);

	responseDoc.Accept(writer);

	// Get the JSON data as a C++ string
	string json = buffer.GetString();
	spdlog::info("TestAgent::writeDataToTMSocket(), Sent to TM : {}", json);

	if (send(clientSocket_, json.c_str(), strlen(json.c_str()), 0) == -1) {
		perror("TestAgent::writeDataToTMSocket(), Error sending data to TM ");
	}
}

void TestAgent::sendToTestManager(const Message& proto, const string& action, const string& strTest_id) const
{
	Document responseDict;
	responseDict.SetObject();
	Value dataValue = ProtoConverter::convertMessageToJson(proto, responseDict);
	//Value dataValue = ProtoConverter::convertMessageToDocument(proto, responseDict);
	spdlog::info("TestAgent::sendToTestManager(), dataValue is : {}", dataValue.GetString());

	responseDict.AddMember("data", dataValue, responseDict.GetAllocator());

	if(!strTest_id.empty())
	{
		Value jsonStrValue(rapidjson::kStringType);
		jsonStrValue.SetString(strTest_id.c_str(), static_cast<rapidjson::SizeType>(strTest_id.length()), responseDict.GetAllocator());
		responseDict.AddMember("test_id", jsonStrValue, responseDict.GetAllocator());
	}
	else
	{
		responseDict.AddMember("test_id", "", responseDict.GetAllocator());
	}

	writeDataToTMSocket(responseDict, action);
}

void TestAgent::sendToTestManager(Document &document, Value &jsonData, string action, const string& strTest_id) const
{
	document.AddMember("data", jsonData, document.GetAllocator());
	spdlog::info("TestAgent::sendToTestManager(), jsonData is : {}", jsonData.GetString());
	if(!strTest_id.empty())
	{
		Value jsonStrValue(rapidjson::kStringType);
		jsonStrValue.SetString(strTest_id.c_str(), static_cast<rapidjson::SizeType>(strTest_id.length()), document.GetAllocator());
		document.AddMember("test_id", jsonStrValue, document.GetAllocator());
	}
	else
	{
		document.AddMember("test_id", "", document.GetAllocator());
	}

	writeDataToTMSocket(document, action);
}

UStatus TestAgent::handleSendCommand(Document &jsonData)
{
	UMessage umsg1 = UMessage::default_instance();
	UMessage umsg(*((UMessage *)ProtoConverter::dictToProto(jsonData["data"], umsg1, jsonData.GetAllocator())));
	spdlog::info("TestAgent::handleSendCommand(), umsg string is : {}", umsg.DebugString());

	
	uprotocol::v1::UPayload pay = umsg.payload();
	string str = pay.value();
	//std::cout << "TestAgent::handleSendCommand(), payload is : " << str << std::endl;
	uprotocol::utransport::UPayload payload((const unsigned char *)str.c_str(), str.length(),uprotocol::utransport::UPayloadType::VALUE);
	payload.setFormat((uprotocol::utransport::UPayloadFormat)pay.format());

	auto id = uprotocol::uuid::Uuidv8Factory::create();
	auto uAttributesWithId = uprotocol::utransport::UAttributesBuilder(umsg.attributes().source(), id, umsg.attributes().type(),
			umsg.attributes().priority()).build();
	//uAttributesWithId.setSink(umsg.attributes().sink());

	uprotocol::utransport::UMessage transportUMessage(payload, uAttributesWithId);
	return transportPtr_->send(transportUMessage);
}

UStatus TestAgent::handleRegisterListenerCommand(Document &jsonData)
{
	UUri uri = BuildUUri().build();
	ProtoConverter::dictToProto(jsonData["data"], uri, jsonData.GetAllocator());
	return transportPtr_->registerListener(uri, *this);
}

UStatus TestAgent::handleUnregisterListenerCommand(Document &jsonData)
{
	UUri uri = BuildUUri().build();
	ProtoConverter::dictToProto(jsonData["data"], uri, jsonData.GetAllocator());
	return transportPtr_->unregisterListener(uri, *this);
}

void TestAgent::handleInvokeMethodCommand(Document &jsonData)
{
	Value& data = jsonData["data"];
	std::string strTest_id = jsonData["test_id"].GetString();

	// Convert data and payload to protocol buffers
	uprotocol::v1::UPayload upPay;
	ProtoConverter::dictToProto(data["payload"],upPay, jsonData.GetAllocator());
	string str = upPay.value();
	spdlog::debug("TestAgent::handleInvokeMethodCommand(), payload in string format is :  {}", str);
	uprotocol::utransport::UPayload payload((const unsigned char *)str.c_str(), str.length(),uprotocol::utransport::UPayloadType::VALUE);
	payload.setFormat((uprotocol::utransport::UPayloadFormat)upPay.format());
	
	data.RemoveMember("payload"); // removing payload to make it proper  uuri
	UUri uri = BuildUUri().build();
	ProtoConverter::dictToProto(data, uri, jsonData.GetAllocator());
	spdlog::debug("TestAgent::handleInvokeMethodCommand(), UUri in string format is :  {}", uri.DebugString());

	CallOptions options;
	options.set_ttl(10000);

	auto rpc_ptr = dynamic_cast<uprotocol::rpc::RpcClient*>(transportPtr_.get());
	std::future<uprotocol::rpc::RpcResponse> responseFuture = rpc_ptr->invokeMethod(uri, payload, options);

	try
	{
	//std::cout << "handleInvokeMethodCommand(), waiting for payload from responseFuture " << std::endl;
	responseFuture.wait();
	//std::cout << "handleInvokeMethodCommand(), getting payload from responseFuture " << std::endl;
	uprotocol::rpc::RpcResponse rpcResponse = responseFuture.get();
	uprotocol::utransport::UPayload pay2 = rpcResponse.message.payload();
	//std::cout << "handleInvokeMethodCommand(), payload size from responseFuture is : " << pay2.size() << std::endl;
	string strPayload = std::string(reinterpret_cast<const char*>(pay2.data()), pay2.size());
	spdlog::info("TestAgent::handleInvokeMethodCommand(), payload got from responseFuture is : {}", strPayload);

	uprotocol::v1::UPayload payV1;
	payV1.set_format((uprotocol::v1::UPayloadFormat)pay2.format());
	payV1.set_value(pay2.data(), pay2.size());

	// Create v1 UMessage from transport UMessage
	UMessage umsg;
	umsg.mutable_payload()->CopyFrom(payV1);
	umsg.mutable_attributes()->CopyFrom(rpcResponse.message.attributes());

	sendToTestManager(umsg, Constants::INVOKE_METHOD_COMMAND, strTest_id);

	} catch (const std::exception& e) {
		std::cerr << "TestAgent::handleInvokeMethodCommand(), Exception received while getting payload: " << e.what() << std::endl;
	}
	return;
}

void TestAgent::handleSerializeUriCommand(Document &jsonData)
{
	UUri uri = BuildUUri().build();
	ProtoConverter::dictToProto(jsonData["data"], uri, jsonData.GetAllocator());

	Document document;
	document.SetObject();

	Value jsonValue(rapidjson::kStringType);
	string strUri = LongUriSerializer::serialize(uri);
	jsonValue.SetString(strUri.c_str(), static_cast<rapidjson::SizeType>(strUri.length()), document.GetAllocator());

	std::string strTest_id = jsonData["test_id"].GetString();

	sendToTestManager(document, jsonValue, Constants::SERIALIZE_URI, strTest_id);
	return;
}

void TestAgent::handleDeserializeUriCommand(Document &jsonData)
{
	Document document;
	document.SetObject();

	Value jsonValue(rapidjson::kStringType);
	string strUri = LongUriSerializer::serialize(LongUriSerializer::deserialize(jsonData["data"].GetString()));
	jsonValue.SetString(strUri.c_str(), static_cast<rapidjson::SizeType>(strUri.length()), document.GetAllocator());

	std::string strTest_id = jsonData["test_id"].GetString();

	sendToTestManager(document, jsonValue, Constants::DESERIALIZE_URI, strTest_id);

	return;
}

void TestAgent::processMessage(Document &json_msg)
{
	std::string action = json_msg["action"].GetString();
	std::string strTest_id = json_msg["test_id"].GetString();

	spdlog::info("TestAgent::processMessage(), Received action : {}", action);

	auto it = actionHandlers_.find(action);
	if (it != actionHandlers_.end())
	{
		const auto& function = it->second;
		//std::cout << "TestAgent::processMessage(), Found respective function and calling the same. " << std::endl;
		if (std::holds_alternative<std::function<UStatus(Document &)>>(function)) {
			auto result = std::get<std::function<UStatus(Document &)>>(function)(json_msg);
			spdlog::info("TestAgent::processMessage(), received result is : {}", result.message());
			Document document;
			document.SetObject();

			Value statusObj(rapidjson::kObjectType);

			Value strValMsg;
			strValMsg.SetString(result.message().c_str(), document.GetAllocator());
			statusObj.AddMember("message", strValMsg, document.GetAllocator());

			//Value strValCode;
			//strValCode.SetString(UCode_Name(result.code()).c_str(), document.GetAllocator());
			statusObj.AddMember("code", result.code(), document.GetAllocator());

			rapidjson::Value detailsArray(rapidjson::kArrayType);
			statusObj.AddMember("details", detailsArray, document.GetAllocator());

			sendToTestManager(document, statusObj, action, strTest_id);
		} else {
			std::get<std::function<void(Document &)>>(function)(json_msg);
			spdlog::warn("TestAgent::processMessage(), Received no result");
		}
	}
	else {
		spdlog::warn("TestAgent::processMessage(), action '{}' not found.", action);
	}
}

void TestAgent::receiveFromTM()
{
	char recv_data[Constants::BYTES_MSG_LENGTH];
	try
	{
		while (true) {
			ssize_t bytes_received = recv(clientSocket_, recv_data, Constants::BYTES_MSG_LENGTH, 0);
			if (bytes_received < 1) {
				std::cerr << "TestAgent::receiveFromTM(), no data received, exiting the CPP Test Agent ... " << std::endl;
				DisConnect();
				return;
			}

			recv_data[bytes_received] = '\0';
			std::string json_str(recv_data);
			spdlog::info("TestAgent::receiveFromTM(), Received data from test manager: {}", json_str);

			Document json_msg;
			json_msg.Parse(json_str.c_str());
			if (json_msg.HasParseError()) {
				// Handle parsing error
				spdlog::error("TestAgent::receiveFromTM(), Failed to parse JSON data: {}", json_str);
				continue;
			}

			processMessage(json_msg);
		}
	}
	catch (std::exception & e) {
		spdlog::error("TestAgent::receiveFromTM(), Exception occurred due to {}", e.what());
	}
}

bool TestAgent::Connect()
{
	clientSocket_ = socket(AF_INET, SOCK_STREAM, 0);
	if (clientSocket_ == -1) {
		spdlog::error("TestAgent::Connect(), Error creating socket");
		return 1;
	}

	mServerAddress_.sin_family = AF_INET;
	mServerAddress_.sin_port = htons(Constants::TEST_MANAGER_PORT);
	inet_pton(AF_INET, Constants::TEST_MANAGER_IP, &(mServerAddress_.sin_addr));

	if (connect(clientSocket_, (struct sockaddr*)&mServerAddress_, sizeof(mServerAddress_)) == -1) {
		spdlog::error("TestAgent::Connect(), Error connecting to server");
		return false;
	}

	return true;
}

int TestAgent::DisConnect()
{
	close(clientSocket_);
	return 0;
}

int main(int argc, char* argv[]) {
	// uncomment this line to set log level to debug
	//spdlog::set_level(spdlog::level::level_enum::debug);
	spdlog::info(" *** Starting CPP Test Agent *** ");
    if (argc < 2){
        spdlog::error("Incorrect input prams: {} ", argv[0]);
        return 1;
    }

	std::string transportType = argv[1];

	TestAgent testAgent = TestAgent(transportType);
	if(testAgent.Connect())
	{
		std::thread receiveThread = std::thread(&TestAgent::receiveFromTM, &testAgent);

		Document document;
		document.SetObject();

		Value sdkName(kObjectType); // Create an empty object
		sdkName.AddMember("SDK_name", "cpp", document.GetAllocator());

		testAgent.sendToTestManager(document, sdkName, "initialize");
		receiveThread.join();
	}

	return 0;
}

