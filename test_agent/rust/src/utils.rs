/*
 * SPDX-FileCopyrightText: Copyright (c) 2024 Contributors to the Eclipse Foundation
 *
 * See the NOTICE file(s) distributed with this work for additional
 * information regarding copyright ownership.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http: *www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * SPDX-FileType: SOURCE
 * SPDX-License-Identifier: Apache-2.0
 */

use log::{debug, error, info};
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
        let authority = parse_uauthority(&value);
        if authority.is_none() {
            info!("No UAuthority parsed");
        }

        let resource = parse_uresource(&value);
        let entity = parse_uentity(&value);

        let uuri = match authority {
            Some(authority) => {
                debug!("Authority is not default");
                UUri {
                    authority: Some(authority).into(),
                    entity: Some(entity).into(),
                    resource: Some(resource).into(),
                    ..Default::default()
                }
            }
            None => UUri {
                entity: Some(entity).into(),
                resource: Some(resource).into(),
                ..Default::default()
            },
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
    };

    if let Some(resource_value) = value
        .get("resource")
        .and_then(|resource_value| resource_value.get("message"))
        .and_then(|resource_value| resource_value.as_str())
    {
        uresource.message = Some(resource_value.to_owned());
    } else {
        error!("Error: message field is not a string in resource_value");
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
        }
    } else {
        error!("Error: id field is not string");
    };
    uresource
}

fn parse_string_field(
    message: &str,
    value: &Value,
    field: &str,
) -> Result<String, serde_json::Error> {
    if let Some(msg_value) = value
        .get(message)
        .and_then(|msg_value| msg_value.get(field))
        .and_then(|field_value| field_value.as_str())
    {
        Ok(msg_value.to_owned())
    } else {
        let err_str = format!("Error: {field} field is not a string");
        error!("{err_str}");
        Err(serde::de::Error::custom(err_str))
    }
}

fn parse_u32_field(
    message: &str,
    value: &Value,
    field: &str,
) -> Result<Option<u32>, serde_json::Error> {
    if let Some(msg_value) = value
        .get(message)
        .and_then(|msg_value| msg_value.get(field))
        .and_then(|field_value| field_value.as_str())
    {
        if let Ok(parsed_value) = msg_value.parse::<u32>() {
            Ok(Some(parsed_value))
        } else {
            let err_str = format!("Error: {field} field is not a number");
            error!("{err_str}");
            Err(serde::de::Error::custom(err_str))
        }
    } else {
        let err_str = format!("Error: {field} field is not a string");
        error!("{err_str}");
        Err(serde::de::Error::custom(err_str))
    }
}

fn parse_uentity(value: &Value) -> UEntity {
    let name = parse_string_field("entity", value, "name")
        .ok()
        .unwrap_or_else(|| "None".to_owned());
    let id = parse_u32_field("entity", value, "id").ok().flatten();
    let version_major = parse_u32_field("entity", value, "version_major")
        .ok()
        .flatten();
    let version_minor = parse_u32_field("entity", value, "version_minor")
        .ok()
        .flatten();

    UEntity {
        name,
        id,
        version_major,
        version_minor,
        special_fields: SpecialFields::default(),
    }
}

fn parse_uauthority(value: &Value) -> Option<UAuthority> {
    let name = if let Some(authority_value) = value
        .get("authority")
        .and_then(|authority_value| authority_value.get("name"))
        .and_then(|authority_value| authority_value.as_str())
    {
        Some(authority_value.to_owned())
    } else {
        error!("Error: Missing value authority name");
        return None;
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
        error!("Error: Missing value number");
        return None;
    };

    Some(UAuthority {
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
        let mut uattributes = UAttributes::default();

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

        debug!("uattributes.priority: {:?}", uattributes.priority);

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

        debug!("uattributes.type_: {:?}", uattributes.type_);

        if let Some(source_value) = value.get("source") {
            if let Ok(wrapper_uri) = serde_json::from_value::<WrapperUUri>(source_value.clone()) {
                uattributes.source = Some(wrapper_uri.0).into();
            }
        };
        if let Some(sink_value) = value.get("sink") {
            if let Ok(wrapper_uri) = serde_json::from_value::<WrapperUUri>(sink_value.clone()) {
                uattributes.sink = Some(wrapper_uri.0).into();
            }
        };

        let Ok(id) = parse_uuid(&value, "id") else {
            let err_msg = "Error parsing UUID id: ".to_string();
            return Err(serde::de::Error::custom(err_msg));
        };

        uattributes.id = MessageField(Some(Box::new(id)));

        if value.get("ttl").and_then(|ttl| ttl.as_str()).is_some() {
            if let Ok(Some(parsed_ttl)) = parse_u32_field("entity", &value, "ttl") {
                uattributes.ttl = parsed_ttl.into();
            } else {
                error!("Error: Failed to parse ttl as u32");
            }
        }

        if value
            .get("permission_level")
            .and_then(|permission_level| permission_level.as_str())
            .is_some()
        {
            if let Ok(Some(parsed_permission_level)) =
                parse_u32_field("entity", &value, "permission_level")
            {
                uattributes.permission_level = Some(parsed_permission_level);
            } else {
                error!("Error: Failed to parse permission_level as u32");
            }
        };

        match parse_string_field("entity", &value, "commstatus") {
            Ok(commstatus_str) => {
                if let Some(code) = UCode::from_str(&commstatus_str) {
                    uattributes.commstatus = Some(code.into());
                } else {
                    error!("Failed to parse commstatus string into UCode.");
                }
            }
            Err(err) => {
                error!("Error parsing commstatus field: {}", err);
            }
        }

        debug!(" uattributes.commstatus: {:?}", uattributes.commstatus);

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

        uattributes.special_fields = SpecialFields::default();

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

#[allow(clippy::map_unwrap_or)]
fn parse_upayload(value: &Value) -> Result<UPayload, serde_json::Error> {
    let format = value
        .get("format")
        .and_then(|format_value| format_value.as_str())
        .map(|format_str| {
            UPayloadFormat::from_str(format_str).unwrap_or_else(|| {
                error!("Error: Unable to parse string to UPayloadFormat");
                UPayloadFormat::UPAYLOAD_FORMAT_UNSPECIFIED
            })
        })
        .unwrap_or_else(|| {
            error!("Error: value of format is not a string");
            UPayloadFormat::UPAYLOAD_FORMAT_UNSPECIFIED
        });

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
        format: format.into(),
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

        let wattributes = value
            .get("attributes")
            .and_then(|attributes| {
                serde_json::from_value::<WrapperUAttribute>(attributes.clone()).ok()
            })
            .map(|wrapper_attr| wrapper_attr.0);

        let wpayload = value
            .get("payload")
            .and_then(|payload| serde_json::from_value::<WrapperUPayload>(payload.clone()).ok())
            .map(|wrapper_payload| wrapper_payload.0);

        Ok(WrapperUMessage(UMessage {
            attributes: wattributes.into(),
            payload: wpayload.into(),
            special_fields: SpecialFields::default(),
        }))
    }
}

pub fn escape_control_character(c: char) -> String {
    format!("\\u{:04x}", c as u32)
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
