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
 * SPDX-FileCopyrightText: 2024 General Motors GTO LLC
 * SPDX-License-Identifier: Apache-2.0
 */

package org.tck.examples;

import com.google.protobuf.Any;
import org.eclipse.uprotocol.rpc.CallOptions;
import org.eclipse.uprotocol.uri.serializer.LongUriSerializer;
import org.eclipse.uprotocol.v1.*;
import org.tck.up_client_socket_java.SocketRPCClient;

import java.io.IOException;
import java.net.Socket;
import java.util.concurrent.CompletionStage;

public class TestRpcClient {
    public static void main(String[] args) throws IOException {

        Socket clientSocket = new Socket();
        SocketRPCClient socketRPCClient = new SocketRPCClient("127.0.0.1", 44444, clientSocket);
        System.out.println("Connected to RpcClient");

        CompletionStage<UMessage> response = socketRPCClient.invokeMethod(TestRpcClient.buildTopic(), TestRpcClient.buildUPayload(), CallOptions.newBuilder().build());
        System.out.println("Response ->"+response);
    }

    private static UUri buildTopic() {
        return LongUriSerializer.instance().deserialize("/body.access//door.front_left#Door");
    }

    private static UPayload buildUPayload() {
        Any any = Any.pack(buildCloudEvent());
        return UPayload.newBuilder()
                .setFormat(UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF)
                .setValue(any.toByteString())
                .build();
    }

    private static io.cloudevents.v1.proto.CloudEvent buildCloudEvent() {
        return io.cloudevents.v1.proto.CloudEvent.newBuilder().setSpecVersion("1.0").setId("TEST")
                .setSource("http://example.com").build();
    }
}
