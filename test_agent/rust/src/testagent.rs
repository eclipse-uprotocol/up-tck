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

use async_trait::async_trait;
use log::{debug, error};
use serde_json::Value;
use up_rust::{Data, UCode, UListener};
use up_rust::{UMessage, UStatus, UTransport};

use std::io::{Read, Write};
use std::{collections::HashMap, sync::Arc};
use tokio::sync::Mutex;

use serde::Serialize;

use crate::constants::SDK_INIT_MESSAGE;
use crate::utils::{convert_json_to_jsonstring, WrapperUMessage, WrapperUUri};
use crate::{constants, utils, UTransportSocket};
use std::net::TcpStream;

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
    clientsocket: Arc<Mutex<TcpStream>>,

    listener: Arc<dyn UListener>,
}
#[derive(Clone)]
pub struct ListenerHandlers {
    clientsocket_to_tm: Arc<Mutex<TcpStream>>,
}
impl ListenerHandlers {
    pub fn new(test_clientsocket_to_tm: TcpStream) -> Self {
        let clientsocket_to_tm = Arc::new(Mutex::new(test_clientsocket_to_tm));
        Self { clientsocket_to_tm }
    }
}

#[async_trait]
impl UListener for ListenerHandlers {
    async fn on_receive(&self, msg: UMessage) {
        debug!("OnReceive called");

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
                debug!("No data available");
                "none".into()
            }
        };

        let Ok(value_str) = serde_json::to_string(
            &[("value".to_string(), data_payload.to_string())]
                .iter()
                .cloned()
                .collect::<HashMap<_, _>>(),
        ) else {
            error!("Issue in converting to payload");
            return;
        };

        let Ok(payload_str) = serde_json::to_string(
            &[("payload".to_string(), value_str.to_string())]
                .iter()
                .cloned()
                .collect::<HashMap<_, _>>(),
        ) else {
            error!("Issue in converting to payload");
            return;
        };

        let data = [("data".to_string(), payload_str.to_string())]
            .iter()
            .cloned()
            .collect::<HashMap<_, _>>();
        let json_message = JsonResponseData {
            action: constants::RESPONSE_ON_RECEIVE.to_owned(),
            data,
            ue: "rust".to_string(),
            test_id: "1".to_string(),
        };

        debug!("sending received data to tm....");
        let json_message_str = convert_json_to_jsonstring(&json_message);
        let message = json_message_str.as_bytes();

        let Ok(mut socket) = self.clientsocket_to_tm.try_lock() else {
            error!("Failed to acquire lock for sending data to TM from on_receive");
            return;
        };

        let result = socket.write_all(message);
        match result {
            Ok(()) => println!("on receive could send data to TM"),
            Err(err) => error!("on receive could not send data to TM: {err}"),
        }
    }

    async fn on_error(&self, _err: UStatus) {
        debug!("{}", _err);
    }
}

impl SocketTestAgent {
    pub fn new(test_clientsocket: TcpStream, listener: Arc<dyn UListener>) -> Self {
        let clientsocket = Arc::new(Mutex::new(test_clientsocket));

        Self {
            clientsocket,
            listener,
        }
    }

    async fn handle_send_command(
        &self,
        utransport: &UTransportSocket,
        json_data_value: Value,
    ) -> Result<(), UStatus> {
        let wrapper_umessage: WrapperUMessage = match serde_json::from_value(json_data_value) {
            Ok(message) => message,
            Err(err) => {
                let err_string = format!("Failed to Deserialize: {err}");
                error!("{err_string}");
                return Err(UStatus::fail_with_code(UCode::INTERNAL, err_string));
            }
        };
        let u_message = wrapper_umessage.0;
        utransport.send(u_message).await
    }

    async fn handle_register_listener_command(
        &self,
        utransport: &UTransportSocket,
        json_data_value: Value,
    ) -> Result<(), UStatus> {
        let wrapper_uuri: WrapperUUri = match serde_json::from_value(json_data_value) {
            Ok(message) => message,
            Err(err) => {
                let err_string = format!("Failed to Deserialize: {err}");
                error!("{err_string}");
                return Err(UStatus::fail_with_code(UCode::INTERNAL, err_string));
            }
        };
        let u_uuri = wrapper_uuri.0;
        utransport
            .register_listener(u_uuri, Arc::clone(&self.clone().listener))
            .await
    }

    async fn handle_unregister_listener_command(
        &self,
        utransport: &UTransportSocket,
        json_data_value: Value,
    ) -> Result<(), UStatus> {
        let wrapper_uuri: WrapperUUri = match serde_json::from_value(json_data_value) {
            Ok(message) => message,
            Err(err) => {
                let err_string = format!("Failed to Unregister Listener: {err}");
                error!("{err_string}");
                return Err(UStatus::fail_with_code(UCode::INTERNAL, err_string));
            }
        };
        let u_uuri = wrapper_uuri.0;
        utransport
            .unregister_listener(u_uuri, Arc::clone(&self.clone().listener))
            .await
    }

    pub async fn receive_from_tm(
        &mut self,
        utransport: UTransportSocket,
        ta_to_tm_socket: TcpStream,
    ) {
        self.clone().inform_tm_ta_starting().await;
        let clientsocket = self.clientsocket.clone();
        let mut socket = clientsocket.lock().await;

        let mut recv_data = [0; 2048];
        // Use `while let` to handle reads
        while let Ok(bytes_received) = socket.read(&mut recv_data) {
            if bytes_received == 0 {
                // Handling the case when the connection is closed properly
                debug!("Connection closed by the peer.");
                break;
            }

            let recv_data_str: std::borrow::Cow<'_, str> =
                String::from_utf8_lossy(&recv_data[..bytes_received]);
            let cleaned_json_string = sanitize_input_string(&recv_data_str).replace("BYTES:", "");

            let json_msg: Value = match serde_json::from_str(&cleaned_json_string.to_string()) {
                Ok(json) => json,
                Err(err) => {
                    error!("error in converting json_msg to string{}", err);
                    continue;
                }
            };

            let action = json_msg["action"].clone();
            let json_data_value = json_msg["data"].clone();
            let test_id = json_msg["test_id"].clone();

            let Some(json_str_ref) = action.as_str() else {
                error!("action is not a string");
                continue;
            };

            let status = match json_str_ref {
                constants::SEND_COMMAND => {
                    self.handle_send_command(&utransport, json_data_value).await
                }
                constants::REGISTER_LISTENER_COMMAND => {
                    self.handle_register_listener_command(&utransport, json_data_value)
                        .await
                }
                constants::UNREGISTER_LISTENER_COMMAND => {
                    self.handle_unregister_listener_command(&utransport, json_data_value)
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
                    let enum_number = UStatus::get_code(&u_status) as i32;
                    status_dict.insert("code".to_string(), enum_number.to_string());
                }
            }

            let json_message = JsonResponseData {
                action: json_str_ref.to_owned(),
                data: status_dict.clone(),
                ue: "rust".to_owned(),
                test_id: test_id.to_string(),
            };

            let Ok(ta_to_tm_socket_clone) = ta_to_tm_socket.try_clone() else {
                error!("Socket cloning failed for ta to tm socket clone");

                continue;
            };

            let json_message_str = convert_json_to_jsonstring(&json_message);
            let message = json_message_str.as_bytes();
            let result = ta_to_tm_socket_clone
                .try_clone()
                .and_then(|mut socket_clone| socket_clone.write_all(message));
            match result {
                Ok(()) => println!("on receive could send init to TM"),
                Err(err) => error!("on receive could not send init to TM{}", err),
            }
        }
        self.close_connection().await;
    }

    async fn inform_tm_ta_starting(self) {
        let sdk_init = SDK_INIT_MESSAGE;

        //inform TM that rust TA is running
        debug!("Sending SDK name to Test Manager!");
        let message = sdk_init.as_bytes();
        let clientsocket = self.clientsocket.clone();
        let mut socket = clientsocket.lock().await;

        let result = socket.write_all(message);
        match result {
            Ok(()) => println!("on receive could send init to TM"),
            Err(err) => error!("on receive could not send init to TM{}", err),
        }
    }

    pub async fn close_connection(&self) {
        let clientsocket = self.clientsocket.clone();
        let socket = clientsocket.lock().await;

        match socket.shutdown(std::net::Shutdown::Both) {
            Ok(()) => {
                debug!("Connection closed");
            }
            Err(err) => {
                error!("Error closing connection: {}", err);
            }
        }
    }
}
