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
//use up_rust::{Data, UCode, UListener};
use up_rust::{UCode, UListener};
use up_rust::{UMessage, UStatus, UTransport};

use std::io::{Read, Write};
use std::{collections::HashMap, sync::Arc};
use tokio::sync::Mutex;

use serde::Serialize;

use crate::utils::{convert_json_to_jsonstring, WrapperUMessage, WrapperUUri};
use crate::{constants, utils};
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
    sdk_name: String,
}
impl ListenerHandlers {
    pub fn new(test_clientsocket_to_tm: TcpStream, sdk_name: &str) -> Self {
        let clientsocket_to_tm = Arc::new(Mutex::new(test_clientsocket_to_tm));
        Self { clientsocket_to_tm, sdk_name: sdk_name.to_string() }
    }
}

#[async_trait]
impl UListener for ListenerHandlers {
    async fn on_receive(&self, msg: UMessage) {
        debug!("OnReceive called");

        let value = match &msg.payload {
            Some(bytes) => String::from_utf8_lossy(bytes).to_string(),
            None => "default_value".to_string(),
        };

        // Create a HashMap and insert the key-value pair
        let mut data = HashMap::new();
        data.insert("payload".to_string(), value);

        let json_message = JsonResponseData {
            action: constants::RESPONSE_ON_RECEIVE.to_owned(),
            data,
            ue: self.sdk_name.clone(),
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
        utransport: &dyn UTransport,
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
        let u_message_id = u_message.attributes.id.clone();
        println!("{u_message_id:?}");
        utransport.send(u_message).await
    }

    async fn handle_register_listener_command(
        &self,
        utransport: &dyn UTransport,
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
            .register_listener(&u_uuri, None, Arc::clone(&self.clone().listener))
            .await
    }

    async fn handle_unregister_listener_command(
        &self,
        utransport: &dyn UTransport,
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
            .unregister_listener(&u_uuri, None, Arc::clone(&self.clone().listener))
            .await
    }

    async fn handle_initialize_transport_command(
        &self,
        utransport: &dyn UTransport,
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
        Ok(())
    }

    // async fn handle_uuid_validate_command(
    //     &self,
    //     json_data_value: Value,
    // ) -> Result<(), UStatus> {
    //     let uuid_type: &str = json_data_value.get("uuid_type").unwrap().as_str().unwrap();
    //     let validator_type = json_data_value.get("validator_type").unwrap().as_str().unwrap();

    //     let uuid = match uuid_type {
    //         "uprotocol" => UUID::build(),
    //         "invalid" => match UUID::from_u64_pair(0, 0) {
    //             Ok(uuid) => uuid,
    //             Err(err) => {
    //                 error!("Failed to create UUID: {}", err);
    //                 return Err(UStatus::fail_with_code(UCode::INTERNAL, err.to_string()));
    //             }
    //         },
    //         "uprotocol_time" => {
    //             let start = SystemTime::now();
    //             let since_the_epoch = start
    //                 .duration_since(UNIX_EPOCH)
    //                 .expect("Time went backwards");
    //             match UUID::build_for_timestamp(since_the_epoch) {
    //                 Ok(uuid) => uuid,
    //                 Err(err) => {
    //                     error!("Failed to create UUID: {}", err);
    //                     return Err(UStatus::fail_with_code(UCode::INTERNAL, err.to_string()));
    //                 }
    //             }
    //         },
    //         _ => UUID::build(),
    //     };

    //     Ok(())

    // }

    pub async fn receive_from_tm(
        &mut self,
        utransport: Box<dyn UTransport>,
        ta_to_tm_socket: TcpStream,
        sdk_name: &str,
    ) {
        self.clone().inform_tm_ta_starting(sdk_name).await;
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
                    self.handle_send_command(&*utransport, json_data_value)
                        .await
                }
                constants::REGISTER_LISTENER_COMMAND => {
                    self.handle_register_listener_command(&*utransport, json_data_value)
                        .await
                }
                constants::UNREGISTER_LISTENER_COMMAND => {
                    self.handle_unregister_listener_command(&*utransport, json_data_value)
                        .await
                }
                constants::INITIALIZE_TRANSPORT_COMMAND => {
                    self.handle_initialize_transport_command(&*utransport, json_data_value)
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
                ue: sdk_name.to_string(),
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

    async fn inform_tm_ta_starting(self, sdk_name: &str) {
        let sdk_init = r#"{"ue":""#.to_owned() + sdk_name + r#"","data":{"SDK_name":""#
            + sdk_name
            + r#""},"action":"initialize"}"#;

        //inform TM that rust TA is running
        debug!("Sending SDK name to Test Manager!");
        println!("{sdk_init}");
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
