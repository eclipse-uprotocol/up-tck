#include "SocketUTransport.h"
#include <up-cpp/uri/validator/UriValidator.h>
#include <up-cpp/uuid/factory/Uuidv8Factory.h>

const UUri SocketUTransport::RESPONSE_URI = BuildUUri().
setEntity(BuildUEntity().setName("test_agent_cpp").setMajorVersion(1).build()).
setResource(BuildUResource().setRpcResponse().build()).
build();

SocketUTransport::SocketUTransport()
{
	struct sockaddr_in serv_addr;
	if ((socketFd = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
		std::cerr << "SocketUTransport(), Socket creation error" << std::endl;
		exit(EXIT_FAILURE);
	}

	serv_addr.sin_family = AF_INET;
	serv_addr.sin_port = htons(DISPATCHER_PORT);

	if (inet_pton(AF_INET, DISPATCHER_IP, &serv_addr.sin_addr) <= 0) {
		std::cerr << "SocketUTransport(), Invalid address/ Address not supported" << std::endl;
		exit(EXIT_FAILURE);
	}

	if (connect(socketFd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
		std::cerr << "SocketUTransport(), Socket connection Failed" << std::endl;
		exit(EXIT_FAILURE);
	}

	processThread = std::thread(&SocketUTransport::listen, this);
	//threadPool_ = make_shared<ThreadPool>(queueSize_, maxNumOfCuncurrentRequests_);
}

SocketUTransport::~SocketUTransport()
{

}

void SocketUTransport::listen() {
	while (true) {
		try {
			char buffer[BYTES_MSG_LENGTH];
			int readSize = read(socketFd, buffer, sizeof(buffer));
			if (readSize < 0) {
				std::cerr << "SocketUTransport::listen(), Read error" << std::endl;
				close(socketFd);
				return;
			}
			else if (readSize == 0) {
				//std::cerr << "Received zero bytes" << std::endl;
				continue;
			}

			UMessage umsg;
			if (!umsg.ParseFromArray(buffer, readSize)) {
				std::cerr << "SocketUTransport::listen(), Error parsing UMessage" << std::endl;
				continue;
			}

			std::cout << "SocketUTransport::listen(), Received uMessage: " << umsg.DebugString() << ", size is " << readSize << std::endl;

			auto attributes = umsg.attributes();
			if (attributes.type() == uprotocol::v1::UMessageType::UMESSAGE_TYPE_PUBLISH)
				handlePublishMessage(umsg);
			else if (attributes.type() == uprotocol::v1::UMessageType::UMESSAGE_TYPE_REQUEST)
				handleRequestMessage(umsg);
			else if (attributes.type() == uprotocol::v1::UMessageType::UMESSAGE_TYPE_RESPONSE)
				handleResponseMessage(umsg);

		} catch (const std::exception& e) {
			std::cerr << "SocketUTransport::listen(), Exception: " << e.what() << std::endl;
		}
	}
}

UStatus SocketUTransport::send(const UUri& topic, const uprotocol::utransport::UPayload& payload,
		const uprotocol::utransport::UAttributes& attributes)
{
	// TODO: Convert utransport objects to v1 objects
	uprotocol::v1::UPayload payV1;
	payV1.set_value(payload.data(), payload.size());
	payV1.set_format(uprotocol::v1::UPayloadFormat::UPAYLOAD_FORMAT_PROTOBUF_WRAPPED_IN_ANY);

	uprotocol::v1::UAttributes attrV1;
	attrV1.mutable_source()->CopyFrom(topic); // Assuming topic is of type UUri
	attrV1.set_type((uprotocol::v1::UMessageType)attributes.type());
	attrV1.set_priority((uprotocol::v1::UPriority)attributes.priority());
	attrV1.mutable_id()->CopyFrom(attributes.id());
	/*if(!UuidSerializer::serializeToString(attributes.id()).empty())
	{
	attrV1.mutable_id()->CopyFrom(attributes.id());
	// TODO: currently not able to get sink to utransport attr
	std::optional<uprotocol::v1::UUri> optionalUUri = attributes.sink();
	if(optionalUUri.has_value())
		attrV1.mutable_sink()->CopyFrom(optionalUUri.value());
	attrV1.mutable_sink()->CopyFrom(RESPONSE_URI);
	}*/

	UMessage umsg;
	umsg.mutable_payload()->CopyFrom(payV1);
	umsg.mutable_attributes()->CopyFrom(attrV1);

	std::cout << "SocketUTransport::send(), UMessage in string format is : " << umsg.DebugString() << std::endl;

	/*std::string umsgSerialized;
	bool ret = umsg.SerializeToString(&umsgSerialized);*/

	size_t serializedSize = umsg.ByteSizeLong();
	std::string umsgSerialized(serializedSize, '\0');
	bool ret = umsg.SerializeToArray(umsgSerialized.data(), serializedSize);
	std::cout << "SocketUTransport::send(), ret is "  << ret << " Serialized UMessage is " << umsgSerialized <<
			", size is " << serializedSize << std::endl;

	UStatus status;
	status.set_code(UCode::OK);
	status.set_message("OK");

	if (::send(socketFd, umsgSerialized.c_str(), serializedSize,0) < 0) {
		std::cerr << "SocketUTransport::send(), Error sending UMessage" << std::endl;
		status.set_code(UCode::INTERNAL);
		status.set_message("Sending data in socket failed.");
		return status;
	}

	return status;
}

UStatus SocketUTransport::registerListener(const UUri& topic, const UListener& listener) {
	UStatus status;
	status.set_code(UCode::INTERNAL);

	std::cout << "SocketUTransport::registerListener()" << std::endl;

	if(valid_uri(LongUriSerializer::serialize(topic)))
	{
		std::cout << "SocketUTransport::registerListener(), found valid_uri" << std::endl;
		status.set_code(UCode::OK);
		status.set_message("OK");
		auto uriHash = std::hash<std::string>{}(LongUriSerializer::serialize(topic));
		std::vector<const UListener *>& vec = uriToListener[uriHash];
		if(!vec.empty())
			vec.push_back(&listener);
		else
		{
			std::vector<const UListener *> vec1;
			vec1.push_back(&listener);
			uriToListener[uriHash]= vec1;
		}
	}
	else
	{
		status.set_message("Received invalid URI");
	}

	return status;
}

UStatus SocketUTransport::unregisterListener(const UUri& topic, const UListener& listener) {
	UStatus status;
	status.set_code(UCode::INTERNAL);

	if(valid_uri(LongUriSerializer::serialize(topic)))
	{
		auto uriHash = std::hash<std::string>{}(LongUriSerializer::serialize(topic));
		std::vector<const UListener *>& vec = uriToListener[uriHash];

		auto it = std::find_if(vec.begin(), vec.end(), [&](const UListener * item) {
			return item == &listener;
		});
		if (it != vec.end()) {
			std::cout << "SocketUTransport::unregisterListener(), found listner and removing the same." << std::endl;
			vec.erase(it);
			status.set_code(UCode::OK);
			status.set_message("OK");
		}
		else
		{
			status.set_code(UCode::NOT_FOUND);
			status.set_message("Listener not found for the given UUri");
		}
	}
	else
	{
		status.set_message("Received invalid URI");
	}
	return status;
}

UStatus SocketUTransport::receive(const UUri &uri, const uprotocol::utransport::UPayload &payload,
		const uprotocol::utransport::UAttributes &attributes)
{
	UStatus status;
	status.set_code(UCode::UNAVAILABLE);
	return status;
}

void SocketUTransport::timeout_counter(UUID &req_id, std::future<uprotocol::utransport::UPayload>& resFuture, std::promise<uprotocol::utransport::UPayload>& promise, int timeout)
{
	try {
		int timeinsecs = timeout/1000;
		//std::cout << "SocketUTransport::timeout_counter(),  going to sleep for " << timeinsecs << " seconds" << std::endl;
		std::this_thread::sleep_for(std::chrono::seconds(timeinsecs));
		//std::cout << "SocketUTransport::timeout_counter(),  sleep is done" << std::endl;
		if (!resFuture.valid()) {
			auto uuidStr = UuidSerializer::serializeToString(req_id);
			promise.set_exception( std::make_exception_ptr(std::runtime_error("Not received response for request " +
					uuidStr + " within " + std::to_string(timeout) + " ms")));
		}
		else{
			std::cout << "SocketUTransport::timeout_counter(), resFuture is not valid" << std::endl;
		}
	} catch (const std::exception& e) {
		std::cerr << "SocketUTransport::timeout_counter(), Exception received from thread: " << e.what() << std::endl;
	}
}

std::future<uprotocol::utransport::UPayload> SocketUTransport::invokeMethod(const UUri &topic,
		const uprotocol::utransport::UPayload &payload,
		const uprotocol::utransport::UAttributes &attributes)
{
	std::promise<uprotocol::utransport::UPayload> promise;
	auto responseFuture = promise.get_future();

	auto requestId = uprotocol::uuid::Uuidv8Factory::create();
	//TODO: RESPONSE is REQUEST in v1, signalling is cs4 in v1, not using attributes
	auto attr = uprotocol::utransport::UAttributesBuilder(requestId, uprotocol::utransport::UMessageType::RESPONSE,
			uprotocol::utransport::UPriority::SIGNALING).withSink(RESPONSE_URI).build();

	auto uuidStr = UuidSerializer::serializeToString(requestId);
	reqidToFutureUMessage[uuidStr] = std::move(promise);

	int timeout = 10000;  // get from call options as input argument
	std::thread timeoutThread(std::bind(&SocketUTransport::timeout_counter, this, requestId, std::ref(responseFuture) ,
			std::ref(reqidToFutureUMessage[uuidStr]), timeout));
	timeoutThread.detach();
	send(topic, payload, attr);
	return responseFuture;
}

void SocketUTransport::handlePublishMessage(UMessage umsg) {
	UUri uri = umsg.attributes().source();
	notifyListeners(uri, umsg);
}

void SocketUTransport::handleRequestMessage(UMessage umsg) {
	UUri uri = umsg.attributes().sink();
	notifyListeners(uri, umsg);
}

void SocketUTransport::handleResponseMessage(UMessage umsg) {
	UUID requestId = umsg.attributes().id();
	auto uuidStr = UuidSerializer::serializeToString(requestId);
	auto it = reqidToFutureUMessage.find(uuidStr);
	if (it != reqidToFutureUMessage.end()) {
		// TODO:get from umsg and convert to utransport objects
		//const char * chTest = "hello";
		uprotocol::v1::UPayload pay = umsg.payload();
		string str = pay.value();
		uprotocol::utransport::UPayload payload((const unsigned char *)str.c_str(), str.length(), UPayloadType::VALUE);
		it->second.set_value(payload);
		reqidToFutureUMessage.erase(it);
	}
	else
	{
		std::cerr << "SocketUTransport::handleResponseMessage(), Request ID not found: " << uuidStr << std::endl;
	}
}

void SocketUTransport::notifyListeners(UUri uri, UMessage umsg) {
	std::lock_guard<std::mutex> lock(mutex_);
	auto uriHash = std::hash<std::string>{}(LongUriSerializer::serialize(uri));
	std::vector<const UListener *>& listeners = uriToListener[uriHash];
	if (!listeners.empty() ) {
		for (const auto listener : listeners)
		{
			// TODO:get from umsg and convert to utransport objects
			uprotocol::v1::UPayload pay = umsg.payload();
			string str = pay.value();
			//const char * chTest = "hello";
			std::cout << "SocketUTransport::notifyListeners(),  payload : " << str << std::endl;
			uprotocol::utransport::UPayload payload((const unsigned char *)str.c_str(), str.length(),UPayloadType::VALUE);
			//uprotocol::utransport::UPayload payload((const unsigned char *)"hello", 5,UPayloadType::VALUE);
			uprotocol::utransport::UAttributes attributes(umsg.attributes().id(), (uprotocol::utransport::UMessageType)umsg.attributes().type(),
					(uprotocol::utransport::UPriority)umsg.attributes().priority());
			listener->onReceive(uri, payload, attributes);
		}
	} else {
		std::cerr << "SocketUTransport::notifyListeners(), Uri not found in Listener Map, discarding..."<< std::endl;
	}
}

