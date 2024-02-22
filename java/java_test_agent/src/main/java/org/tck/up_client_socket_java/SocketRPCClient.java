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

package org.tck.up_client_socket_java;

import org.eclipse.uprotocol.rpc.CallOptions;
import org.eclipse.uprotocol.transport.builder.UAttributesBuilder;
import org.eclipse.uprotocol.v1.*;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionStage;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class SocketRPCClient {
    private Socket socket;

    public SocketRPCClient(String hostIp, int port, Socket socket) throws IOException {
        if (socket != null) {
            this.socket = socket;
        } else {
            this.socket = new Socket();
            this.socket.connect(new InetSocketAddress(hostIp, port));
        }
    }

    private UMessage sendToServiceSocket(UUri topic, UPayload payload, CallOptions callOptions) throws IOException {

        UUID requestId = UUID.getDefaultInstance();
        byte[] requestIdB = requestId.toString().getBytes();
        UUri sink = UUri.newBuilder().build();
        UAttributesBuilder builder = UAttributesBuilder.request(topic, sink, UPriority.UPRIORITY_CS4, callOptions.timeout());
        UAttributes attributes = builder.build();

        UMessage umsg = UMessage.newBuilder()
                .setAttributes(attributes)
                .setPayload(payload)
                .build();
        System.out.println("UMessage: \n" + umsg);
        byte[] umsg_bytes = umsg.toByteArray();

        socket.getOutputStream().write(umsg_bytes);

        while (true) {
            int msg_len = 32767;
            byte[] recv_data = new byte[msg_len];
            int readBytes = socket.getInputStream().read(recv_data);
            if (readBytes == -1) {
                continue;
            }
            UMessage responseUmsg = null;
            try {
                responseUmsg.parseFrom(recv_data);
            } catch (UnsupportedOperationException ue) {
                System.out.println("Data isn't type UMessage: \n" + ue.toString());
                continue;
            } catch (Exception err) {
                throw new RuntimeException(err);
            }
            if(responseUmsg.hasAttributes()) {
                UUID response_reqid = responseUmsg.getAttributes().getReqid();
                if (requestId.equals(response_reqid)) {
                    System.out.println("Got response: \n" + responseUmsg.toString());
                    return responseUmsg;
                } else {
                    System.out.println("Response wasn't meant for current client: \n" + responseUmsg.toString());
                    continue;
                }
            }
        }
    }

    public CompletionStage<UMessage> invokeMethod(UUri topic, UPayload payload, CallOptions callOptions) {
        ExecutorService executor = Executors.newFixedThreadPool(1);

        CompletableFuture<UMessage> response = CompletableFuture.supplyAsync(() -> {
            try {
                return this.sendToServiceSocket(topic, payload, callOptions);
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
        }, executor);

        executor.shutdown(); // Initiates an orderly shutdown in which previously submitted tasks are executed, but no new tasks will be accepted.
        return response;
    }
}
