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


use serde_json::Value;
use serde::{Deserialize, Deserializer};
use up_rust::{
    Data, UAttributes, UAuthority, UCode, UEntity, UMessage, UMessageType, UPayload,
    UPayloadFormat, UPriority, UResource, UUri, UUID,
};

use protobuf::{MessageField, SpecialFields};

pub fn convert_json_to_jsonstring<T: serde::Serialize>(value: &T) -> String {
    serde_json::to_string(value).expect("Failed to convert to JSON string")
}

#[derive(Debug, Default)]
pub struct WrapperUUri(pub UUri);
impl<'de> Deserialize<'de> for WrapperUUri {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        let value: Value = Deserialize::deserialize(deserializer)?;
        //dbg!("WrapperUUri: {:?}", value.);

        //update authority
        let _authority_name = match value
            .get("authority")
            .and_then(|authority| authority.get("name"))
        {
            Some(_authority_name) => _authority_name.as_str(),
            None => Some("default"),
        };

        let _authority_number_ip = match value
            .get("authority")
            .and_then(|authority| authority.get("number"))
            .and_then(|number| number.get("Ip"))
        {
            Some(_authority_number_ip) => _authority_number_ip.to_string().as_bytes().to_vec(),
            None => {
                let default: Vec<u8> = vec![0];
                default
            }
        };
        let _authority_number_id = match value
            .get("authority")
            .and_then(|authority| authority.get("number"))
            .and_then(|number| number.get("Id"))
        {
            Some(_authority_number_id) => _authority_number_id.to_string().as_bytes().to_vec(),
            None => {
                let default: Vec<u8> = vec![0];
                default
            }
        };

        let mut _authority = UAuthority::new();
        if!( _authority_name.clone() == Some("default")){
            _authority.name = _authority_name.map(|s| s.to_string());
        }
        if!(_authority_number_id.clone() == vec![0]){
            _authority.set_id(_authority_number_id.clone());
        }
        if!(_authority_number_ip.clone() == vec![0]){
            _authority.set_ip(_authority_number_ip.clone());
        }

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
        if!(_entity_id == 0)
        {
        _entity.id = Some(_entity_id)
        };
        if!(_entity_version_major == 0)
        {
        _entity.version_major = Some(_entity_version_major)
        };
        if!(_entity_version_minor == 0)
        {
        _entity.version_minor = Some(_entity_version_minor)
        };
        _entity.special_fields = _entity_special_fields;
      //  dbg!("_entity: {:?}", _entity);
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
        if!(_resource_id == 0)
        {
        _resource.id = Some(_resource_id)
    };

        let ___resource = MessageField(Some(Box::new(_resource)));
        let _special_fields = SpecialFields::default();
    let mut _uuri:UUri = UUri::new();
    if!(_authority_name.clone() == Some("default") && _authority_number_id.clone() == vec![0] && _authority_number_ip.clone() == vec![0]){
        dbg!("authority is not default");
        _uuri.authority = MessageField(Some(Box::new(_authority)));
    }
    _uuri.entity = ___entity;
    _uuri.resource = ___resource;


        Ok(WrapperUUri(_uuri))
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
        // Conversion function from string to enum variant
        fn from_str_comstatus(s: &str) -> UCode {
            match s {
                "ABORTED" => UCode::ABORTED,
                "OK" => UCode::OK,
                "CANCELLED" => UCode::CANCELLED,
                "UNKOWN" => UCode::UNKNOWN,
                "INVALID_ARGUMENT" => UCode::INVALID_ARGUMENT,
                "DEADLINE_EXCEEDED" => UCode::DEADLINE_EXCEEDED,
                "NOT_FOUND" => UCode::NOT_FOUND,
                "ALREADY_EXISTS" => UCode::ALREADY_EXISTS,
                "PERMISSION_DENIED" => UCode::PERMISSION_DENIED,
                "UNAUTHENTICATED" => UCode::UNAUTHENTICATED,
                "RESOURCE_EXHAUSTED" => UCode::RESOURCE_EXHAUSTED,
                "FAILED_PRECONDITION" => UCode::FAILED_PRECONDITION,
                "OUT_OF_RANGE" => UCode::OUT_OF_RANGE,
                "UNIMPLEMENTED" => UCode::UNIMPLEMENTED,
                "INTERNAL" => UCode::INTERNAL,
                "UNAVAILABLE" => UCode::UNAVAILABLE,
                "DATA_LOSS" => UCode::DATA_LOSS,
                &_ => todo!(),
            }
        }
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
        dbg!("_priority: {:?}", _priority);

        let _type = match value.get("type") {
            Some(_type) => from_str_type(
                _type
                    .as_str()
                    .expect("Deserialize:something wrong with _type field"),
            ),
            None => UMessageType::UMESSAGE_TYPE_UNSPECIFIED,
        };
        dbg!("_type: {:?}", _type);

        let _source = match value.get("source") {
            Some(_source) => {
                serde_json::from_value::<WrapperUUri>(_source.clone()).unwrap_or_default() 
            }
            None => WrapperUUri::default(),
        };


        let _sink = match value.get("sink") {
            Some(_sink) => serde_json::from_value::<WrapperUUri>(_sink.clone()).unwrap_or_default(),
            None => WrapperUUri::default(),
        };


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
      
        let __id = MessageField(Some(Box::new(___id)));

        let _ttl = match value.get("ttl") {
            Some(_ttl) => _ttl
                .as_str()
                .unwrap_or_else(|| panic!("Deserialize: something wrong with ttl field"))
                .parse::<u32>()
                .expect("ttl parsing error"),
            None => 0,
        };

        let _permission_level = match value.get("permission_level") {
            Some(_permission_level) => _permission_level
                .as_str()
                .unwrap_or_else(|| {
                    panic!("Deserialize: something wrong with permission_level field")
                })
                .parse::<u32>()
                .expect("permission_level parsing error"),
            None => 0,
        };

        let _commstatus = match value.get("commstatus") {
            Some(_commstatus) => from_str_comstatus(
                _commstatus
                    .as_str()
                    .expect("Deserialize:something wrong with commstatus field"),
            ),
            None => UCode::OUT_OF_RANGE,
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
        let mut _uattributes =  UAttributes::new();
       if _special_fields.ne(&SpecialFields::default()){
        _uattributes.special_fields = _special_fields;
       }
        _uattributes.id = __id;
        _uattributes.type_ = _type.into();

        
        if !(_source.0.clone() == UUri::default()) {
        _uattributes.source = MessageField(Some(Box::new(_source.0)));
        }
        if!(_sink.0.clone() == UUri::default()){
            _uattributes.sink = MessageField(Some(Box::new(_sink.0)));
            }
            _uattributes.priority = _priority.into();
            _uattributes.ttl = _ttl.into();
            _uattributes.permission_level = Some(_permission_level.into());
            _uattributes.commstatus = Some(_commstatus.into());
            _uattributes.reqid = __reqid;
            _uattributes.token= Some(_token.to_owned());
            _uattributes.traceparent = Some(_traceparent.to_owned());
        
        Ok(WrapperUAttribute( _uattributes))
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

        
         
        let _data = match value.get("value") {
            Some(_data) => Data::Value( serde_json::to_vec(_data).expect("error in converting data value to vector")),
            None => Data::Reference(0),
        };

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
       // dbg!("mattribute: {:?} \n", mattribute);
        let mpayload = MessageField::from_option(Some(wpayload.0));
       // dbg!("mpayload: {:?} \n", mpayload);
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

    use super::*;

    #[test]
    fn test_convert_json_to_jsonstring() {
        let json = serde_json::json!({"key": "value"});
        let result = convert_json_to_jsonstring(&json);
        assert_eq!(result, r#"{"key":"value"}"#);
    }

}


// use prost::Message; // Import the prost crate for protobuf message handling
use std::fmt::Debug;

// Function to serialize any protobuf message to JSON string
// fn protobuf_to_json<M: Message>(message: &M) -> Result<String, serde_json::Error> {
//     // Serialize the protobuf message to bytes
//     let bytes = message.encode_to_vec();

//     // Deserialize the bytes into a JSON value
//     let json_value = serde_json::from_slice(&bytes)?;

//     // Serialize the JSON value into a JSON string
//     let json_string = serde_json::to_string(&json_value)?;

//     Ok(json_string)
// }
