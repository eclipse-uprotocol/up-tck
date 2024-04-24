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

 mod constants;

 use async_trait::async_trait;

 use up_rust::UListener;
 use up_rust::{UAttributesValidators, UriValidator};
 use up_rust::{UCode, UMessage, UMessageType, UStatus, UTransport, UUri};
 
 use crate::constants::BYTES_MSG_LENGTH;
 use crate::constants::DISPATCHER_ADDR;
 use protobuf::Message;
 use std::collections::hash_map::Entry;
 use std::collections::HashSet;
 use std::io::{Read, Write};
 use std::net::TcpStream as TcpStreamSync;
 use std::{
     collections::HashMap,
     sync::{Arc, Mutex},
 };
 use tokio::task;
 use up_rust::ComparableListener;
 
 pub struct UTransportSocket {
     socket_sync: TcpStreamSync,
     listener_map: Arc<Mutex<HashMap<UUri, HashSet<ComparableListener>>>>,
 }
 impl Clone for UTransportSocket {
     fn clone(&self) -> Self {
         UTransportSocket {
             socket_sync: self
                 .socket_sync
                 .try_clone()
                 .expect("issue in cloning sync socket"),
             //  listener_map: self.listener_map.clone(),
             listener_map: self.listener_map.clone(),
         }
     }
 }
 
 impl Default for UTransportSocket {
     fn default() -> Self {
         Self::new()
     }
 }
 
 impl UTransportSocket {
     #[must_use]
     /// # Panics
     ///
     /// Will panic if issue connecting in sync socket
     pub fn new() -> Self {
         let _socket_sync: TcpStreamSync =
             TcpStreamSync::connect(DISPATCHER_ADDR).expect("issue in connecting  sync socket");
         let socket_sync = _socket_sync;
         UTransportSocket {
             socket_sync,
             listener_map: Arc::new(Mutex::new(HashMap::new())),
         }
     }
 
     /// # Panics
     ///
     /// Will panic if failed to parse message
     pub fn socket_init(&mut self) {
         loop {
             // Receive data from the socket
             let mut buffer: [u8; BYTES_MSG_LENGTH] = [0; BYTES_MSG_LENGTH];
             let bytes_read = match self.socket_sync.read(&mut buffer) {
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
 
             let umessage =
                 UMessage::parse_from_bytes(&buffer[..bytes_read]).expect("Failed to parse message");
 
             match umessage
                 .attributes
                 .type_
                 .enum_value_or(UMessageType::UMESSAGE_TYPE_UNSPECIFIED)
             {
                 UMessageType::UMESSAGE_TYPE_PUBLISH => {
                     dbg!("calling handle publish....");
                     let _ = self.check_on_receive(&umessage.attributes.source, &umessage);
                 }
                 UMessageType::UMESSAGE_TYPE_NOTIFICATION => todo!(),
                 UMessageType::UMESSAGE_TYPE_UNSPECIFIED | UMessageType::UMESSAGE_TYPE_RESPONSE => (),
                 UMessageType::UMESSAGE_TYPE_REQUEST => {
                     let _ = self.check_on_receive(&umessage.attributes.sink, &umessage);
                 }
             }
         }
     }
 
 
     /// # Panics
     ///
     /// Will panic if something breaks
     /// # Errors
     ///
     /// Will return `Err` if no listeners registered for topic
     pub fn check_on_receive(&self, uuri: &UUri, umessage: &UMessage) -> Result<(), UStatus> {
         let mut topics_listeners = self.listener_map.lock().unwrap();
         let listeners = topics_listeners.entry(uuri.clone());
         dbg!("check_on_receive..\n");
         match listeners {
             Entry::Vacant(_) => {
                 dbg!("check_on_receive 1..\n");
                 return Err(UStatus::fail_with_code(
                     UCode::NOT_FOUND,
                     format!("No listeners registered for topic: {:?}", &uuri),
                 ));
             }
             Entry::Occupied(mut e) => {
                 let occupied = e.get_mut();
                 dbg!("check_on_receive 2..\n");
                 if occupied.is_empty() {
                     return Err(UStatus::fail_with_code(
                         UCode::NOT_FOUND,
                         format!("No listeners registered for topic: {:?}", &uuri),
                     ));
                 }
                 dbg!("invoking listner on receive..\n");
                 for listener in occupied.iter() {
                     let task_listener = listener.clone();
                     let task_umessage = umessage.clone();
                     dbg!("invoking listner on receive\n");
                     task::spawn(async move { task_listener.on_receive(task_umessage).await });
                 }
             }
         }
 
         Ok(())
     }
 }
 
 #[async_trait]
 impl UTransport for UTransportSocket {
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
         let mut socket_clone = self.socket_sync.try_clone().expect("issue in sending data");
 
         let umsg_serialized = message
             .clone()
             .write_to_bytes()
             .expect("Send Serialization Issue");
         let _result = UMessage::parse_from_bytes(&umsg_serialized.clone());
         //todo: handle result
 
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
                     Ok(()) => Ok(()),
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
                     Ok(()) => Ok(()),
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
                     Ok(()) => Ok(()),
                     Err(_) => Err(UStatus::fail_with_code(
                         UCode::UNAVAILABLE,
                         "Dispatcher communication issue",
                     )),
                 }
             }
             UMessageType::UMESSAGE_TYPE_UNSPECIFIED | UMessageType::UMESSAGE_TYPE_NOTIFICATION => {
                 Err(UStatus::fail_with_code(
                     UCode::INVALID_ARGUMENT,
                     "Wrong Message type in UAttributes",
                 ))
             }
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
             dbg!(topic.authority.is_some());
             dbg!(UriValidator::is_remote(&topic));
             UriValidator::validate(&topic)
                 .map_err(|err| UStatus::fail_with_code(UCode::INVALID_ARGUMENT, err.to_string()))?;
 
             if UriValidator::is_rpc_response(&topic) {
                 let mut topics_listeners = self.listener_map.lock().unwrap();
                 let listeners = topics_listeners.entry(topic).or_default();
                 let identified_listener = ComparableListener::new(listener);
                 let inserted = listeners.insert(identified_listener);
 
                 return if inserted {
                     Ok(())
                 } else {
                     Err(UStatus::fail_with_code(
                         UCode::ALREADY_EXISTS,
                         "UUri + UListener pair already exists!",
                     ))
                 };
             } else if UriValidator::is_rpc_method(&topic) {
                 let mut topics_listeners = self.listener_map.lock().unwrap();
                 let listeners = topics_listeners.entry(topic).or_default();
                 let identified_listener = ComparableListener::new(listener);
                 let inserted = listeners.insert(identified_listener);
                 dbg!("register listner called for rpc !");
                 return if inserted {
                     Ok(())
                 } else {
                     Err(UStatus::fail_with_code(
                         UCode::ALREADY_EXISTS,
                         "UUri + UListener pair already exists!",
                     ))
                 };
             }
             let mut topics_listeners = self.listener_map.lock().unwrap();
             let listeners = topics_listeners.entry(topic).or_default();
             let identified_listener = ComparableListener::new(listener);
             let inserted = listeners.insert(identified_listener);
             dbg!("register listner called for topic !");
             return if inserted {
                 Ok(())
             } else {
                 Err(UStatus::fail_with_code(
                     UCode::ALREADY_EXISTS,
                     "UUri + UListener pair already exists!",
                 ))
             };
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
         let mut topics_listeners = self.listener_map.lock().unwrap();
         let listeners = topics_listeners.entry(topic.clone());
         return match listeners {
             Entry::Vacant(_) => Err(UStatus::fail_with_code(
                 UCode::NOT_FOUND,
                 format!("No listeners registered for topic: {:?}", &topic),
             )),
             Entry::Occupied(mut e) => {
                 let occupied = e.get_mut();
                 let identified_listener = ComparableListener::new(listener);
                 let removed = occupied.remove(&identified_listener);
 
                 if removed {
                     Ok(())
                 } else {
                     Err(UStatus::fail_with_code(
                         UCode::NOT_FOUND,
                         "UUri + UListener not found!",
                     ))
                 }
             }
         };
     }
 }
 