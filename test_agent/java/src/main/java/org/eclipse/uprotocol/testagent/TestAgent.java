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

package org.eclipse.uprotocol.tck.testagent;
import com.google.protobuf.InvalidProtocolBufferException;
import org.eclipse.uprotocol.cloudevent.serialize.Base64ProtobufSerializer;
import org.eclipse.uprotocol.rpc.CallOptions;
import org.eclipse.uprotocol.transport.UListener;
import org.eclipse.uprotocol.v1.*;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.eclipse.uprotocol.tck.up_client_socket_java.SocketUListener;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionStage;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.logging.Logger;
import java.util.*;

public class TestAgent {
    private static final String SEND_COMMAND = "send";
    private static final String REGISTER_LISTENER_COMMAND = "registerlistener";
    private static final String UNREGISTER_LISTENER_COMMAND = "unregisterlistener";
    private static final String INVOKE_METHOD_COMMAND = "invokemethod";
    private static final Set<String> COMMANDS = new HashSet<>(Arrays.asList(new String[] {SEND_COMMAND, REGISTER_LISTENER_COMMAND, UNREGISTER_LISTENER_COMMAND, INVOKE_METHOD_COMMAND}));

    private static final Logger logger = Logger.getLogger(TestAgent.class.getName());
    private TransportLayer socketUTransport;
    private JSONObject jsonObject;
    private Socket clientSocket;
    OutputStream clientOutputStream;

    public TestAgent(Socket socket, TransportLayer utransport, SocketUListener listener) {
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
                    logger.info("jsonString from TM: " + jsonStr);
                    if (isValidJSON(jsonStr)) {
                        handle_json_message(jsonStr, listener);
                    }
                } else {
                    clientSocket.close();
                    logger.info("Closing TA Client Socket");
                    return;
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    public void handle_json_message(String jsonStr, UListener listener) throws InvalidProtocolBufferException, InterruptedException, ExecutionException, TimeoutException {
        jsonObject = new JSONObject(jsonStr);
        String action = jsonObject.getString("action");
        logger.info("action ->" + action);
        if (COMMANDS.contains(action)) {
            this.handleCommandJson(jsonObject, listener);
        } 
    }
    public void handleCommandJson(JSONObject jsonObj, UListener listener) throws InvalidProtocolBufferException, InterruptedException, ExecutionException, TimeoutException {
        String action = jsonObj.getString("action");
        String message = jsonObj.getString("message");
        byte[] protobuf_bytes = base64ToProtobufBytes(message);
        logger.info("message ->" + protobuf_bytes);
        UMessage umsg = UMessage.parseFrom(protobuf_bytes);
        logger.info("UMessage: " + umsg);

        UPayload payload = umsg.getPayload();
        UAttributes attributes = umsg.getAttributes();

        CompletableFuture<UMessage> futureMsg = new CompletableFuture<>();
        UStatus status = null;
        switch (action) {
            case SEND_COMMAND:
                status = socketUTransport.send(umsg);
                break;
            case REGISTER_LISTENER_COMMAND:
                status = socketUTransport.registerListener(attributes.getSource(), listener);
                break;
            case UNREGISTER_LISTENER_COMMAND:
                status = socketUTransport.unregisterListener(attributes.getSource(), listener);
                break;
            case INVOKE_METHOD_COMMAND:
                CompletionStage<UMessage> futureMsgStage = socketUTransport.invokeMethod(attributes.getSource(), payload, CallOptions.newBuilder().withTimeout(0).build());
                futureMsg = futureMsgStage.toCompletableFuture();
                System.out.println("Future message -> " + futureMsg);
                status = UStatus.newBuilder()
                        .setCode(UCode.OK)
                        .setMessage("OK")
                        .build();
                break;
        }
        this.send(status);

        if (action == INVOKE_METHOD_COMMAND){
            logger.info("waiting for future umsg");

            if (attributes.getTtl() == 0){
                // Can wait forever
                umsg = futureMsg.get();
            }
            else{
                umsg = futureMsg.get(attributes.getTtl(), TimeUnit.MILLISECONDS);
            }

            logger.info("----invoke_method registered----");
            socketUTransport.registerListener(attributes.getSource(), listener);
        }
    }

    public void send(UStatus status) {
        JSONObject json = new JSONObject();
        json.put("action", "uStatus");
        json.put("message", protobufToBase64(status));
        sendToTM(json);
    }

    void sendToTM(JSONObject jsonObj) {
        try {
            clientOutputStream = clientSocket.getOutputStream();
            String jsonString = jsonObj.toString();
            byte[] messageBytes = jsonString.getBytes(StandardCharsets.UTF_8);
            clientOutputStream.write(messageBytes);
            clientOutputStream.flush();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private boolean isValidJSON(String jsonStr) throws Exception {
        try {
            new JSONObject(jsonStr);
        } catch (JSONException ex) {
            try {
                logger.info("exception: " + ex);
                new JSONArray(jsonStr);
            } catch (JSONException ex1) {
                logger.info("exception: " + ex1);
                throw new Exception("Invalid JSON.");
            }
        }
        return true;
    }

}