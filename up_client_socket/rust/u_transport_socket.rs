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

use async_std::io;
use async_trait::async_trait;
use tokio::runtime::Runtime;
use up_rust::UListener;
use up_rust::{UAttributesValidators, UriValidator};
use up_rust::{UCode, UMessage, UMessageType, UStatus, UTransport, UUri};

use protobuf::Message;
use std::net::TcpStream as TcpStreamSync;
use std::{
    collections::HashMap,
    sync::{Arc, Mutex},
};
use std::io::{Read, Write};

use crate::constants::BYTES_MSG_LENGTH;
use crate::constants::DISPATCHER_ADDR;

pub trait UtransportExt {
     fn socket_init(&mut self);
     fn _handle_publish_message(&mut self, umsg: UMessage);
     fn _handle_request_message(&mut self, umsg: UMessage);
    fn read_socket(&self, buffer: &mut [u8]) -> io::Result<usize>;
}

pub struct UtransportSocket {
    socket_sync: TcpStreamSync,
    listner_map: Arc<Mutex<HashMap<String, Vec<Arc<dyn UListener>>>>>,
}
impl Clone for UtransportSocket {
    fn clone(&self) -> Self {
        UtransportSocket {
            socket_sync: self
                .socket_sync
                .try_clone()
                .expect("issue in cloning sync socket"),
            listner_map: self.listner_map.clone(),
        }
    }
}

impl UtransportSocket {
    pub fn new() -> Self {
        let socket_sync: TcpStreamSync =
            TcpStreamSync::connect(DISPATCHER_ADDR).expect("issue in connecting  sync socket");

        UtransportSocket {
            socket_sync,
            listner_map: Arc::new(Mutex::new(HashMap::new())),
        }
    }
}

impl UtransportExt for UtransportSocket {
     fn socket_init(&mut self) {
        loop {
            // Receive data from the socket
            let mut buffer: [u8; BYTES_MSG_LENGTH] = [0; BYTES_MSG_LENGTH];

            let bytes_read = match self.read_socket(&mut buffer) {
                Ok(bytes_read) => bytes_read,
                Err(e) => {
                    dbg!("Socket error: {}", e);
                    break;
                }
            };

            // Check if no data is received
            if bytes_read == 0 {
                continue;
            }

            let umessage = UMessage::parse_from_bytes(&buffer[..bytes_read]).expect("Failed to parse message");

            match umessage.attributes.type_.enum_value() {
                Ok(mt) => match mt {
                    UMessageType::UMESSAGE_TYPE_PUBLISH => {
                        println!("calling handle publish...");
                        self._handle_publish_message(umessage);
                        ()
                    }
                    UMessageType::UMESSAGE_TYPE_NOTIFICATION => todo!(),
                    UMessageType::UMESSAGE_TYPE_UNSPECIFIED => (),
                    UMessageType::UMESSAGE_TYPE_RESPONSE => (),
                    UMessageType::UMESSAGE_TYPE_REQUEST => {
                        self._handle_request_message(umessage);
                        ()
                    }
                },
                Err(_) => (),
            }
        }
    }

    fn read_socket(&self, buffer: &mut [u8]) -> io::Result<usize> {
        let mut socket = &self.socket_sync;

        socket.read(buffer)
    }

     fn _handle_publish_message(&mut self, umsg: UMessage) {
        dbg!("HANDLING PUB MESG");
        // Create a new Tokio runtime
        let rt = Runtime::new().unwrap();
   
        dbg!(&umsg.attributes.source.to_string());
    
        if let Some(listner_array) = self
            .listner_map
            .lock()
            .unwrap()
            .get(&umsg.attributes.source.to_string())
        {
            for listner_ref in listner_array {
                rt.block_on(async {
                    let _ = listner_ref.on_receive(umsg.clone()).await;
                });
            }
        }
    }

     fn _handle_request_message(&mut self, umsg: UMessage) {

        let rt_ = Runtime::new().unwrap();
        if let Some(listner_array) = self
            .listner_map
            .lock()
            .unwrap()
            .get(&umsg.attributes.sink.to_string())
        {
            for listner_ref in listner_array {
                rt_.block_on(async {
                let _ = listner_ref.on_receive(umsg.clone()).await;
            });
        }
    }
}
}
#[async_trait]
impl UTransport for UtransportSocket {
    /// Sends a message using this transport's message exchange mechanism.
    ///
    /// # Arguments
    ///
    /// * `message` - The message to send. The `type`, `source` and`sink` properties of the [`crate::UAttributes`] contained
    ///   in the message determine the addressing semantics:
    ///   * `source` - The origin of the message being sent. The address must be resolved. The semantics of the address
    ///     depends on the value of the given [attributes' type](crate::UAttributes::type_) property .
    ///     * For a [`PUBLISH`](crate::UMessageType::UMESSAGE_TYPE_PUBLISH) message, this is the topic that the message should be published to,
    ///     * for a [`REQUEST`](crate::UMessageType::UMESSAGE_TYPE_REQUEST) message, this is the *reply-to* address that the sender expects to receive the response at, and
    ///     * for a [`RESPONSE`](crate::UMessageType::UMESSAGE_TYPE_RESPONSE) message, this identifies the method that has been invoked.
    ///   * `sink` - For a `notification`, an RPC `request` or RPC `response` message, the (resolved) address that the message
    ///     should be sent to.
    ///
    /// # Errors
    ///
    /// Returns an error if the message could not be sent.
    async fn send(&self, message: UMessage) -> Result<(), UStatus> {
        let mut socket_clone = self
            .socket_sync
            .try_clone()
            .expect("dispatcher socket connection cloning failed");

        let umsg_serialized = message.clone().write_to_bytes().expect("Send Serialization Issue");
        let _ = UMessage::parse_from_bytes(&umsg_serialized.clone()).expect("Failed to parse message");
        let _payload = *message
            .payload
            .0
            .ok_or(UStatus::fail_with_code(UCode::INVALID_ARGUMENT, "Invalid uPayload").clone())?;
        let attributes = *message.attributes.0.ok_or(
            UStatus::fail_with_code(UCode::INVALID_ARGUMENT, "Invalid uAttributes").clone(),
        )?;

        // Check the type of UAttributes (Publish / Request / Response)
        match attributes
            .type_
            .enum_value()
            .map_err(|_| UStatus::fail_with_code(UCode::INTERNAL, "Unable to parse type"))?
        {
            UMessageType::UMESSAGE_TYPE_PUBLISH => {
                // PublishValidator::validate(, &attributes) /* .map(|e|{ UStatus::fail_with_code(UCode::INVALID_ARGUMENT,format!("wrong Publish Uattribute{e:?}"),})?;*/
                println!("UMESSAGE_TYPE_PUBLISH sending data");
                UAttributesValidators::Publish
                    .validator()
                    .validate(&attributes)
                    .map_err(|e| {
                        UStatus::fail_with_code(
                            UCode::INVALID_ARGUMENT,
                            format!("Wrong Publish UAttributes {e:?}"),
                        )
                    })?;

                match socket_clone.write_all(&umsg_serialized) {
                    Ok(_) => Err(UStatus::ok()),
                    Err(_) => Err(UStatus::fail_with_code(
                        UCode::UNAVAILABLE,
                        "Dispatcher communication issue",
                    )),
                }
            }
            UMessageType::UMESSAGE_TYPE_REQUEST => {
                UAttributesValidators::Request
                    .validator()
                    .validate(&attributes)
                    .map_err(|e| {
                        UStatus::fail_with_code(
                            UCode::INVALID_ARGUMENT,
                            format!("Wrong Request UAttributes {e:?}"),
                        )
                    })?;

                match socket_clone.write_all(&umsg_serialized) {
                    Ok(_) => Err(UStatus::ok()),
                    Err(_) => Err(UStatus::fail_with_code(
                        UCode::UNAVAILABLE,
                        "Dispatcher communication issue",
                    )),
                }
            }
            UMessageType::UMESSAGE_TYPE_RESPONSE => {
                UAttributesValidators::Response
                    .validator()
                    .validate(&attributes)
                    .map_err(|e| {
                        UStatus::fail_with_code(
                            UCode::INVALID_ARGUMENT,
                            format!("Wrong Response UAttributes {e:?}"),
                        )
                    })?;
                match socket_clone.write_all(&umsg_serialized) {
                    Ok(_) => Err(UStatus::ok()),
                    Err(_) => Err(UStatus::fail_with_code(
                        UCode::UNAVAILABLE,
                        "Dispatcher communication issue",
                    )),
                }
            }
            UMessageType::UMESSAGE_TYPE_UNSPECIFIED => Err(UStatus::fail_with_code(
                UCode::INVALID_ARGUMENT,
                "Wrong Message type in UAttributes",
            )),
            UMessageType::UMESSAGE_TYPE_NOTIFICATION => Err(UStatus::fail_with_code(
                UCode::INVALID_ARGUMENT,
                "Wrong Message type in UAttributes",
            )),
        }
    }

    /// Receives a message from the transport.
    ///
    /// # Arguments
    ///
    /// * `topic` - The topic to receive the message from.
    ///
    /// # Errors
    ///
    /// Returns an error if no message could be received. Possible reasons are that the topic does not exist
    /// or that no message is available from the topic.
    async fn receive(&self, _topic: UUri) -> Result<UMessage, UStatus> {
        Err(UStatus::fail_with_code(
            UCode::UNIMPLEMENTED,
            "Not implemented",
        ))
    }

    /// Registers a listener to be called for each message that is received on a given address.
    ///
    /// # Arguments
    ///
    /// * `address` - The (resolved) address to register the listener for.
    /// * `listener` - The listener to invoke.
    ///
    /// # Returns
    ///
    /// An identifier that can be used for [unregistering the listener](Self::unregister_listener) again.
    ///
    /// # Errors
    ///
    /// Returns an error if the listener could not be registered.
    ///
    ///
    ///
    ///
    ///

    async fn register_listener(
        &self,
        topic: UUri,
        listener: Arc<dyn UListener>,
    ) -> Result<(), UStatus> {
        dbg!("register listner called !");
        if topic.authority.is_some() && topic.entity.is_none() && topic.resource.is_none() {
            // This is special UUri which means we need to register for all of Publish, Request, and Response
            // RPC response
            Err(UStatus::fail_with_code(
                UCode::UNIMPLEMENTED,
                "Not implemented",
            ))
        } else {
            // Do the validation
            UriValidator::validate(&topic)
                .map_err(|_| UStatus::fail_with_code(UCode::INVALID_ARGUMENT, "Invalid topic"))?;

            if UriValidator::is_rpc_response(&topic) {
                self.listner_map
                    .lock()
                    .unwrap()
                    .entry(topic.to_string())
                    .and_modify(|listener_local| listener_local.push(listener.clone()))
                    .or_insert_with(|| vec![Arc::clone(&listener)as Arc<dyn UListener>]);

                Ok(())
            } else if UriValidator::is_rpc_method(&topic) {
                self.listner_map
                    .lock()
                    .unwrap()
                    .entry(topic.to_string())
                    .and_modify(|listener_local| listener_local.push(listener.clone()))
                    .or_insert_with(|| vec![Arc::clone(&listener) as Arc<dyn UListener>]);
                dbg!("register listner called for rpc !");
                Ok(())
            } else {
                self.listner_map
                    .lock()
                    .unwrap()
                    .entry(topic.to_string())
                    .and_modify(|listener_local| listener_local.push(listener.clone()))
                    .or_insert_with(|| vec![Arc::clone(&listener) as Arc<dyn UListener>]);
                dbg!("register listner called for topic !");
                Err(UStatus::ok())
            }
        }
    }

    /// Unregisters a listener for a given topic.
    ///
    /// Messages arriving on this topic will no longer be processed by this listener.
    ///
    /// # Arguments
    ///
    /// * `topic` - Resolved topic uri where the listener was registered originally.
    /// * `listener` - Identifier of the listener that should be unregistered.
    ///
    /// # Errors
    ///
    /// Returns an error if the listener could not be unregistered, for example if the given listener does not exist.
    async fn unregister_listener(
        &self,
        topic: UUri,
        listener: Arc<dyn UListener>,
    ) -> Result<(), UStatus> {
        let mut map = self.listner_map.lock().expect("Failed to acquire lock");
        let listner_clone = Arc::clone(&listener) as Arc<dyn UListener>;

        if let Some(listeners) = map.get_mut(&topic.to_string()) {
            if let Some(index) = listeners
                .iter()
                .position(|l| Arc::ptr_eq(l, &listner_clone))
            {
                let _ = listeners.remove(index);

                // If the vector becomes empty after removal, delete the entry from the map
                if listeners.is_empty() {
                    map.remove(&topic.to_string());
                }
            }
        }

        Err(UStatus::ok())
    }
}
