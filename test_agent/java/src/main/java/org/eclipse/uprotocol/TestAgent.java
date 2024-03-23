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

package org.eclipse.uprotocol;

import com.google.gson.Gson;
import com.google.protobuf.Any;
import com.google.protobuf.Message;
import com.google.protobuf.StringValue;
import org.eclipse.uprotocol.rpc.CallOptions;
import org.eclipse.uprotocol.transport.UListener;
import org.eclipse.uprotocol.transport.builder.UAttributesBuilder;
import org.eclipse.uprotocol.uri.serializer.LongUriSerializer;
import org.eclipse.uprotocol.uuid.serializer.LongUuidSerializer;
import org.eclipse.uprotocol.v1.*;
import org.json.JSONObject;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.CompletionStage;
import java.util.logging.Level;
import java.util.logging.Logger;

public class TestAgent {
    private static final Socket clientSocket;
    private static final SocketUTransport transport;
    private static final Map<String, ActionHandler> actionHandlers = new HashMap<>();
    private static final Logger logger = Logger.getLogger("JavaTestAgent");
    private static final UListener listener = TestAgent::handleOnReceive;
    private static final Gson gson = new Gson();

    static {
        actionHandlers.put(Constant.SEND_COMMAND, TestAgent::handleSendCommand);
        actionHandlers.put(Constant.REGISTER_LISTENER_COMMAND, TestAgent::handleRegisterListenerCommand);
        actionHandlers.put(Constant.UNREGISTER_LISTENER_COMMAND, TestAgent::handleUnregisterListenerCommand);
        actionHandlers.put(Constant.INVOKE_METHOD_COMMAND, TestAgent::handleInvokeMethodCommand);
        actionHandlers.put(Constant.SERIALIZE_URI, TestAgent::handleSerializeUriCommand);
        actionHandlers.put(Constant.DESERIALIZE_URI, TestAgent::handleDeserializeUriCommand);
        actionHandlers.put(Constant.SERIALIZE_UUID, TestAgent::handleSerializeUuidCommand);
        actionHandlers.put(Constant.DESERIALIZE_UUID, TestAgent::handleDeserializeUuidCommand);

    }

    static {
        try {

            transport = new SocketUTransport();
            clientSocket = new Socket(Constant.TEST_MANAGER_IP, Constant.TEST_MANAGER_PORT);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    public static void processMessage(Map<String, Object> jsonData) throws IOException {
        String action = (String) jsonData.get("action");
        if (actionHandlers.containsKey(action)) {
            UStatus status = (UStatus) actionHandlers.get(action).handle(jsonData);
            if (status != null) {
                sendToTestManager(status, action);
            }
        }
    }

    private static void sendToTestManager(Message proto, String action) {
        // Create a new dictionary
        JSONObject responseDict = new JSONObject();
        responseDict.put("data", ProtoConverter.convertMessageToMap(proto));
        writeDataToTMSocket(responseDict, action);
    }

    private static void writeDataToTMSocket(JSONObject responseDict, String action) {
        responseDict.put("action", action);
        responseDict.put("ue", "java");


        try {
            OutputStream outputStream = clientSocket.getOutputStream();
            outputStream.write(responseDict.toString().getBytes(StandardCharsets.UTF_8));
            outputStream.flush();
            logger.info("Sent to TM: " + responseDict);

        } catch (IOException ioException) {
            logger.log(Level.SEVERE, "Error sending data to TM:  " + ioException.getMessage(), ioException);

        }
    }

    private static void sendToTestManager(Object json, String action) {
        // Create a new dictionary
        JSONObject responseDict = new JSONObject();
        responseDict.put("data", json);
        writeDataToTMSocket(responseDict, action);

    }

    private static UStatus handleSendCommand(Map<String, Object> jsonData) {
        UMessage uMessage = (UMessage) ProtoConverter.dictToProto((Map<String, Object>) jsonData.get("data"),
                UMessage.newBuilder());
        return transport.send(uMessage);
    }

    private static UStatus handleRegisterListenerCommand(Map<String, Object> jsonData) {
        UUri uri = (UUri) ProtoConverter.dictToProto((Map<String, Object>) jsonData.get("data"), UUri.newBuilder());
        return transport.registerListener(uri, listener);
    }

    private static UStatus handleUnregisterListenerCommand(Map<String, Object> jsonData) {
        UUri uri = (UUri) ProtoConverter.dictToProto((Map<String, Object>) jsonData.get("data"), UUri.newBuilder());
        return transport.unregisterListener(uri, listener);
    }

    private static Object handleInvokeMethodCommand(Map<String, Object> jsonData) {
        Map<String, Object> data = (Map<String, Object>) jsonData.get("data");
        // Convert data and payload to protocol buffers
        UUri uri = (UUri) ProtoConverter.dictToProto(data, UUri.newBuilder());
        UPayload payload = (UPayload) ProtoConverter.dictToProto((Map<String, Object>) data.get("payload"),
                UPayload.newBuilder());
        CompletionStage<UMessage> responseFuture = transport.invokeMethod(uri, payload,
                CallOptions.newBuilder().build());
        responseFuture.whenComplete(
                (responseMessage, exception) -> sendToTestManager(responseMessage, Constant.RESPONSE_RPC));
        return null;
    }

    private static Object handleSerializeUriCommand(Map<String, Object> jsonData) {
        Map<String, Object> data = (Map<String, Object>) jsonData.get("data");
        UUri uri = (UUri) ProtoConverter.dictToProto(data, UUri.newBuilder());
        sendToTestManager(LongUriSerializer.instance().serialize(uri), Constant.SERIALIZE_URI);
        return null;
    }

    private static Object handleDeserializeUriCommand(Map<String, Object> jsonData) {
        sendToTestManager(LongUriSerializer.instance().deserialize(jsonData.get("data").toString()),
                Constant.DESERIALIZE_URI);
        return null;
    }

    private static Object handleSerializeUuidCommand(Map<String, Object> jsonData) {
        Map<String, Object> data = (Map<String, Object>) jsonData.get("data");
        UUID uuid = (UUID) ProtoConverter.dictToProto(data, UUID.newBuilder());
        sendToTestManager(LongUuidSerializer.instance().serialize(uuid), Constant.SERIALIZE_UUID);
        return null;
    }

    private static Object handleDeserializeUuidCommand(Map<String, Object> jsonData) {
        sendToTestManager(LongUuidSerializer.instance().deserialize(jsonData.get("data").toString()),
                Constant.DESERIALIZE_UUID);
        return null;
    }

    private static void handleOnReceive(UMessage uMessage) {
        logger.info("Java on_receive called");
        if (uMessage.getAttributes().getType().equals(UMessageType.UMESSAGE_TYPE_REQUEST)) {
            UAttributes reqAttributes = uMessage.getAttributes();
            UAttributes uAttributes = UAttributesBuilder.response(reqAttributes.getSink(), reqAttributes.getSource(),
                    UPriority.UPRIORITY_CS4, reqAttributes.getId()).build();
            StringValue stringValue = StringValue.newBuilder().setValue("SuccessRPCResponse").build();
            Any anyObj = Any.pack(stringValue);

            UPayload uPayload = UPayload.newBuilder().setValue(anyObj.toByteString())
                    .setFormat(UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF_WRAPPED_IN_ANY).build();

            UMessage resMsg = UMessage.newBuilder().setAttributes(uAttributes).setPayload(uPayload).build();
            transport.send(resMsg);
        } else {
            sendToTestManager(uMessage, Constant.RESPONSE_ON_RECEIVE);
        }

    }

    public static void main(String[] args) throws IOException {
        Thread receiveThread = new Thread(TestAgent::receiveFromTM);
        receiveThread.start();
        JSONObject obj = new JSONObject();
        obj.put("SDK_name", "java");
        sendToTestManager(obj, "initialize");
    }

    public static void receiveFromTM() {
        try {
            while (true) {
                byte[] buffer = new byte[Constant.BYTES_MSG_LENGTH];
                InputStream inputStream = clientSocket.getInputStream();
                int readSize = inputStream.read(buffer);
                if (readSize < 1) {
                    return;
                }
                logger.info("Received data from test manager: " + readSize);

                String jsonData = new String(buffer, 0, readSize);
                logger.info("Received data from test manager: " + jsonData);

                // Parse the JSON string using Gson
                Map<String, Object> jsonMap = gson.fromJson(jsonData, Map.class);
                processMessage(jsonMap);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    @FunctionalInterface
    private interface ActionHandler {
        Object handle(Map<String, Object> jsonData);
    }


}
