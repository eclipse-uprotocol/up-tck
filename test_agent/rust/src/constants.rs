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

pub const SEND_COMMAND: &str = "send";
pub const REGISTER_LISTENER_COMMAND: &str = "registerlistener";
pub const UNREGISTER_LISTENER_COMMAND: &str = "unregisterlistener";
pub const SDK_INIT_MESSAGE: &str =
    r#"{"ue":"rust","data":{"SDK_name":"rust"},"action":"initialize"}"#;

pub const RESPONSE_ON_RECEIVE: &str = "onreceive";

pub const TEST_MANAGER_ADDR: (&str, u16) = ("127.0.0.5", 12345);

pub const ZENOH_TRANSPORT: &str = "zenoh";
pub const SOMEIP_TRANSPORT: &str = "someip";
