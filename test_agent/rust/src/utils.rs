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

use bytes::Bytes;
use log::{debug, error};
use protobuf::{Enum, MessageField};
use serde::{Deserialize, Deserializer};
use serde_json::Value;
use up_rust::{UAttributes, UCode, UMessage, UMessageType, UPriority, UUri, UUID};

pub fn convert_json_to_jsonstring<T: serde::Serialize>(value: &T) -> String {
    if let Ok(json_string) = serde_json::to_string(value) {
        json_string
    } else {
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

        let authority_name = if let Some(authority_value) = value
            .get("authority_name")
            .and_then(|authority_value| authority_value.as_str())
        {
            Some(authority_value.to_owned())
        } else {
            error!("Error: Missing value authority name");
            Some("default".to_owned())
        };

        let ue_id = if let Some(ue_id_value) = value
            .get("ue_id")
            .and_then(|ue_id_value| ue_id_value.as_str())
        {
            if let Ok(parsed_value) = ue_id_value.parse::<u32>() {
                Some(parsed_value)
            } else {
                let err_str = "Error: ue_id field is not a number";
                error!("{err_str}");
                Some(0)
            }
        } else {
            let err_str = "Error: ue_id_value field is not a string";
            error!("{err_str}");
            Some(0)
        };

        let ue_version_major = if let Some(ue_version_major_value) = value
            .get("ue_version_major")
            .and_then(|ue_version_major_value| ue_version_major_value.as_str())
        {
            if let Ok(parsed_value) = ue_version_major_value.parse::<u32>() {
                Some(parsed_value)
            } else {
                let err_str = "Error: ue_version_major field is not a number";
                error!("{err_str}");
                Some(0)
            }
        } else {
            let err_str = "Error: ue_version_major_value field is not a string";
            error!("{err_str}");
            Some(0)
        };

        let resource_id = if let Some(resource_id_value) = value
            .get("resource_id")
            .and_then(|resource_id_value| resource_id_value.as_str())
        {
            if let Ok(parsed_value) = resource_id_value.parse::<u32>() {
                Some(parsed_value)
            } else {
                let err_str = "Error: resource_id field is not a number";
                error!("{err_str}");
                Some(0)
            }
        } else {
            let err_str = "Error: resource_id_value field is not a string";
            error!("{err_str}");
            Some(0)
        };

        let uuri = UUri {
            authority_name: authority_name.expect("todo"),
            ue_id: ue_id.expect("todo"),
            ue_version_major: ue_version_major.expect("todo"),
            resource_id: resource_id.expect("todo"),
            ..Default::default()
        };
        Ok(WrapperUUri(uuri))
    }
}

fn parse_string_field(value: &Value, field: &str) -> Result<String, serde_json::Error> {
    if let Some(msg_value) = value
        .get(field)
        .and_then(|field_value| field_value.as_str())
    {
        Ok(msg_value.to_owned())
    } else {
        let err_str = format!("Error: {field} field is not a string");
        error!("{err_str}");
        error!("{value}");
        let new_val = value.get(field).unwrap();
        error!("{new_val}");
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

        match parse_string_field(&value, "commstatus") {
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

        if value.get("type") != Some(&Value::String("UMESSAGE_TYPE_PUBLISH".to_string())) {
            if let Ok(reqid) = parse_uuid(&value, "reqid") {
                uattributes.reqid = MessageField(Some(Box::new(reqid)));
            } else {
                let err_msg = "Error parsing UUID reqid: ".to_string();
                error!("{}", err_msg);
            }
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
        msb,
        lsb,
        ..Default::default()
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

        let payload = if let Some(payload_value) = value.get("payload") {
            // Check if the word BYTES: is in the payload, if so, remove it
            let payload_value = if let Some(payload_str) = payload_value.as_str() {
                if payload_str.starts_with("BYTES:") {
                    payload_str.trim_start_matches("BYTES:").to_string()
                } else {
                    payload_str.to_string()
                }
            } else {
                "default value".to_string()
            };
            // Then convert the payload to bytes
            Bytes::from(payload_value.into_bytes())
        } else {
            return Err(serde::de::Error::custom("Missing value field"));
        };

        Ok(WrapperUMessage(UMessage {
            attributes: wattributes.into(),
            payload: Some(payload),
            ..Default::default()
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
