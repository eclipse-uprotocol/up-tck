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

use log::error;
use serde::{Deserialize, Deserializer};
use serde_json::Value;
use up_rust::{
    Data, UAttributes, UAuthority, UCode, UEntity, UMessage, UMessageType, UPayload,
    UPayloadFormat, UPriority, UResource, UUri, UUID,
};

use protobuf::{Enum, MessageField, SpecialFields};

pub fn convert_json_to_jsonstring<T: serde::Serialize>(value: &T) -> String {
    if let Ok(json_string) = serde_json::to_string(value) {
        json_string
    } else {
        // Handle the error
        error!("Error: Failed to convert to JSON string");
        "None".to_owned()
    }
}

#[derive(Debug, Default)]
pub struct WrapperUUri(pub UUri);
impl<'de> Deserialize<'de> for WrapperUUri {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        let value: Value = Deserialize::deserialize(deserializer)?;
        let mut authority = UAuthority::new();
        let mut uuri: UUri = UUri::new();
        let mut entity = UEntity::new();
        let mut resource = UResource::new();
        //update authority

        if let Some(authority_value) = value
            .get("authority_value")
            .and_then(|authority_value| authority_value.get("name"))
            .and_then(|authority_value| authority_value.as_str())
        {
            authority.name = Some(authority_value.to_owned());
        } else {
            error!("Error: Name field is not a string in authority");
        };

        if let Some(authority_number_ip) = value
            .get("authority")
            .and_then(|authority_value| authority_value.get("number"))
            .and_then(|number| number.get("ip"))
        {
            authority.number = Some(up_rust::Number::Ip(
                authority_number_ip.to_string().as_bytes().to_vec(),
            ));
        } else if let Some(authority_number_id) = value
            .get("authority")
            .and_then(|authority_value| authority_value.get("number"))
            .and_then(|number| number.get("id"))
        {
            authority.number = Some(up_rust::Number::Id(
                authority_number_id.to_string().as_bytes().to_vec(),
            ));
        };

        if let Some(entity_value) = value
            .get("entity")
            .and_then(|entity_value| entity_value.get("name"))
            .and_then(|entity_value| entity_value.as_str())
        {
            entity.name = entity_value.to_owned();
        } else {
            error!("Error: Name field is not a string in entity");
        };

        if let Some(entity_value) = value
            .get("entity")
            .and_then(|entity_value| entity_value.get("id"))
            .and_then(|entity_value| entity_value.as_str())
        {
            if let Ok(entity_id_parsed) = entity_value.parse::<u32>() {
                entity.id = Some(entity_id_parsed);
            } else {
                error!("Error: Not able to parse entity id");
            }
        } else {
            error!("Error: entity id filed is not a string");
        };

        if let Some(entity_value) = value.get("entity").and_then(|entity_value| {
            entity_value
                .get("version_major")
                .and_then(|entity_value| entity_value.as_str())
        }) {
            if let Ok(version_major_parsed) = entity_value.parse::<u32>() {
                entity.version_major = Some(version_major_parsed);
            }
        } else {
            error!("Error: entity_value version major is not a string");
        };

        if let Some(entity_value) = value.get("entity").and_then(|entity_value| {
            entity_value
                .get("version_minor")
                .and_then(|entity_value| entity_value.as_str())
        }) {
            if let Ok(version_minor_parsed) = entity_value.parse::<u32>() {
                entity.version_minor = Some(version_minor_parsed);
            }
        } else {
            error!("Error: entity version minor is not a string");
        };

        entity.special_fields = SpecialFields::default();

        if let Some(resource_value) = value
            .get("resource")
            .and_then(|resource_value| resource_value.get("name"))
            .and_then(|resource_value| resource_value.as_str())
        {
            resource.name = resource_value.to_owned();
        } else {
            error!("Error: Name field is not a string in resource");
        };

        if let Some(resource_value) = value
            .get("resource")
            .and_then(|resource_value| resource_value.get("instance"))
            .and_then(|resource_value| resource_value.as_str())
        {
            resource.instance = Some(resource_value.to_owned());
        } else {
            error!("Error: instance field is not a string in resource");
        }

        if let Some(resource_value) = value
            .get("resource")
            .and_then(|resource_value| resource_value.get("message"))
            .and_then(|resource_value| resource_value.as_str())
        {
            resource.message = Some(resource_value.to_owned());
        } else {
            error!("Error: message field is not a string in resource_value");
        };

        if let Some(resource_value) = value
            .get("resource")
            .and_then(|resource_value| resource_value.get("id"))
            .and_then(|resource_value| resource_value.as_str())
        {
            if let Ok(parsed_id) = resource_value.parse::<u32>() {
                resource.id = Some(parsed_id);
            } else {
                error!("Error: id field parsing to u32");
            }
        } else {
            error!("Error: id field is not string");
        };

        if !(authority.get_name().is_none() && authority.number.is_none()) {
            dbg!(" authority is not default");
            uuri.authority = MessageField(Some(Box::new(authority)));
        }
        uuri.entity = MessageField(Some(Box::new(entity)));
        uuri.resource = MessageField(Some(Box::new(resource)));

        Ok(WrapperUUri(uuri))
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
        let mut uattributes = UAttributes::new();

        if let Some(priority_value) = value.get("priority").and_then(|v| v.as_str()) {
            uattributes.priority = UPriority::from_str(priority_value)
                .unwrap_or_else(|| {
                    // Handle the case where the conversion fails
                    error!("Error:: Something wrong with priority field");
                    UPriority::UPRIORITY_UNSPECIFIED
                })
                .into();
        } else {
            error!("Error:pririty value is not string!");
        }

        dbg!("uattributes.priority: {:?}", uattributes.priority);

        if let Some(type_value) = value.get("type").and_then(|v| v.as_str()) {
            uattributes.type_ = UMessageType::from_str(type_value)
                .unwrap_or_else(|| {
                    // Handle the case where the conversion fails
                    error!("Error: Something wrong with type field");
                    UMessageType::UMESSAGE_TYPE_UNSPECIFIED
                })
                .into();
        } else {
            error!("Error: type value is not string!");
        }

        dbg!("uattributes.type_: {:?}", uattributes.type_);

        if let Some(source_value) = value.get("source") {
            if let Ok(wrapper_uri) = serde_json::from_value::<WrapperUUri>(source_value.clone()) {
                uattributes.source = MessageField(Some(Box::new(wrapper_uri.0)));
            }
        };
        if let Some(sink_value) = value.get("sink") {
            if let Ok(wrapper_uri) = serde_json::from_value::<WrapperUUri>(sink_value.clone()) {
                uattributes.sink = MessageField(Some(Box::new(wrapper_uri.0)));
            }
        };

        let mut ___id = UUID::new();
        if let Some(resource) = value
            .get("id")
            .and_then(|resource| resource.get("lsb"))
            .and_then(|v| v.as_str())
        {
            if let Ok(parsed_id) = resource.parse::<u64>() {
                ___id.lsb = parsed_id;
            } else {
                error!("Error: Failed to parse _id_lsb as u64");
            }
        } else {
            error!("Error: _id_lsb is not a string");
        };

        if let Some(resource) = value
            .get("id")
            .and_then(|resource| resource.get("msb"))
            .and_then(|v| v.as_str())
        {
            if let Ok(parsed_id) = resource.parse::<u64>() {
                ___id.msb = parsed_id;
            } else {
                error!("Error: Failed to parse _id_msb as u64");
            }
        };

        uattributes.id = MessageField(Some(Box::new(___id)));

        if let Some(ttl) = value.get("ttl").and_then(|ttl| ttl.as_str()) {
            if let Ok(parsed_ttl) = ttl.parse::<u32>() {
                uattributes.ttl = parsed_ttl.into();
            } else {
                error!("Error: Failed to parse _ttl as u32");
            }
        };

        if let Some(permission_level) = value
            .get("permission_level")
            .and_then(|permission_level| permission_level.as_str())
        {
            if let Ok(parsed_permission_level) = permission_level.parse::<u32>() {
                uattributes.permission_level = Some(parsed_permission_level);
            } else {
                error!("Error: Failed to parse permission_level as u32");
            }
        };

        if let Some(commstatus_value) = value
            .get("commstatus")
            .and_then(|commstatus_value| commstatus_value.as_str())
        {
            uattributes.commstatus = Some(UCode::from_str(commstatus_value).unwrap().into());
        } else {
            error!("commstatus value is not string");
        };

        dbg!(" uattributes.commstatus: {:?}", uattributes.commstatus);

        let mut ___reqid = UUID::new();
        if let Some(resource) = value
            .get("reqid")
            .and_then(|resource| resource.get("lsb"))
            .and_then(|resource| resource.as_str())
        {
            if let Ok(parsed_id) = resource.parse::<u64>() {
                ___reqid.lsb = parsed_id;
            } else {
                error!("Error: Failed to parse _reqid_lsb as u64");
            }
        };

        if let Some(resource) = value
            .get("reqid")
            .and_then(|resource| resource.get("msb"))
            .and_then(|resource| resource.as_str())
        {
            if let Ok(parsed_id) = resource.parse::<u64>() {
                ___reqid.msb = parsed_id;
            } else {
                dbg!("Error: Failed to parse _reqid_msb as u64");
            }
        };

        uattributes.reqid = MessageField(Some(Box::new(___reqid)));

        if let Some(token) = value.get("token") {
            if let Some(token_str) = token.as_str() {
                uattributes.token = Some(token_str.to_owned());
            } else {
                error!("Error: token is not a string");
            }
        };
        if let Some(traceparent) = value
            .get("traceparent")
            .and_then(|traceparent| traceparent.as_str())
        {
            uattributes.traceparent = Some(traceparent.to_owned());
        } else {
            error!("Error: traceparent is not a string");
        };

        // special field //todo
        let special_fields = SpecialFields::default();

        if special_fields.ne(&SpecialFields::default()) {
            uattributes.special_fields = special_fields;
        }

        Ok(WrapperUAttribute(uattributes))
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
        let mut upayload = UPayload::new();

        if let Some(format_value) = value
            .get("format")
            .and_then(|format_value| format_value.as_str())
        {
            upayload.format = UPayloadFormat::from_str(format_value).unwrap().into();
        } else {
            error!("Error: value of format is not a string");
            upayload.format = UPayloadFormat::UPAYLOAD_FORMAT_UNSPECIFIED.into();
        };

        if let Some(length_value) = value
            .get("length")
            .and_then(|length_value| length_value.as_str())
        {
            if let Ok(parsed_length_value) = length_value.parse::<i32>() {
                upayload.length = Some(parsed_length_value);
            } else {
                error!("Error: Failed to parse permission_level as u32");
            }
        };

        if let Some(data_value) = value.get("value") {
            if let Ok(data_vec) = serde_json::to_vec(data_value) {
                upayload.data = Some(Data::Value(data_vec));
            } else {
                upayload.data = Some(Data::Reference(0));
            }
        }

        Ok(WrapperUPayload(upayload))
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

        Ok(WrapperUMessage(UMessage {
            attributes: Some(wattributes.0).into(),
            payload: Some(wpayload.0).into(),
            special_fields: SpecialFields::default(),
        }))
    }
}

pub fn escape_control_character(c: char) -> String {
    let escaped = format!("\\u{:04x}", c as u32);
    escaped
}

pub fn sanitize_input_string(input: &str) -> String {
    input
        .chars()
        .map(|c| match c {
            '\x00'..='\x1F' => escape_control_character(c),
            _ => c.to_string(),
        })
        .collect()
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
