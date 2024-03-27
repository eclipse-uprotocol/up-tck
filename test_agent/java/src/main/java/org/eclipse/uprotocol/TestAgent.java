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
import org.eclipse.uprotocol.uuid.factory.UuidFactory;
import org.eclipse.uprotocol.v1.*;
import org.json.JSONObject;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.List;
import java.util.concurrent.CompletionStage;
import java.util.logging.Level;
import java.util.logging.Logger;

public class TestAgent {
    private static final Socket clientSocket;
    private static final SocketUTransport transport;
    private static final Map<String, ActionHandler> actionHandlers = new HashMap<>();
    private static final Logger logger = Logger.getLogger("JavaTestAgent");
    private static final UListener listener = TestAgent::handleOnReceive;
    private static final UListener performanceListener = TestAgent::handlePerformanceOnReceive;
    private static final Gson gson = new Gson();

    static {
        actionHandlers.put(Constant.SEND_COMMAND, TestAgent::handleSendCommand);
        actionHandlers.put(Constant.REGISTER_LISTENER_COMMAND, TestAgent::handleRegisterListenerCommand);
        actionHandlers.put(Constant.UNREGISTER_LISTENER_COMMAND, TestAgent::handleUnregisterListenerCommand);
        actionHandlers.put(Constant.INVOKE_METHOD_COMMAND, TestAgent::handleInvokeMethodCommand);
        actionHandlers.put(Constant.SERIALIZE_URI, TestAgent::handleSerializeUriCommand);
        actionHandlers.put(Constant.DESERIALIZE_URI, TestAgent::handleDeserializeUriCommand);
        actionHandlers.put(Constant.PERFORMANCE_PUBLISHER, TestAgent::handlePerformancePublishCommand);
        actionHandlers.put(Constant.PERFORMANCE_SUBSCRIBER, TestAgent::handlePerformanceSubscribeCommand);
        actionHandlers.put(Constant.UNREGISTER_SUBSCRIBERS, TestAgent::handleUnregisterSubscribersCommand);
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

    private static UStatus handlePerformanceSubscribeCommand(Map<String, Object> jsonData) {
        Map<String, Object> data = (Map<String, Object>) jsonData.get("data");
        String topic_string = data.get("topics").toString();
        List<UStatus> statusMessages = new ArrayList<UStatus>();
        for (int i = 0; i < Integer.parseInt(topic_string); i++) {
            UUri uri = UUri.newBuilder().setAuthority(UAuthority.newBuilder().setName("vcu.someVin.veh.ultifi.gm.com"))
                    .setEntity(UEntity.newBuilder().setName("performance.test").setVersionMajor(1).setId(1234))
                    .setResource(UResource.newBuilder().setName("dummy_" + i)).build();
            statusMessages.add(transport.registerListener(uri, performanceListener));
        }
        boolean allOkay = statusMessages.stream().allMatch(msg -> msg.getCode() == UCode.OK);
        UStatus failMsg = statusMessages.stream().filter(msg -> msg.getCode() != UCode.OK).findFirst().orElse(null);
        return allOkay ? UStatus.newBuilder().setCode(UCode.OK).setMessage("OK").build()
                : failMsg;
    }

    private static UStatus handlePerformancePublishCommand(Map<String, Object> jsonData) {
        Map<String, Object> data = (Map<String, Object>) jsonData.get("data");
        String topic_string = data.get("topics").toString();
        String event_string = data.get("events").toString();
        Map<String, Object> publishTimestamp = new HashMap<>();
        for (int i = 0; i < Integer.parseInt(topic_string); i++) {
            UUri uri = UUri.newBuilder().setAuthority(UAuthority.newBuilder().setName("vcu.someVin.veh.ultifi.gm.com"))
                    .setEntity(UEntity.newBuilder().setName("performance.test").setVersionMajor(1).setId(1234))
                    .setResource(UResource.newBuilder().setName("dummy_" + i)).build();
            for (int j = 0; j < Integer.parseInt(event_string); j++) {
                UMessage uMessage = UMessage.newBuilder().setAttributes(UAttributes.newBuilder().setSource(uri).setType(UMessageType.UMESSAGE_TYPE_PUBLISH).setId(UuidFactory.Factories.UUIDV6.factory().create()).build()).build();
                transport.send(uMessage);
                publishTimestamp.put("id", Long.toString(uMessage.getAttributes().getId().getMsb()));
                publishTimestamp.put("published_timestamp", System.currentTimeMillis());
                sendToTestManager(publishTimestamp, Constant.PUB_ON_RECEIVE);
                try {
                    Thread.sleep(Integer.parseInt(data.get("interval").toString()));
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }
        try {
            Thread.sleep(Integer.parseInt(data.get("timeout").toString()) * 1000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        Map<String, Object> empty_map = new HashMap<>();
        sendToTestManager(empty_map, Constant.PUB_COMPLETE);
        return UStatus.newBuilder().setCode(UCode.OK).setMessage("OK").build();
    }

    private static Object handleUnregisterSubscribersCommand(Map<String, Object> jsonData) {
        Map<String, Object> data = (Map<String, Object>) jsonData.get("data");
        String topic_string = data.get("topics").toString();
        List<UStatus> statusMessages = new ArrayList<UStatus>();
        for (int i = 0; i < Integer.parseInt(topic_string); i++) {
            UUri uri = UUri.newBuilder().setAuthority(UAuthority.newBuilder().setName("vcu.someVin.veh.ultifi.gm.com"))
                    .setEntity(UEntity.newBuilder().setName("performance.test").setVersionMajor(1).setId(1234))
                    .setResource(UResource.newBuilder().setName("dummy_" + i)).build();
            statusMessages.add(transport.unregisterListener(uri, performanceListener));
        }
        boolean allOkay = statusMessages.stream().allMatch(msg -> msg.getCode() == UCode.OK);
        UStatus failMsg = statusMessages.stream().filter(msg -> msg.getCode() != UCode.OK).findFirst().orElse(null);
        return allOkay ? UStatus.newBuilder().setCode(UCode.OK).setMessage("OK").build()
                : failMsg;
        
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

    private static void handlePerformanceOnReceive(UMessage uMessage) {
        logger.info("Java performance on_receive called");
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
            Map<String, Object> data = new HashMap<>();
            data.put("id", Long.toString(uMessage.getAttributes().getId().getMsb()));
            data.put("received_timestamp", System.currentTimeMillis());
            sendToTestManager(data, Constant.SUB_ON_RECEIVE);
        }

    }

    public static void main(String[] args) throws IOException {
        // Listening thread to receive messages from Test Manager
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
