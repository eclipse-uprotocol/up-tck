/*
 * Copyright (c) 2024 General Motors GTO LLC
 *
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 * SPDX-FileType: SOURCE
 * SPDX-FileCopyrightText: 2023 General Motors GTO LLC
 * SPDX-License-Identifier: Apache-2.0
 */

use crate::constants::*;
use serde_json::Value;
//use serde::{Serialize, Deserialize};
use serde::{Deserialize, Deserializer, Serialize};
use std::io::{Read, Write};
use up_rust::{
    Data, UAttributes, UAuthority, UEntity, UMessage, UMessageType, UPayload, UPayloadFormat,
    UPriority, UResource, UUri, UUID,
};

use protobuf::{Message, MessageField, SpecialFields};

use std::net::TcpStream;

pub fn send_socket_data(stream: &mut TcpStream, msg: &[u8]) -> std::io::Result<()> {
    stream.write_all(msg)?;
    Ok(())
}

pub fn receive_socket_data(stream: &mut TcpStream) -> std::io::Result<Vec<u8>> {
    let mut buffer = vec![0; BYTES_MSG_LENGTH];
    stream.read_exact(&mut buffer)?;
    Ok(buffer)
}

// Define a function to convert a Protocol Buffers message to a Base64-encoded string
pub fn protobuf_to_base64<T: Message>(obj: &T) -> String {
    // Serialize the Protocol Buffers message to bytes
    let serialized_bytes = obj.write_to_bytes().expect("Failed to serialize message");

    // Encode the bytes to Base64
    let base64_str = base64::encode(&serialized_bytes);

    // Return the Base64-encoded string
    base64_str
}

// Define a function to convert a Base64-encoded string to Protocol Buffers bytes
pub fn base64_to_protobuf_bytes(base64str: &str) -> Result<Vec<u8>, base64::DecodeError> {
    // Decode the Base64-encoded string to bytes
    let decoded_bytes = base64::decode(base64str)?;

    // Return the decoded bytes
    Ok(decoded_bytes)
}

pub fn convert_bytes_to_string(data: &[u8]) -> String {
    String::from_utf8_lossy(data).into_owned()
}

pub fn convert_jsonstring_to_json(jsonstring: &str) -> Value {
    serde_json::from_str(jsonstring).unwrap()
}

pub fn convert_json_to_jsonstring<T: serde::Serialize>(value: &T) -> String {
    serde_json::to_string(value).expect("Failed to convert to JSON string")
}
//pub fn convert_json_to_jsonstring(j: &Value) -> String {
//  j.to_string()
//}

pub fn convert_str_to_bytes(string: &str) -> Vec<u8> {
    string.as_bytes().to_vec()
}

#[derive(Debug, Default)]
pub struct WrapperUUri(pub UUri);
impl<'de> Deserialize<'de> for WrapperUUri {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        let value: Value = Deserialize::deserialize(deserializer)?;
        println!("WrapperUUri: {:?}", value);

        //update authority
        let _authority_name = match value
            .get("authority")
            .and_then(|authority| authority.get("name"))
        {
            Some(_authority_name) => _authority_name.as_str(),
            None => Some("default"),
        };
        
        let _authority_number_Ip = match value
            .get("authority")
            .and_then(|authority| authority.get("number"))
            .and_then(|number| number.get("Ip"))
        {
            Some(_authority_number_Ip) => _authority_number_Ip.to_string().as_bytes().to_vec(),
            None => {
                let default: Vec<u8> = vec![0];
                default
            }
        };
        let _authority_number_Id = match value
            .get("authority")
            .and_then(|authority| authority.get("number"))
            .and_then(|number| number.get("Id"))
        {
            Some(_authority_number_Id) => _authority_number_Id.to_string().as_bytes().to_vec(),
            None => {
                let default: Vec<u8> = vec![0];
                default
            }
        };
        let _special_fields = SpecialFields::default();

        let mut _authority = UAuthority::new();
        _authority.name = _authority_name.map(|s| s.to_string());
        _authority.set_id(_authority_number_Id);
        _authority.set_ip(_authority_number_Ip);
        _authority.special_fields = _special_fields;

        println!("_authority: {:?}", _authority);
        let ___authority = MessageField(Some(Box::new(_authority)));

        //update entity
        let _entity_name = match value.get("entity").and_then(|entity| entity.get("name")) {
            Some(_entity_name) => _entity_name.as_str(),
            None => Some("default"),
        };
        let _entity_id = match value.get("entity").and_then(|entity| entity.get("id")) {
            Some(_entity_id) => _entity_id
                .clone()
                .as_str()
                .expect("not a string")
                .parse::<u32>()
                .expect("issue in converting to u32"),
            None => 0,
        };
        let _entity_version_major = match value
            .get("entity")
            .and_then(|entity| entity.get("version_major"))
        {
            Some(_entity_version_major) => _entity_version_major
                .clone()
                .as_str()
                .expect("not a string")
                .parse::<u32>()
                .expect("issue in converting to u32"),

            None => 0,
        };
        let _entity_version_minor = match value
            .get("entity")
            .and_then(|entity| entity.get("version_minor"))
        {
            Some(_entity_version_minor) => _entity_version_minor
                .clone()
                .as_str()
                .expect("not a string")
                .parse::<u32>()
                .expect("issue in converting to u32"),
            None => 0,
        };
        let _entity_special_fields = SpecialFields::default();
        let mut _entity = UEntity::new();
        _entity.name = _entity_name.unwrap_or_default().to_string();
        _entity.id = Some(_entity_id);
        _entity.version_major = Some(_entity_version_major);
        _entity.version_minor = Some(_entity_version_minor);
        _entity.special_fields = _entity_special_fields;
        println!("_entity: {:?}", _entity);
        let ___entity = MessageField(Some(Box::new(_entity)));

        let _resource_name = match value
            .get("resource")
            .and_then(|resource| resource.get("name"))
        {
            Some(_resource_name) => _resource_name.as_str().expect("issue in name"),
            None => "default",
        };
        let _resource_instance = match value
            .get("resource")
            .and_then(|resource| resource.get("instance"))
        {
            Some(_resource_instance) => _resource_instance.as_str().map(|s| s.to_owned()),
            None => Some(String::from("default")),
        };
        let _resource_message = match value
            .get("resource")
            .and_then(|resource| resource.get("message"))
        {
            Some(_resource_message) => _resource_message.as_str().map(|s| s.to_owned()),
            None => Some(String::from("default")),
        };
        let _resource_id = match value
            .get("resource")
            .and_then(|resource| resource.get("id"))
        {
            Some(_resource_id) => _resource_id
                .clone()
                .as_str()
                .expect("not a string")
                .parse::<u32>()
                .expect("issue in converting to u32"),
            None => 0,
        };
        let _resource_special_fields = SpecialFields::default();
        let mut _resource = UResource::new();
        _resource.name = _resource_name.to_owned();
        _resource.instance = _resource_instance;
        _resource.message = _resource_message;
        _resource.id = Some(_resource_id);

        println!("_resource: {:?}", _resource);
        let ___resource = MessageField(Some(Box::new(_resource)));
        // special field //todo
        let _special_fields = SpecialFields::default();

        Ok(WrapperUUri(UUri {
            authority: ___authority,
            entity: ___entity,
            resource: ___resource,
            special_fields: _special_fields,
        }))
    }
}
#[derive(Default)]
pub struct WrapperUAttribute(pub UAttributes);
impl<'de> Deserialize<'de> for WrapperUAttribute {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        let value: Value = Deserialize::deserialize(deserializer)?;
        println!("WrapperUAttribute: {:?}", value);
        // Conversion function from string to enum variant
        fn from_str_priority(s: &str) -> UPriority {
            match s {
                "UPRIORITY_UNSPECIFIED" => UPriority::UPRIORITY_UNSPECIFIED,
                "UPRIORITY_CS0" => UPriority::UPRIORITY_CS0,
                "UPRIORITY_CS1" => UPriority::UPRIORITY_CS1,
                "UPRIORITY_CS2" => UPriority::UPRIORITY_CS2,
                "UPRIORITY_CS3" => UPriority::UPRIORITY_CS3,
                "UPRIORITY_CS4" => UPriority::UPRIORITY_CS4,
                "UPRIORITY_CS5" => UPriority::UPRIORITY_CS5,
                "UPRIORITY_CS6" => UPriority::UPRIORITY_CS6,
                _ => UPriority::UPRIORITY_UNSPECIFIED,
            }
        }

        fn from_str_type(s: &str) -> UMessageType {
            match s {
                "UMESSAGE_TYPE_PUBLISH" => UMessageType::UMESSAGE_TYPE_PUBLISH,
                "UMESSAGE_TYPE_REQUEST" => UMessageType::UMESSAGE_TYPE_REQUEST,
                "UMESSAGE_TYPE_RESPONSE" => UMessageType::UMESSAGE_TYPE_RESPONSE,
                "UMESSAGE_TYPE_UNSPECIFIED" => UMessageType::UMESSAGE_TYPE_UNSPECIFIED,
                _ => UMessageType::UMESSAGE_TYPE_UNSPECIFIED,
            }
        }

        let _priority = match value.get("priority") {
            Some(_priority) => from_str_priority(
                _priority
                    .as_str()
                    .expect("Deserialize:something wrong with priority field"),
            ),
            None => UPriority::UPRIORITY_UNSPECIFIED,
        };
        println!("_priority: {:?}", _priority);

        let _type = match value.get("type") {
            Some(_type) => from_str_type(
                _type
                    .as_str()
                    .expect("Deserialize:something wrong with _type field"),
            ),
            None => UMessageType::UMESSAGE_TYPE_UNSPECIFIED,
        };
        println!("_type: {:?}", _type);

        let _source = match value.get("source") {
            Some(_source) => {
                serde_json::from_value::<WrapperUUri>(_source.clone()).unwrap_or_default()
            }
            None => WrapperUUri::default(),
        };

        let __source = MessageField(Some(Box::new(_source.0)));
        println!("_source: {:?}", __source);

        let _sink = match value.get("sink") {
            Some(_sink) => serde_json::from_value::<WrapperUUri>(_sink.clone()).unwrap_or_default(),
            None => WrapperUUri::default(),
        };
        let __sink = MessageField(Some(Box::new(_sink.0)));
        println!("_sink: {:?}", __sink);

        let _id_msb = match value.get("id").and_then(|resource| resource.get("msb")) {
            Some(_id_msb) => _id_msb
                .clone()
                .as_str()
                .expect("not a string")
                .parse::<u64>()
                .expect("issue in converting to u32"),
            None => 0,
        };
        let _id_lsb = match value.get("id").and_then(|resource| resource.get("lsb")) {
            Some(_id_lsb) => _id_lsb
                .clone()
                .as_str()
                .expect("not a string")
                .parse::<u64>()
                .expect("issue in converting to u32"),
            None => 0,
        };
        let ___id = UUID {
            msb: _id_msb,
            lsb: _id_lsb,
            special_fields: SpecialFields::default(),
        };
        println!("__id: {:?}", ___id);
        let __id = MessageField(Some(Box::new(___id)));

        let _ttl = match value.get("ttl") {
            Some(_ttl) => _ttl
                .as_str()
                .unwrap_or_else(|| panic!("Deserialize: something wrong with ttl field"))
                .parse::<i32>()
                .expect("ttl parsing error"),
            None => 0,
        };

        let _permission_level = match value.get("permission_level") {
            Some(_permission_level) => _permission_level
                .as_str()
                .unwrap_or_else(|| {
                    panic!("Deserialize: something wrong with permission_level field")
                })
                .parse::<i32>()
                .expect("permission_level parsing error"),
            None => 0,
        };

        let _commstatus = match value.get("commstatus") {
            Some(_commstatus) => _commstatus
                .as_str()
                .unwrap_or_else(|| panic!("Deserialize: something wrong with commstatus field"))
                .parse::<i32>()
                .expect("commstatus parsing error"),
            None => 0,
        };

        let _reqid_msb = match value.get("reqid").and_then(|resource| resource.get("msb")) {
            Some(_reqid_msb) => _reqid_msb
                .clone()
                .as_str()
                .expect("not a string")
                .parse::<u64>()
                .expect("issue in converting to u32"),
            None => 0,
        };
        let _reqid_lsb = match value.get("reqid").and_then(|resource| resource.get("lsb")) {
            Some(_reqid_lsb) => _reqid_lsb
                .clone()
                .as_str()
                .expect("not a string")
                .parse::<u64>()
                .expect("issue in converting to u32"),
            None => 0,
        };
        let ___reqid = UUID {
            msb: _reqid_msb,
            lsb: _reqid_lsb,
            special_fields: SpecialFields::default(),
        };
        println!("__id: {:?}", ___reqid);
        let __reqid = MessageField(Some(Box::new(___reqid)));

        let _token = match value.get("token") {
            Some(_token) => _token
                .as_str()
                .unwrap_or_else(|| panic!("Deserialize: something wrong with token field")),
            None => "Null",
        };

        let _traceparent = match value.get("traceparent") {
            Some(_traceparent) => _traceparent
                .as_str()
                .unwrap_or_else(|| panic!("Deserialize: something wrong with traceparen field")),
            None => "Null",
        };
        // special field //todo
        let _special_fields = SpecialFields::default();
        Ok(WrapperUAttribute(UAttributes {
            special_fields: _special_fields,
            id: __id,
            type_: _type.into(),
            source: __source,
            sink: __sink,
            priority: _priority.into(),
            ttl: Some(_ttl),
            permission_level: Some(_permission_level),
            commstatus: Some(_commstatus),
            reqid: __reqid,
            token: Some(_token.to_owned()),
            traceparent: Some(_traceparent.to_owned()),
        }))
    }
}
#[derive(Default)]
pub struct WrapperUPayload(pub UPayload);
impl<'de> Deserialize<'de> for WrapperUPayload {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        let value: Value = Deserialize::deserialize(deserializer)?;
        println!("WrapperUPayload: {:?}", value);

        fn from_str_format(s: &str) -> UPayloadFormat {
            match s {
                "UPAYLOAD_FORMAT_JSON" => UPayloadFormat::UPAYLOAD_FORMAT_JSON,
                "UPAYLOAD_FORMAT_PROTOBUF" => UPayloadFormat::UPAYLOAD_FORMAT_PROTOBUF,
                "UPAYLOAD_FORMAT_RAW" => UPayloadFormat::UPAYLOAD_FORMAT_RAW,
                "UPAYLOAD_FORMAT_SOMEIP" => UPayloadFormat::UPAYLOAD_FORMAT_SOMEIP,

                "UPAYLOAD_FORMAT_PROTOBUF_WRAPPED_IN_ANY" => {
                    UPayloadFormat::UPAYLOAD_FORMAT_PROTOBUF_WRAPPED_IN_ANY
                }
                "UPAYLOAD_FORMAT_SOMEIP_TLV" => UPayloadFormat::UPAYLOAD_FORMAT_SOMEIP_TLV,
                "UPAYLOAD_FORMAT_TEXT" => UPayloadFormat::UPAYLOAD_FORMAT_TEXT,
                "UPAYLOAD_FORMAT_UNSPECIFIED" => UPayloadFormat::UPAYLOAD_FORMAT_UNSPECIFIED,
                _ => UPayloadFormat::UPAYLOAD_FORMAT_UNSPECIFIED,
            }
        }

        let _format = match value.get("format") {
            Some(_format) => from_str_format(
                _format
                    .as_str()
                    .expect("Deserialize:something wrong with _type field"),
            ),
            None => UPayloadFormat::UPAYLOAD_FORMAT_UNSPECIFIED,
        };

        let _length = match value.get("length") {
            Some(_length) => _length
                .as_str()
                .unwrap_or_else(|| panic!("Deserialize: something wrong with commstatus field"))
                .parse::<i32>()
                .expect("commstatus parsing error"),
            None => 0,
        };

        let _data = match value.get("data") {
            Some(_data) => Data::Reference(_data.to_string().parse().unwrap()),
            None => Data::Reference(0),
        };

        // special field //todo
        let _special_fields = SpecialFields::default();

        Ok(WrapperUPayload(UPayload {
            length: Some(_length),
            format: _format.into(),
            data: _data.into(),
            special_fields: _special_fields,
        }))
    }
}

#[derive(Debug, Default)]

pub struct WrapperUMessage(pub UMessage);

impl<'de> Deserialize<'de> for WrapperUMessage {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        let value: Value = Deserialize::deserialize(deserializer)?;
        println!("WrapperUMessage: {:?} \n", value);
        // let test:UMessage  = value.clone().into();
        // println!("WrapperUMessage after into_proto: {:?}\n", value.clone().into_proto());

        let wattributes = match value.get("attributes") {
            Some(attributes) => {
                serde_json::from_value::<WrapperUAttribute>(attributes.clone()).unwrap_or_default()
            }
            None => WrapperUAttribute(UAttributes::default()),
        };

        let wpayload = match value.get("payload") {
            Some(payload) => {
                serde_json::from_value::<WrapperUPayload>(payload.clone()).unwrap_or_default()
            }
            None => WrapperUPayload(UPayload::default()),
        };

        let mattribute = MessageField::from_option(Some(wattributes.0));
        let mpayload = MessageField::from_option(Some(wpayload.0));

        // special field //todo
        let _special_fields = SpecialFields::default();

        Ok(WrapperUMessage(UMessage {
            attributes: mattribute,
            payload: mpayload,
            special_fields: _special_fields,
        }))
    }
}

#[cfg(test)]
mod tests {
    //use std::any::Any;
    use super::*;
    use protobuf::well_known_types::any::Any;
    use std::net::TcpListener;

    #[test]
    // use std::net::TcpListener;
    fn test_send_receive_socket_data() {
        let listener = TcpListener::bind("127.0.0.1:0").expect("Failed to bind to socket");
        let addr = listener.local_addr().expect("Failed to get local address");

        // Spawn a thread to accept incoming connections
        std::thread::spawn(move || {
            let (mut stream, _) = listener.accept().expect("Failed to accept connection");
            let mut received_data = vec![0; 10];
            receive_socket_data(&mut stream)
                .unwrap()
                .copy_from_slice(&mut received_data);
            assert_eq!(received_data, b"HelloWorld");
        });

        // Connect to the listener's address
        let mut stream = TcpStream::connect(addr).expect("Failed to connect to server");

        // Send data
        send_socket_data(&mut stream, b"HelloWorld").unwrap();
    }

    #[test]
    //use std::net::TcpListener;
    fn test_protobuf_to_base64_and_base64_to_protobuf_bytes() {
        // Create a sample Protocol Buffers Any message
        let mut any = Any::new();

        any.type_url = "example.com/MyMessage".to_string();
        any.value = vec![1, 2, 3, 4, 5];

        // Convert the message to a Base64-encoded string
        let base64_str = protobuf_to_base64(&any);

        // Decode the Base64-encoded string to bytes
        let decoded_bytes = base64_to_protobuf_bytes(&base64_str).unwrap();

        println!("any: {:x?}", any.write_to_bytes().unwrap());
        println!("Decoded bytes: {:x?}", decoded_bytes);
        // Check if the decoded bytes match the original message bytes
        assert_eq!(any.write_to_bytes().unwrap(), decoded_bytes);
    }
    #[test]
    fn test_convert_bytes_to_string() {
        let data = vec![104, 101, 108, 108, 111]; // "hello" in bytes
        let result = convert_bytes_to_string(&data);
        assert_eq!(result, "hello");
    }

    #[test]
    fn test_convert_jsonstring_to_json() {
        let jsonstring = r#"{"key": "value"}"#;
        let result = convert_jsonstring_to_json(jsonstring);
        assert_eq!(result["key"], "value");
    }

    #[test]
    fn test_convert_json_to_jsonstring() {
        let json = serde_json::json!({"key": "value"});
        let result = convert_json_to_jsonstring(&json);
        assert_eq!(result, r#"{"key":"value"}"#);
    }

    #[test]
    fn test_convert_str_to_bytes() {
        let string = "hello";
        let result = convert_str_to_bytes(string);
        assert_eq!(result, vec![104, 101, 108, 108, 111]); // "hello" in bytes
    }

    // Write more test cases for other functions...
}
