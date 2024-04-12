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

pub const SEND_COMMAND: &str = "send";
pub const REGISTER_LISTENER_COMMAND: &str= "registerlistener";
pub const UNREGISTER_LISTENER_COMMAND: &str = "unregisterlistener";

pub const RESPONSE_ON_RECEIVE: &str = "onreceive";

// Define constants for addresses
pub const DISPATCHER_ADDR: (&str, u16) = ("127.0.0.1", 44444);
pub const TEST_MANAGER_ADDR: (&str, u16) = ("127.0.0.5", 12345);

// Define constant for maximum message length
pub const BYTES_MSG_LENGTH: usize = 32767;

#[test]
pub fn test_constants() {
    dbg!("SEND_COMMAND: {}", SEND_COMMAND);
    dbg!("REGISTER_LISTENER_COMMAND: {}", REGISTER_LISTENER_COMMAND);
    dbg!(
        "UNREGISTER_LISTENER_COMMAND: {}",
        UNREGISTER_LISTENER_COMMAND
    );
    dbg!("DISPATCHER_ADDR: {:?}", DISPATCHER_ADDR);
    dbg!("TEST_MANAGER_ADDR: {:?}", TEST_MANAGER_ADDR);
    dbg!("BYTES_MSG_LENGTH: {}", BYTES_MSG_LENGTH);
}
