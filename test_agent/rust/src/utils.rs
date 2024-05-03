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
    UPayloadFormat, UPriority, UResource, UStatus, UUri, UUID,
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

pub fn get_ustatus_code(u_status: &UStatus) -> u32 {
    match u_status.get_code() {
        UCode::OK => 0,
        UCode::INTERNAL => 13,
        UCode::ABORTED => 10,
        UCode::ALREADY_EXISTS => 6,
        UCode::CANCELLED => 1,
        UCode::DATA_LOSS => 15,
        UCode::DEADLINE_EXCEEDED => 4,
        UCode::FAILED_PRECONDITION => 9,
        UCode::INVALID_ARGUMENT => 3,
        UCode::NOT_FOUND => 5,
        UCode::OUT_OF_RANGE => 11,
        UCode::PERMISSION_DENIED => 7,
        UCode::RESOURCE_EXHAUSTED => 8,
        UCode::UNAUTHENTICATED => 16,
        UCode::UNAVAILABLE => 14,
        UCode::UNIMPLEMENTED => 12,
        UCode::UNKNOWN => 2,
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
        let authority = if let Ok(authority) = parse_uauthority(&value) {
            authority
        } else {
            let err_msg = "Error parsing authority: ".to_string();
            error!("{}", err_msg);
            UAuthority::default()
        };

        let resource = parse_uresource(&value);
        let entity = parse_uentity(&value);

        let uuri = if authority.get_name().is_none() && authority.number.is_none() {
            UUri {
                entity: MessageField(Some(Box::new(entity))),
                resource: MessageField(Some(Box::new(resource))),
                ..Default::default() // If authority is default, fill in the rest with default values
            }
        } else {
            dbg!(" authority is not default");
            UUri {
                authority: MessageField(Some(Box::new(authority))),
                entity: MessageField(Some(Box::new(entity))),
                resource: MessageField(Some(Box::new(resource))),
                ..Default::default()
            }
        };

        Ok(WrapperUUri(uuri))
    }
}

fn parse_uresource(value: &Value) -> UResource {
    let mut uresource = UResource::new();
    if let Some(resource_value) = value
        .get("resource")
        .and_then(|resource_value| resource_value.get("name"))
        .and_then(|resource_value| resource_value.as_str())
    {
        uresource.name = resource_value.to_owned();
    } else {
        error!("Error: name field is not a string in resource");
    };

    if let Some(resource_value) = value
        .get("resource")
        .and_then(|resource_value| resource_value.get("instance"))
        .and_then(|resource_value| resource_value.as_str())
    {
        uresource.instance = Some(resource_value.to_owned());
    } else {
        error!("Error: instance field is not a string in resource");
        //Some("None".to_owned())
    };

    if let Some(resource_value) = value
        .get("resource")
        .and_then(|resource_value| resource_value.get("message"))
        .and_then(|resource_value| resource_value.as_str())
    {
        uresource.message = Some(resource_value.to_owned());
    } else {
        error!("Error: message field is not a string in resource_value");
        //Some("None".to_owned())
    };

    if let Some(resource_value) = value
        .get("resource")
        .and_then(|resource_value| resource_value.get("id"))
        .and_then(|resource_value| resource_value.as_str())
    {
        if let Ok(parsed_id) = resource_value.parse::<u32>() {
            uresource.id = Some(parsed_id);
        } else {
            error!("Error: id field parsing to u32");
            // Some(0)
        }
    } else {
        error!("Error: id field is not string");
        //Some(0)
    };
    uresource
}

fn parse_string_field(value: &Value, field: &str) -> Result<String, serde_json::Error> {
    if let Some(entity_value) = value
        .get("entity")
        .and_then(|entity_value| entity_value.get(field))
        .and_then(|field_value| field_value.as_str())
    {
        Ok(entity_value.to_owned())
    } else {
        error!("Error: {field} field is not a string");
        Err(serde::de::Error::custom(format!(
            "Error: {field} field is not a string"
        )))
    }
}

fn parse_u32_field(value: &Value, field: &str) -> Result<Option<u32>, serde_json::Error> {
    if let Some(entity_value) = value
        .get("entity")
        .and_then(|entity_value| entity_value.get(field))
        .and_then(|field_value| field_value.as_str())
    {
        if let Ok(parsed_value) = entity_value.parse::<u32>() {
            Ok(Some(parsed_value))
        } else {
            error!("Error: {field} is not a number");
            Err(serde::de::Error::custom(format!(
                "Error: {field} is not a number"
            )))
        }
    } else {
        error!("Error: {} field is not a string", field);
        Err(serde::de::Error::custom(format!(
            "Error: {field} field is not a string"
        )))
    }
}

fn parse_uentity(value: &Value) -> UEntity {
    let name = match parse_string_field(value, "name") {
        Ok(value) => value,
        Err(_) => "None".to_owned(),
    };

    let id = match parse_u32_field(value, "id") {
        Ok(value) => value,
        Err(_) => None,
    };

    let version_major = match parse_u32_field(value, "version_major") {
        Ok(value) => value,
        Err(_) => None,
    };

    let version_minor = match parse_u32_field(value, "version_minor") {
        Ok(value) => value,
        Err(_) => None,
    };

    UEntity {
        name,
        id,
        version_major,
        version_minor,
        special_fields: SpecialFields::default(),
    }
}

fn parse_uauthority(value: &Value) -> Result<UAuthority, serde_json::Error> {
    let name = if let Some(authority_value) = value
        .get("authority")
        .and_then(|authority_value| authority_value.get("name"))
        .and_then(|authority_value| authority_value.as_str())
    {
        Some(authority_value.to_owned())
    } else {
        return Err(serde::de::Error::custom("Missing value authority name"));
    };

    let number = if let Some(authority_number_ip) = value
        .get("authority")
        .and_then(|authority_value| authority_value.get("number"))
        .and_then(|number| number.get("ip"))
    {
        Some(up_rust::Number::Ip(
            authority_number_ip.to_string().as_bytes().to_vec(),
        ))
    } else if let Some(authority_number_id) = value
        .get("authority")
        .and_then(|authority_value| authority_value.get("number"))
        .and_then(|number| number.get("id"))
    {
        Some(up_rust::Number::Id(
            authority_number_id.to_string().as_bytes().to_vec(),
        ))
    } else {
        return Err(serde::de::Error::custom("Missing value number"));
    };

    Ok(UAuthority {
        name,
        number,
        special_fields: SpecialFields::default(),
    })
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

        let Ok(id) = parse_uuid(&value, "id") else {
            let err_msg = "Error parsing UUID id: ".to_string();
            return Err(serde::de::Error::custom(err_msg));
        };

        uattributes.id = MessageField(Some(Box::new(id)));

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

        if let Ok(reqid) = parse_uuid(&value, "reqid") {
            uattributes.reqid = MessageField(Some(Box::new(reqid)));
        } else {
            let err_msg = "Error parsing UUID reqid: ".to_string();
            error!("{}", err_msg);
        }

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

        // special field
        let special_fields = SpecialFields::default();

        if special_fields.ne(&SpecialFields::default()) {
            uattributes.special_fields = special_fields;
        }

        Ok(WrapperUAttribute(uattributes))
    }
}

#[allow(clippy::similar_names)]
fn parse_uuid(value: &Value, uuid: &str) -> Result<UUID, serde_json::Error> {
    let get_field = |field: &str| -> Option<u64> {
        value
            .get(uuid)
            .and_then(|uuid| uuid.get(field))
            .and_then(|uuid| uuid.as_str())
            .and_then(|value| value.parse().ok())
    };

    let Some(lsb) = get_field("lsb") else {
        let err_msg = "Missing ".to_string() + "reqid.lsb field";
        error!("{}", err_msg);
        return Err(serde::de::Error::custom(err_msg));
    };

    let Some(msb) = get_field("msb") else {
        let err_msg = "Missing ".to_string() + "reqid.msb field";
        error!("{}", err_msg);
        return Err(serde::de::Error::custom(err_msg));
    };

    Ok(UUID {
        lsb,
        msb,
        special_fields: SpecialFields::default(),
    })
}

#[derive(Default)]
pub struct WrapperUPayload(pub UPayload);
impl<'de> Deserialize<'de> for WrapperUPayload {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        let value: Value = Deserialize::deserialize(deserializer)?;
        let Ok(upayload) = parse_upayload(&value) else {
            let err_msg = "Error parsing payload: ".to_string();
            return Err(serde::de::Error::custom(err_msg));
        };

        Ok(WrapperUPayload(upayload))
    }
}

fn parse_upayload(value: &Value) -> Result<UPayload, serde_json::Error> {
    let format = if let Some(format_value) = value
        .get("format")
        .and_then(|format_value| format_value.as_str())
    {
        UPayloadFormat::from_str(format_value).unwrap().into()
    } else {
        error!("Error: value of format is not a string");
        UPayloadFormat::UPAYLOAD_FORMAT_UNSPECIFIED.into()
    };

    let length = value
        .get("length")
        .and_then(Value::as_str)
        .and_then(|length_value| length_value.parse::<i32>().ok());

    let data = if let Some(data_value) = value.get("value") {
        if let Ok(data_vec) = serde_json::to_vec(data_value) {
            Some(Data::Value(data_vec))
        } else {
            Some(Data::Reference(0))
        }
    } else {
        return Err(serde::de::Error::custom("Missing value field"));
    };

    Ok(UPayload {
        format,
        length,
        data,
        special_fields: SpecialFields::default(),
    })
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
