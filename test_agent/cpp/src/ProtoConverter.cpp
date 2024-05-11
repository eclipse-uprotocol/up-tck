#include "ProtoConverter.h"

Message* ProtoConverter::dictToProto(Value& parentJsonObj, Message& parentProtoObj, Document::AllocatorType& allocator)
{
    // Covert parentJsonObj value to string
    rapidjson::StringBuffer buffer;
    rapidjson::Writer<rapidjson::StringBuffer> writer(buffer);
    parentJsonObj.Accept(writer);
    std::string strBuf = buffer.GetString();
    std::cout << "Received parentJsonObj string is  : " << strBuf << std::endl;

    // Iterate over JSON object members
    for (auto& m : parentJsonObj.GetObject()) {
        // Check if value is a string and has 'BYTES:' prefix
        if (m.value.IsString() && std::string(m.value.GetString()).find("BYTES:") == 0) {
            std::string byteString = std::string(m.value.GetString()).substr(6); // Remove 'BYTES:' prefix
            m.value.SetString(byteString.c_str(), byteString.length(), allocator);
        }
    }

    google::protobuf::util::JsonParseOptions options;
    auto status = google::protobuf::util::JsonStringToMessage(strBuf, &parentProtoObj, options);
    if (!status.ok()) {
        std::cout << "Error during JSON to Message conversion: " << status.ToString() << std::endl;
    }
    
	return &parentProtoObj;
}

Value ProtoConverter::convertMessageToJson(const Message& message, Document& doc) {
    std::string jsonString;
    util::MessageToJsonString(message, &jsonString);
    return Value(jsonString.c_str(), jsonString.length(), doc.GetAllocator());
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
