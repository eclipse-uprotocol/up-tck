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

use async_trait::async_trait;
use log::error;
use serde_json::Value;
use up_rust::{Data, UCode, UListener};
use up_rust::{UMessage, UStatus, UTransport};

use std::io::{Read, Write};
use std::{
    collections::HashMap,
    sync::{Arc, Mutex},
};

use serde::Serialize;

use crate::utils::{convert_json_to_jsonstring, WrapperUMessage, WrapperUUri};
use crate::{constants, utils, TcpStreamSync, UTransportSocket};

use self::utils::sanitize_input_string;

#[derive(Serialize)]
pub struct JsonResponseData {
    data: HashMap<String, String>,
    action: String,
    ue: String,
    test_id: String,
}
#[derive(Clone)]
pub struct SocketTestAgent {
    utransport: UTransportSocket,
    clientsocket: Arc<Mutex<TcpStreamSync>>,
    clientsocket_to_tm: Arc<Mutex<TcpStreamSync>>,
}

#[async_trait]
impl UListener for SocketTestAgent {
    async fn on_receive(&self, msg: UMessage) {
        dbg!("OnReceive called");

        let data_payload = match &msg.payload.data {
            Some(data) => {
                // Now we have access to the Data enum
                match data {
                    Data::Reference(reference) => reference.to_string(),
                    Data::Value(value) => {
                        let value_str = String::from_utf8_lossy(value);
                        value_str.to_string()
                    }
                    _ => "none".into(),
                }
            }
            None => {
                dbg!("No data available");
                "none".into()
            }
        };

        let mut value: HashMap<String, String> = HashMap::new();
        value.insert("value".into(), data_payload);
        let Ok(value_str) = serde_json::to_string(&value) else {
            error!("issue in converting to payload");
            return;
        };

        let mut payload: HashMap<String, String> = HashMap::new();
        payload.insert("payload".into(), value_str);
        let Ok(payload_str) = serde_json::to_string(&payload) else {
            error!("issue in converting to payload");
            return;
        };

        let mut json_message = JsonResponseData {
            action: constants::RESPONSE_ON_RECEIVE.to_owned(),
            data: HashMap::new(),
            ue: "rust".to_string(),
            test_id: "1".to_string(),
        };

        json_message.data.insert("data".into(), payload_str);

        //<SocketTestAgent as Clone>::clone(&self)
        //todo: revisit this and check:Better pattern might be to have the UListener be impled on a different struct
        //e.g. SocketTestListener that then holds an Arc<Mutex<SocketTestAgent>> to be able to call send_to_tm() on that instead.
        dbg!("sending received data to tm....");
        self.clone().send_to_tm(json_message).await;
    }

    async fn on_error(&self, _err: UStatus) {
        todo!();
    }
}

impl SocketTestAgent {
    pub fn new(
        test_clientsocket: TcpStreamSync,
        test_clientsocket_to_tm: TcpStreamSync,
        utransport: UTransportSocket,
    ) -> Self {
        let clientsocket = Arc::new(Mutex::new(test_clientsocket));
        let clientsocket_to_tm = Arc::new(Mutex::new(test_clientsocket_to_tm));
        Self {
            utransport,
            clientsocket,
            clientsocket_to_tm,
        }
    }

    pub async fn receive_from_tm(&mut self) {
        let arc_self = Arc::new(self.clone());
        self.clone().inform_tm_ta_starting();

        let mut socket = if let Ok(socket) = self.clientsocket.lock() {
            socket
        } else {
            error!("Error: Error accessing TM server");
            return;
        };

        loop {
            let mut recv_data = [0; 2048];
            let bytes_received = match socket.read(&mut recv_data) {
                Ok(bytes_received) => bytes_received,
                Err(e) => {
                    // Handle socket errors (e.g., connection closed)
                    dbg!("Socket error: {}", e);
                    break;
                }
            };
            if bytes_received == 0 {
                continue;
            }

            let recv_data_str: std::borrow::Cow<'_, str> =
                String::from_utf8_lossy(&recv_data[..bytes_received]);
            let mut action_str = "";
            let cleaned_json_string = sanitize_input_string(&recv_data_str).replace("BYTES:", "");
            let json_msg: Value =
                serde_json::from_str(&cleaned_json_string.to_string()).expect("issue in from str"); // Assuming serde_json is used for JSON serialization/deserialization

            let action = json_msg["action"].clone();
            let json_data_value = json_msg["data"].clone();
            let test_id = json_msg["test_id"].clone();

            let json_str_ref = action
                .as_str()
                .expect("issue in converting value to string");

            dbg!(json_str_ref);
            let status = match json_str_ref {
                constants::SEND_COMMAND => {
                    let wu_message: WrapperUMessage =
                        serde_json::from_value(json_data_value).unwrap(); // convert json to UMessage
                    let u_message = wu_message.0;
                    action_str = constants::SEND_COMMAND;
                    self.utransport.send(u_message).await
                }

                constants::REGISTER_LISTENER_COMMAND => {
                    let cloned_listener = Arc::clone(&arc_self);

                    let wu_uuri: WrapperUUri = serde_json::from_value(json_data_value).unwrap(); // convert json to UMessage
                    let u_uuri = wu_uuri.0;
                    action_str = constants::REGISTER_LISTENER_COMMAND;
                    self.utransport
                        .register_listener(
                            u_uuri,
                            Arc::clone(&cloned_listener) as Arc<dyn UListener>,
                        )
                        .await
                }

                constants::UNREGISTER_LISTENER_COMMAND => {
                    let cloned_listener = Arc::clone(&arc_self);
                    let wu_uuri: WrapperUUri = serde_json::from_value(json_data_value).unwrap(); // convert json to UMessage
                    let u_uuri = wu_uuri.0;
                    action_str = constants::UNREGISTER_LISTENER_COMMAND;
                    self.utransport
                        .unregister_listener(
                            u_uuri,
                            Arc::clone(&cloned_listener) as Arc<dyn UListener>, /*&cloned_listener*/
                        )
                        .await
                }

                _ => Ok(()),
            };

            let mut status_dict: HashMap<String, _> = HashMap::new();

            match status {
                Ok(()) => {
                    let status = UStatus::default();
                    status_dict.insert(
                        "message".to_string(),
                        status.message.clone().unwrap_or_default(),
                    );
                    status_dict.insert("code".to_string(), 0.to_string());
                }
                Err(u_status) => {
                    status_dict.insert(
                        "message".to_string(),
                        u_status.message.clone().unwrap_or_default(),
                    );
                    let enum_number = match u_status.get_code() {
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
                    };
                    status_dict.insert("code".to_string(), enum_number.to_string());
                }
            }

            let json_message = JsonResponseData {
                action: action_str.to_owned(),
                data: status_dict.clone(),
                ue: "rust".to_owned(),
                test_id: test_id.to_string(),
            };

            <SocketTestAgent as Clone>::clone(self)
                .send_to_tm(json_message)
                .await;
        }
        self.close_connection();
    }

    fn inform_tm_ta_starting(self) {
        let sdk_init = r#"{"ue":"rust","data":{"SDK_name":"rust"},"action":"initialize"}"#;

        //inform TM that rust TA is running
        dbg!("Sending SDK name to Test Manager!");
        let message = sdk_init.as_bytes();

        let socket_clone = self.clientsocket.clone();
        let _ = socket_clone
            .lock()
            .expect("error in sending data to TM")
            .write_all(message);
        //todo: handle result
    }

    async fn send_to_tm(self, json_message: JsonResponseData) {
        let json_message_str = convert_json_to_jsonstring(&json_message);
        let message = json_message_str.as_bytes();

        let socket_clone = self.clientsocket_to_tm.clone();
        let _ = socket_clone
            .try_lock()
            .expect("error in sending data to TM")
            .write_all(message);
        //todo:handle result
    }
    pub fn close_connection(&self) {
        todo!();
    }
}
