#include <TestAgent.h>
#include <google/protobuf/any.pb.h>

SocketUTransport *TestAgent::transport = new SocketUTransport();
const UListener *TestAgent::listener = new SocketUListener(transport);
int TestAgent::clientSocket = 0;
struct sockaddr_in TestAgent::mServerAddress;

std::unordered_map<std::string, FunctionType> TestAgent::actionHandlers = {
		{string(Constants::SEND_COMMAND), std::function<UStatus(Document &)>(TestAgent::handleSendCommand)},
		{string(Constants::REGISTER_LISTENER_COMMAND), std::function<UStatus(Document &)>(TestAgent::handleRegisterListenerCommand)},
		{string(Constants::UNREGISTER_LISTENER_COMMAND), std::function<UStatus(Document &)>(TestAgent::handleUnregisterListenerCommand)},
		{string(Constants::INVOKE_METHOD_COMMAND), std::function<void(Document &)>(TestAgent::handleInvokeMethodCommand)},
		{string(Constants::SERIALIZE_URI), std::function<void(Document &)>(TestAgent::handleSerializeUriCommand)},
		{string(Constants::DESERIALIZE_URI), std::function<void(Document &)>(TestAgent::handleDeserializeUriCommand)}
};

TestAgent::TestAgent()
{

}

TestAgent::~TestAgent()
{

}

void TestAgent::writeDataToTMSocket(Document & responseDoc, string action)
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
	cout << "TestAgent::writeDataToTMSocket(), Sent to TM : " << json << endl;

	if (send(clientSocket, json.c_str(), strlen(json.c_str()), 0) == -1) {
		perror("TestAgent::writeDataToTMSocket(), Error sending data to TM ");
	}
}

void TestAgent::sendToTestManager(const Message& proto, const string& action, const string& strTest_id)
{
	Document responseDict;
	responseDict.SetObject();
	//Value dataValue = ProtoConverter::convertMessageToJson(proto, responseDict);
	Value dataValue = ProtoConverter::convertMessageToDocument(proto, responseDict);
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

void TestAgent::sendToTestManager(Document &document, Value &jsonData, string action, const string& strTest_id)
{
	document.AddMember("data", jsonData, document.GetAllocator());
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
	UMessage umsg(*((UMessage *)ProtoConverter::dictToProto(jsonData["data"], umsg1)));
	std::cout << "TestAgent::handleSendCommand(), umsg string is : " << umsg.DebugString() << std::endl;

	UUri uri = umsg.attributes().source();
	uprotocol::v1::UPayload pay = umsg.payload();
	string str = pay.value();
	//std::cout << "TestAgent::handleSendCommand(), payload is : " << str << std::endl;
	uprotocol::utransport::UPayload payload((const unsigned char *)str.c_str(), str.length(),UPayloadType::REFERENCE);
	auto id = uprotocol::uuid::Uuidv8Factory::create();

	uprotocol::utransport::UAttributes attributes(id, (uprotocol::utransport::UMessageType)umsg.attributes().type(),
			(uprotocol::utransport::UPriority)umsg.attributes().priority());

	return transport->send(uri, payload, attributes);
}

UStatus TestAgent::handleRegisterListenerCommand(Document &jsonData)
{
	UUri uri = BuildUUri().build();
	ProtoConverter::dictToProto(jsonData["data"], uri);
	return transport->registerListener(uri, *listener);
}

UStatus TestAgent::handleUnregisterListenerCommand(Document &jsonData)
{
	UUri uri = BuildUUri().build();
	ProtoConverter::dictToProto(jsonData["data"], uri);
	return transport->unregisterListener(uri, *listener);
}

void TestAgent::handleInvokeMethodCommand(Document &jsonData)
{
	Value& data = jsonData["data"];
	// Convert data and payload to protocol buffers
	UUri uri = BuildUUri().build();
	ProtoConverter::dictToProto(data, uri);
	uprotocol::v1::UPayload upPay;
	ProtoConverter::dictToProto(data["payload"],upPay);
	string str = upPay.value();
	//std::cout << "handleInvokeMethodCommand(), payload is : " << str << std::endl;
	uprotocol::utransport::UPayload payload((const unsigned char *)str.c_str(), str.length(),UPayloadType::VALUE);
	uprotocol::utransport::UAttributes attr;

	// TODO: get umsg from transport and send to test manager
	std::future<uprotocol::utransport::UPayload> responseFuture = transport->invokeMethod(uri, payload, attr);
	// CallOptions.newBuilder().build());


	try
	{
	//std::cout << "handleInvokeMethodCommand(), waiting for payload from responseFuture " << std::endl;
	responseFuture.wait();
	//std::cout << "handleInvokeMethodCommand(), getting payload from responseFuture " << std::endl;
	uprotocol::utransport::UPayload pay2 = responseFuture.get();
	//std::cout << "handleInvokeMethodCommand(), payload size from responseFuture is : " << pay2.size() << std::endl;
	string strPayload = std::string(reinterpret_cast<const char*>(pay2.data()), pay2.size());
	std::cout << "handleInvokeMethodCommand(), payload got from responseFuture is : " << strPayload << std::endl;


	std::string strTest_id = jsonData["test_id"].GetString();

	uprotocol::v1::UPayload payV1;
	payV1.set_format(uprotocol::v1::UPayloadFormat::UPAYLOAD_FORMAT_PROTOBUF_WRAPPED_IN_ANY);
	payV1.set_value(pay2.data(), pay2.size());

	//TODO: Get all details from response message
	uprotocol::v1::UAttributes attrV1;
	attrV1.set_priority((uprotocol::v1::UPriority)uprotocol::utransport::UPriority::SIGNALING);
	attrV1.mutable_source()->CopyFrom(uri); // Assuming topic is of type UUri
	attrV1.set_type((uprotocol::v1::UMessageType)uprotocol::utransport::UMessageType::RESPONSE);
	attrV1.mutable_id()->CopyFrom(attr.id());
	std::optional<uprotocol::v1::UUID> optionalreqid = attr.reqid();
	if(optionalreqid.has_value())
		attrV1.mutable_reqid()->CopyFrom(optionalreqid.value());
	attrV1.mutable_sink()->CopyFrom(transport->RESPONSE_URI);

	UMessage umsg;
	umsg.mutable_payload()->CopyFrom(payV1);
	    		umsg.mutable_attributes()->CopyFrom(attrV1);
	sendToTestManager(umsg, Constants::INVOKE_METHOD_COMMAND, strTest_id);

	} catch (const std::exception& e) {
		std::cerr << "TestAgent::handleInvokeMethodCommand(), Exception received while getting payload: " << e.what() << std::endl;
	}
	return;
}

void TestAgent::handleSerializeUriCommand(Document &jsonData)
{
	UUri uri = BuildUUri().build();
	ProtoConverter::dictToProto(jsonData["data"], uri);

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

	std::cout << "TestAgent::processMessage(), Received action : " << action << std::endl;

	auto it = actionHandlers.find(action);
	if (it != actionHandlers.end())
	{
		const auto& function = it->second;
		//std::cout << "TestAgent::processMessage(), Found respective function and calling the same. " << std::endl;
		if (std::holds_alternative<std::function<UStatus(Document &)>>(function)) {
			auto result = std::get<std::function<UStatus(Document &)>>(function)(json_msg);
			std::cout << "TestAgent::processMessage(), received result is : " << result.message() <<  std::endl;
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
			std::cout << "TestAgent::processMessage(), Received no result" << std::endl;
		}
	}
	else {
		std::cout << "TestAgent::processMessage(), action '" << action << "' not found." << std::endl;
	}
}

void TestAgent::receiveFromTM()
{
	char recv_data[Constants::BYTES_MSG_LENGTH];
	try
	{
		while (true) {
			ssize_t bytes_received = recv(clientSocket, recv_data, Constants::BYTES_MSG_LENGTH, 0);
			if (bytes_received < 1) {
				std::cerr << "TestAgent::receiveFromTM(), no data received, exiting the CPP Test Agent ... " << std::endl;
				DisConnect();
				return;
			}

			recv_data[bytes_received] = '\0';
			std::string json_str(recv_data);
			cout << "TestAgent::receiveFromTM(), Received data from test manager: " << json_str << endl;

			Document json_msg;
			json_msg.Parse(json_str.c_str());
			if (json_msg.HasParseError()) {
				// Handle parsing error
				cout << "TestAgent::receiveFromTM(), Failed to parse JSON data: " <<  json_str << endl;
				continue;
			}

			processMessage(json_msg);
		}
	}
	catch (std::exception & e) {
		cout << "TestAgent::receiveFromTM(), Exception occurred due to " << e.what() << endl;
	}
}

int TestAgent::Connect()
{
	clientSocket = socket(AF_INET, SOCK_STREAM, 0);
	if (clientSocket == -1) {
		cout <<"TestAgent::Connect(), Error creating socket" << endl;
		return 1;
	}

	mServerAddress.sin_family = AF_INET;
	mServerAddress.sin_port = htons(Constants::TEST_MANAGER_PORT);
	inet_pton(AF_INET, Constants::TEST_MANAGER_IP, &(mServerAddress.sin_addr));

	if (connect(clientSocket, (struct sockaddr*)&mServerAddress, sizeof(mServerAddress)) == -1) {
		cout << "TestAgent::Connect(), Error connecting to server" <<  endl;
		return 1;
	}

	return 0;
}

int TestAgent::DisConnect()
{
	close(clientSocket);
	return 0;
}

int main() {

	cout << " *** Starting CPP Test Agent *** " <<  endl;
	if(!TestAgent::Connect())
	{
		std::thread receiveThread = std::thread(&TestAgent::receiveFromTM);

		Document document;
		document.SetObject();

		Value sdkName(kObjectType); // Create an empty object
		sdkName.AddMember("SDK_name", "cpp", document.GetAllocator());

		TestAgent::sendToTestManager(document, sdkName, "initialize");
		receiveThread.join();
	}

	return 0;
}

