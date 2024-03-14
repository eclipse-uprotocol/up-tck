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

package org.eclipse.uprotocol.tck.up_client_socket_java;
import org.eclipse.uprotocol.rpc.CallOptions;
import org.eclipse.uprotocol.transport.UListener;
import org.eclipse.uprotocol.v1.*;
import org.eclipse.uprotocol.uri.factory.UResourceBuilder;
import org.eclipse.uprotocol.transport.builder.UAttributesBuilder;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.Socket;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionStage;
import java.util.concurrent.ConcurrentHashMap;
import java.util.logging.Logger;

public class SocketUTransport implements IUTransport {
    private static final String DISPATCHER_IP = "127.0.0.1";
    private static final Integer DISPATCHER_PORT = 44444;

    private static final Logger logger = Logger.getLogger(SocketUTransport.class.getName());
    private final Socket socket;
    private final Map<UUri, ArrayList<UListener>> topicToListener = new ConcurrentHashMap<>();
    Map<UUID, CompletionStage<UMessage>> reqidToFuture = new HashMap<>();

    public SocketUTransport() throws IOException {
        socket = new Socket(DISPATCHER_IP, DISPATCHER_PORT);
        Thread thread = new Thread(() -> {
            try {
                listen();
            } catch (IOException e) {
                e.printStackTrace();
            }
        });
        thread.start();
    }

    public SocketUTransport(boolean listen) throws IOException {
        socket = new Socket(DISPATCHER_IP, DISPATCHER_PORT);

        // if want to receive messages, then spin new thread to receive messages
        if (listen){
            Thread thread = new Thread(() -> {
                try {
                    listen();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            });
            thread.start();
        }
    }

    private void listen() throws IOException {
        try {
            while (true) {
                InputStream inputStream = socket.getInputStream();
                byte[] buffer = new byte[32767];
                int readSize = inputStream.read(buffer);
                logger.info("Message length: " + readSize);

                UMessage umsg = UMessage.parseFrom(Arrays.copyOfRange(buffer, 0, readSize));
                logger.info("Received uMessage: " + umsg);
                
                // if registered to topic, then listeners should receive this incoming UMessage 
                UAttributes attributes = umsg.getAttributes();

                if (attributes.getType() == UMessageType.UMESSAGE_TYPE_PUBLISH){
                    this.handlePublishMessage(umsg);
                } else if (attributes.getType() == UMessageType.UMESSAGE_TYPE_REQUEST) {
                    this.handleRequestMessage(umsg);
                } else if (attributes.getType() == UMessageType.UMESSAGE_TYPE_RESPONSE) {
                    this.handleResponseMessage(umsg);
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

    private void handlePublishMessage(UMessage umsg) {
        // Publish messages' attribute.source is the recevied publish topic
        UUri topic = umsg.getAttributes().getSource();

        if (topicToListener.containsKey(topic)) {
            for (UListener listener : topicToListener.get(topic)) {
                Logger.getLogger(" Handle Topic");
                listener.onReceive(umsg);
            }
        } else {
            Logger.getLogger(" Topic not found in Listener Map, discarding...");
        }
    }

    private void handleResponseMessage(UMessage umsg) {
        UUID requestId = umsg.getAttributes().getReqid();
        if (this.reqidToFuture.containsKey(requestId)) {
            CompletionStage<UMessage> responseFuture = this.reqidToFuture.get(requestId);
            responseFuture.toCompletableFuture().complete(umsg);
            
            this.reqidToFuture.remove(requestId);
        }
    }

    private void handleRequestMessage(UMessage umsg) {
        // Request messages' attribute.sink is for subscribed/registered Destination UUri
        UUri topic = umsg.getAttributes().getSink();
        if (topicToListener.containsKey(topic)) {
            for (UListener listener : topicToListener.get(topic)) {
                Logger.getLogger(" Handle Topic");
                listener.onReceive(umsg);
            }
        } else {
            Logger.getLogger(" Topic not found in Listener Map, discarding...");
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
    	ArrayList<UListener> new_array_list = new ArrayList<UListener>();
    	if (topicToListener.containsKey(topic)) {
    		new_array_list = topicToListener.get(topic);
    	}
		new_array_list.add(listener);
		topicToListener.put(topic,  new_array_list);
        return UStatus.newBuilder()
                .setCode(UCode.OK)
                .setMessage("OK")
                .build();
    }

    @Override
    public UStatus unregisterListener(UUri topic, UListener listener) {
    	ArrayList<UListener> new_array_list = new ArrayList<UListener>();
    	if (topicToListener.containsKey(topic)) {
    		new_array_list = topicToListener.get(topic);
    		if (new_array_list.size() > 1) {
    			new_array_list.remove(listener);
    			topicToListener.put(topic, new_array_list);
    		} else {
    			topicToListener.remove(topic);
    		}
    	}
    	else {
    		return UStatus.newBuilder()
                    .setCode(UCode.NOT_FOUND)
                    .setMessage("UUri topic was not registered initially")
                    .build();
    	}
    	
        return UStatus.newBuilder()
                .setCode(UCode.OK)
                .setMessage("OK")
                .build();
    }

    @Override
    public CompletionStage<UMessage> invokeMethod(UUri methodUri, UPayload requestPayload, CallOptions options) {
        UEntity entity = UEntity.newBuilder().setName("nameJava").setVersionMajor(1).build();
        UResource resrc = UResourceBuilder.forRpcResponse();
        UUri source = UUri.newBuilder().setEntity(entity).setResource(resrc).build();

        //have to create own uAttribute UUID to 
        UAttributes attributes = UAttributesBuilder.request(source, methodUri, UPriority.UPRIORITY_CS4, options.timeout()).build();
        
        //Get UAttributes's request id
        UUID requestId = attributes.getId();

        UMessage request_umsg = UMessage.newBuilder().setAttributes(attributes).setPayload(requestPayload).build();

        //create Future so can store response UMessage in the future
        CompletionStage<UMessage> response = new CompletableFuture<>();
        this.reqidToFuture.put(requestId, response);
        this.send(request_umsg);
        return response;
    }
}