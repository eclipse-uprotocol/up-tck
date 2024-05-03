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


Value ProtoConverter::convertFieldToValue(const FieldDescriptor* field, const Message& message, Document& doc) {
    const Reflection* reflection = message.GetReflection();
    switch (field->cpp_type()) {
        case FieldDescriptor::CPPTYPE_INT32:
            return Value(reflection->GetInt32(message, field));
        case FieldDescriptor::CPPTYPE_INT64:
            return Value(reflection->GetInt64(message, field));
        case FieldDescriptor::CPPTYPE_UINT32:
            return Value(reflection->GetUInt32(message, field));
        case FieldDescriptor::CPPTYPE_UINT64:
            return Value(reflection->GetUInt64(message, field));
        case FieldDescriptor::CPPTYPE_DOUBLE:
            return Value(reflection->GetDouble(message, field));
        case FieldDescriptor::CPPTYPE_FLOAT:
            return Value(reflection->GetFloat(message, field));
        case FieldDescriptor::CPPTYPE_BOOL:
            return Value(reflection->GetBool(message, field));
        case FieldDescriptor::CPPTYPE_ENUM:
            return Value(reflection->GetEnum(message, field)->number());
        case FieldDescriptor::CPPTYPE_STRING:
            return Value(reflection->GetString(message, field).c_str(), doc.GetAllocator());
        case FieldDescriptor::CPPTYPE_MESSAGE:
            return convertMessageToDocument(reflection->GetMessage(message, field), doc);
        default:
            return Value();
    }
}

Value ProtoConverter::convertRepeatedFieldToValue(const FieldDescriptor* field, const Message& message, Document& doc) {
    const Reflection* reflection = message.GetReflection();
    const int size = reflection->FieldSize(message, field);
    Value array(kArrayType);
    for (int i = 0; i < size; ++i) {
        array.PushBack(convertFieldToValue(field, message, doc), doc.GetAllocator());
    }
    return array;
}

Value ProtoConverter::convertMessageToDocument(const Message& message, Document& doc) {
    Value object(kObjectType);

    const Descriptor* descriptor = message.GetDescriptor();
    const Reflection* reflection = message.GetReflection();

    for (int i = 0; i < descriptor->field_count(); ++i) {
        const FieldDescriptor* field = descriptor->field(i);
        if (field->is_repeated()) {
            Value array(kArrayType);
            const int size = reflection->FieldSize(message, field);
            for (int j = 0; j < size; ++j) {
                array.PushBack(convertFieldToValue(field, message, doc), doc.GetAllocator());
            }
            object.AddMember(StringRef(field->name().c_str()), array, doc.GetAllocator());
        } else {
            object.AddMember(StringRef(field->name().c_str()), convertFieldToValue(field, message, doc), doc.GetAllocator());
        }
    }

    return object;
}
