/**
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

package org.eclipse.uprotocol;

public class Constant {
    public static final String TEST_MANAGER_IP = "127.0.0.5";
    public static final int TEST_MANAGER_PORT = 12345;
    public static final int BYTES_MSG_LENGTH = 32767;
    public static final String SEND_COMMAND = "send";
    public static final String REGISTER_LISTENER_COMMAND = "registerlistener";
    public static final String UNREGISTER_LISTENER_COMMAND = "unregisterlistener";
    public static final String INVOKE_METHOD_COMMAND = "invokemethod";
    public static final String RESPONSE_ON_RECEIVE = "onreceive";
    public static final String RESPONSE_RPC = "rpcresponse";
    public static final String SERIALIZE_URI = "uri_serialize";
    public static final String DESERIALIZE_URI = "uri_deserialize";
    public static final String VALIDATE_URI = "uri_validate";
    public static final String VALIDATE_UUID = "uuid_validate";
    public static final String SERIALIZE_UUID = "uuid_serialize";
    public static final String DESERIALIZE_UUID = "uuid_deserialize";
    public static final String VALIDATE_UATTRIBUTES = "uattributes_validate";
    public static final String MICRO_SERIALIZE_URI = "micro_serialize_uri";
    public static final String MICRO_DESERIALIZE_URI = "micro_deserialize_uri";
}
