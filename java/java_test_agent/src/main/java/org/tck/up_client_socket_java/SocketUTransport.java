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

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.Socket;
import java.util.Arrays;
import java.util.Map;
import java.util.concurrent.CompletionStage;
import java.util.concurrent.ConcurrentHashMap;
import java.util.logging.Logger;

import org.eclipse.uprotocol.rpc.CallOptions;
import org.eclipse.uprotocol.rpc.RpcClient;
import org.eclipse.uprotocol.transport.UListener;
import org.eclipse.uprotocol.transport.UTransport;
import org.eclipse.uprotocol.v1.*;
import org.tck.testagent.TestAgent;

public class SocketUTransport implements UTransport, RpcClient {
    private static final Logger logger = Logger.getLogger(SocketUTransport.class.getName());
    private final Socket socket;
    SocketRPCClient socketRPCClient;
    private final Map<UUri, UListener> topicToListener = new ConcurrentHashMap<>();

    public SocketUTransport(String hostIp, int port) throws IOException {
        socket = new Socket(hostIp, port);
        Thread thread = new Thread(this::listen);
        thread.start();
    }

    private void listen() {
        try {
            while (true) {
                InputStream inputStream = socket.getInputStream();
                byte[] buffer = new byte[32767];
                int readSize = inputStream.read(buffer);
                logger.info("Message length: "+readSize);

                UMessage umsg = UMessage.parseFrom(Arrays.copyOfRange(buffer, 0, readSize) );
                logger.info("Received uMessage: " + umsg);

                UUri topic = umsg.getAttributes().getSource();
                if (topicToListener.containsKey(topic)) {
                    topicToListener.get(topic).onReceive(umsg);
                } else {
                    logger.info("Topic not found in Listener Map, discarding...");
                }
            }
        } catch (IOException e) {
            try {
                socket.close();
            } catch (IOException ioException) {
                ioException.printStackTrace();
            }
        }
    }

    @Override
    public UStatus send(UMessage umsg) {

        byte[] umsgSerialized = umsg.toByteArray();

        try {
            OutputStream outputStream = socket.getOutputStream();
            outputStream.write(umsgSerialized);
            outputStream.flush();
            logger.info("uMessage Sent");
        } catch (IOException e) {
            return UStatus.newBuilder()
                    .setCode(UCode.INTERNAL)
                    .setMessage("INTERNAL ERROR: IOException sending UMessage")
                    .build();
        }

        return UStatus.newBuilder()
                .setCode(UCode.OK)
                .setMessage("OK")
                .build();
    }

    @Override
    public UStatus registerListener(UUri topic, UListener listener) {
        topicToListener.put(topic, listener);
        return UStatus.newBuilder()
                .setCode(UCode.OK)
                .setMessage("OK")
                .build();
    }

    @Override
    public UStatus unregisterListener(UUri topic, UListener listener) {
        topicToListener.remove(topic);
        return UStatus.newBuilder()
                .setCode(UCode.OK)
                .setMessage("OK")
                .build();
    }


    @Override
    public CompletionStage<UMessage> invokeMethod(UUri methodURI, UPayload payload, CallOptions callOptions) {
        CompletionStage<UMessage> response = socketRPCClient.invokeMethod(methodURI, payload, callOptions);
        return response;
    }
}
