#include "ProtoConverter.h"

/*bool ProtoConverter::dictToProto(const Value& parentJsonObj, Message& parentProtoObj) {
	rapidjson::StringBuffer buffer;
	rapidjson::Writer<rapidjson::StringBuffer> writer(buffer);
	parentJsonObj.Accept(writer);
	std::string strBuf =  buffer.GetString();
	std::cout << "Received parentJsonObj string is  : " << strBuf << std::endl;

    return util::JsonStringToMessage(strBuf, &parentProtoObj).ok();
}*/

Message* ProtoConverter::dictToProto(const Value& parentJsonObj, Message& parentProtoObj)
{
	populateFields(parentJsonObj, parentProtoObj);
	return &parentProtoObj;
}

Value ProtoConverter::convertMessageToJson(const Message& message, Document& doc) {
    std::string jsonString;
    util::MessageToJsonString(message, &jsonString);
    return Value(jsonString.c_str(), jsonString.length(), doc.GetAllocator());
}

void ProtoConverter::populateFields(const Value& jsonObj, Message& protoObj) {
    const Descriptor* descriptor = protoObj.GetDescriptor();
    for (auto it = jsonObj.MemberBegin(); it != jsonObj.MemberEnd(); ++it) {
        const std::string& key = it->name.GetString();
        const rapidjson::Value& value = it->value;
        const FieldDescriptor* fieldDescriptor = descriptor->FindFieldByName(key);
        //std::cout << "ProtoConverter::populateFields(), key is : " << key << std::endl;
        if (fieldDescriptor != nullptr) {
            if (value.IsString() && std::string(value.GetString()).find("BYTES:") == 0) {
                std::string byteString = std::string(value.GetString()).substr(6); // Remove 'BYTES:' prefix
                //std::cout << "ProtoConverter::populateFields(), string value is : " << byteString<< std::endl;

                Value jsonValue(rapidjson::kStringType);
                jsonValue.SetString(byteString.c_str(), static_cast<rapidjson::SizeType>(byteString.length()));
                setFieldValue(protoObj, fieldDescriptor, jsonValue);
            }
            else
            {
                setFieldValue(protoObj, fieldDescriptor, value);
            }
        }
    }
}

void ProtoConverter::setFieldValue(Message& protoObj, const FieldDescriptor* fieldDescriptor, const rapidjson::Value& value)
{
	switch (fieldDescriptor->type()) {
	case FieldDescriptor::TYPE_INT32:
	{
		//std::cout << "ProtoConverter::setFieldValue(), intValue: " << value.GetInt() << std::endl;
		protoObj.GetReflection()->SetInt32(&protoObj, fieldDescriptor, value.GetInt());
	}
		break;
	case FieldDescriptor::TYPE_INT64:
		protoObj.GetReflection()->SetInt64(&protoObj, fieldDescriptor, value.GetInt64());
		break;
	case FieldDescriptor::TYPE_FLOAT:
		protoObj.GetReflection()->SetFloat(&protoObj, fieldDescriptor, value.GetFloat());
		break;
	case FieldDescriptor::TYPE_DOUBLE:
		protoObj.GetReflection()->SetDouble(&protoObj, fieldDescriptor, value.GetDouble());
		break;
	case FieldDescriptor::TYPE_BOOL:
		protoObj.GetReflection()->SetBool(&protoObj, fieldDescriptor, value.GetBool());
		break;
	case FieldDescriptor::TYPE_STRING:
		{
			//std::cout << "ProtoConverter::setFieldValue(), GetString: " << value.GetString() << std::endl;
			protoObj.GetReflection()->SetString(&protoObj, fieldDescriptor, value.GetString());
		}
		break;
	case FieldDescriptor::TYPE_ENUM:
		protoObj.GetReflection()->SetEnumValue(&protoObj, fieldDescriptor, fieldDescriptor->enum_type()->FindValueByName(value.GetString())->number());
		break;
	case FieldDescriptor::TYPE_MESSAGE:
		if (value.IsObject()) {
			//std::cout << "ProtoConverter::setFieldValue(), TYPE_MESSAGE: " << value.GetString() << std::endl;
			Message* nestedMessage = protoObj.GetReflection()->MutableMessage(&protoObj, fieldDescriptor);
			populateFields(value, *nestedMessage);
		}
		break;
	default:
		{
			//std::cout << "ProtoConverter::setFieldValue(), unknown type, forcing to set as string" << std::endl;
			protoObj.GetReflection()->SetString(&protoObj, fieldDescriptor, value.GetString());
		}
		break;
	}
}
