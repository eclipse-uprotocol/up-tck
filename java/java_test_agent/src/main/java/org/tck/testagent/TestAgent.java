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

package org.tck.testagent;

import org.eclipse.uprotocol.cloudevent.serialize.Base64ProtobufSerializer;
import org.eclipse.uprotocol.transport.UListener;
import org.eclipse.uprotocol.v1.*;
import org.json.JSONObject;
import org.tck.up_client_socket_java.SocketUListener;
import org.tck.up_client_socket_java.SocketUTransport;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.logging.Logger;

public class TestAgent {
    private static final Logger logger = Logger.getLogger(TestAgent.class.getName());
    private SocketUTransport socketUTransport;
    private JSONObject jsonObject;
    private Socket clientSocket;

    public TestAgent(Socket socket, SocketUTransport utransport, SocketUListener listener) {
        try {
            // Socket Connection to Dispatcher
            this.socketUTransport = utransport;

            // Client Socket connection to Test Manager
            clientSocket = socket;

            // Listening thread to receive messages from Test Manager
            Thread receiveThread = new Thread(() -> receiveFromTM(listener));
            receiveThread.start();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private byte[] base64ToProtobufBytes(String base64) {
        return Base64ProtobufSerializer.serialize(base64);
    }

    private String protobufToBase64(UStatus status) {
        return Base64ProtobufSerializer.deserialize(status.toByteArray());
    }

    private void receiveFromTM(UListener listener) {
        int msgLen = 32767;
        try {
            InputStream clientInputStream = clientSocket.getInputStream();
            while (true) {
                byte[] recvData = new byte[msgLen];
                int bytesRead = clientInputStream.read(recvData);
                if (bytesRead > 0) {
                    String jsonStr = new String(recvData, 0, bytesRead, StandardCharsets.UTF_8);
                    logger.info("jsonMsg from TM: " + jsonStr);

                    jsonObject = new JSONObject(jsonStr);
                    String action = jsonObject.getString("action");
                    logger.info("action ->" + action);
                    String message = jsonObject.getString("message");
                    byte[] protobuf_bytes = base64ToProtobufBytes(message);
                    logger.info("message ->" + protobuf_bytes);
                    UMessage umsg = UMessage.parseFrom(protobuf_bytes);
                    logger.info("UMessage: "+umsg);
                    UAttributes attributes = umsg.getAttributes();
                    UStatus status = null;
                    switch (action) {
                        case "send":
                            status = socketUTransport.send(umsg);
                            break;
                        case "registerlistener":
                            status = socketUTransport.registerListener(attributes.getSource(), listener);
                            break;
                        case "unregisterlistener":
                            status = socketUTransport.unregisterListener(attributes.getSource(), listener);
                            break;
                    }
                    this.send(status);
                }
                else {
                	clientSocket.close();
                    logger.info("Closed Test Agent Socket Client");
                    return;
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public void send(UMessage umsg) {
        byte[] base64umsg = umsg.toByteArray();
        JSONObject jsonObject = new JSONObject();
        jsonObject.put("action", "send");
        jsonObject.put("message", Base64ProtobufSerializer.deserialize(base64umsg));
        sendToTM(jsonObject);

    }

    public void send(UStatus status) {
        JSONObject json = new JSONObject();
        json.put("action", "uStatus");
        json.put("message", protobufToBase64(status));
        sendToTM(json);
    }

    void sendToTM(JSONObject jsonObj) {
        try {
            OutputStream clientOutputStream = clientSocket.getOutputStream();
            String jsonString = jsonObj.toString();
            byte[] messageBytes = jsonString.getBytes(StandardCharsets.UTF_8);
            clientOutputStream.write(messageBytes);
            clientOutputStream.flush();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public void registerListener(UUri topic, UListener listener) {
        try {
            socketUTransport.registerListener(topic, listener);
            // Additional logic if needed
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public void unregisterListener(UUri topic, UListener listener) {
        try {
            socketUTransport.unregisterListener(topic, listener);
            // Additional logic to unregister listener based on clientPort
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}