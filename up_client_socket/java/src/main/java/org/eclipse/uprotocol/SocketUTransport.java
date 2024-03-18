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

import org.eclipse.uprotocol.rpc.CallOptions;
import org.eclipse.uprotocol.rpc.RpcClient;
import org.eclipse.uprotocol.transport.UListener;
import org.eclipse.uprotocol.transport.UTransport;
import org.eclipse.uprotocol.transport.builder.UAttributesBuilder;
import org.eclipse.uprotocol.uri.factory.UResourceBuilder;
import org.eclipse.uprotocol.uri.validator.UriValidator;
import org.eclipse.uprotocol.v1.*;
import org.eclipse.uprotocol.validation.ValidationResult;

import java.io.BufferedInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.Socket;
import java.util.concurrent.*;
import java.util.logging.Level;
import java.util.logging.Logger;

public class SocketUTransport implements UTransport, RpcClient {
    private static final Logger logger = Logger.getLogger(SocketUTransport.class.getName());
    private static final String DISPATCHER_IP = "127.0.0.1";
    private static final Integer DISPATCHER_PORT = 44444;
    private static final int BYTES_MSG_LENGTH = 32767;
    private static final UUri RESPONSE_URI;

    static {
        RESPONSE_URI = UUri.newBuilder().setEntity(UEntity.newBuilder().setName("test_agent_java").setVersionMajor(1))
                .setResource(UResourceBuilder.forRpcResponse()).build();
    }

    private final Socket socket;
    private final ConcurrentHashMap<byte[], CompletionStage<UMessage>> reqid_to_future;
    private final ConcurrentHashMap<byte[], CopyOnWriteArrayList<UListener>> uri_to_listener;
    private final Object lock = new Object();


    public SocketUTransport() throws IOException {
        reqid_to_future = new ConcurrentHashMap<>();
        uri_to_listener = new ConcurrentHashMap<>();
        socket = new Socket(DISPATCHER_IP, DISPATCHER_PORT);

        ExecutorService executor = Executors.newFixedThreadPool(5);
        executor.submit(this::listen);
        executor.shutdown();
    }

    /**
     * Listens for incoming messages on the socket input stream from dispatcher.
     * Messages are processed based on their type: PUBLISH, REQUEST, or RESPONSE.
     * Handles each message accordingly by invoking corresponding handler methods.
     */
    private void listen() {
        try (InputStream inputStream = new BufferedInputStream(socket.getInputStream())) {
            while (true) {
                byte[] recvData = new byte[BYTES_MSG_LENGTH];
                int bytesRead = inputStream.read(recvData);
                if (bytesRead == -1) {
                    continue; // No need to process empty reads
                }

                UMessage umsg = UMessage.parseFrom(recvData);
                UAttributes attributes = umsg.getAttributes();
                String logMessage = getClass().getSimpleName() + " Received uMessage";

                switch (attributes.getType()) {
                    case UMESSAGE_TYPE_PUBLISH:
                        handlePublishMessage(umsg);
                        break;
                    case UMESSAGE_TYPE_REQUEST:
                        handleRequestMessage(umsg);
                        break;
                    case UMESSAGE_TYPE_RESPONSE:
                        handleResponseMessage(umsg);
                        break;
                    default:
                        logger.warning(logMessage + " with unknown message type.");
                }

                logger.info(logMessage);
            }
        } catch (IOException e) {
            logger.log(Level.SEVERE, "Error while listening for messages: " + e.getMessage(), e);
        } finally {
            try {
                if (socket != null && !socket.isClosed()) {
                    socket.close();
                }
            } catch (IOException ioException) {
                logger.log(Level.SEVERE, "Error while closing socket: " + ioException.getMessage(), ioException);
            }
        }
    }

    /**
     * Handles a publish message by notifying listeners registered for the source URI.
     *
     * @param umsg The publish message to handle.
     */
    private void handlePublishMessage(UMessage umsg) {
        byte[] uri = umsg.getAttributes().getSource().toByteArray();
        notifyListeners(uri, umsg);
    }

    /**
     * Handles a request message by notifying listeners registered for the target URI.
     *
     * @param umsg The request message to handle.
     */
    private void handleRequestMessage(UMessage umsg) {
        byte[] uri = umsg.getAttributes().getSink().toByteArray();
        notifyListeners(uri, umsg);
    }

    /**
     * Notifies all listeners registered for the given URI with the provided message.
     *
     * @param uri  The URI for which listeners are to be notified.
     * @param umsg The message to be delivered to the listeners.
     */
    private void notifyListeners(byte[] uri, UMessage umsg) {

        synchronized (lock) {
            CopyOnWriteArrayList<UListener> listeners = uri_to_listener.get(uri);
            if (listeners != null) {
                logger.info(getClass().getSimpleName() + " Handle Uri");
                listeners.forEach(listener -> listener.onReceive(umsg));
            } else {
                logger.info(getClass().getSimpleName() + " Uri not found in Listener Map, discarding...");
            }
        }
    }

    /**
     * Handles the response message received from the server.
     * Completes the CompletableFuture associated with the request ID
     * if it exists in the map of pending request futures.
     *
     * @param umsg The response message to handle.
     */
    private void handleResponseMessage(UMessage umsg) {
        byte[] requestId = umsg.getAttributes().getReqid().toByteArray();
        CompletionStage<UMessage> responseFuture = reqid_to_future.remove(requestId);
        if (responseFuture.toCompletableFuture() != null) {
            responseFuture.toCompletableFuture().complete(umsg);
        }
    }

    /**
     * Sends the provided message over the socket connection.
     *
     * @param message The message to be sent.
     * @return A status indicating the outcome of the send operation.
     */
    public UStatus send(UMessage message) {
        byte[] umsgSerialized = message.toByteArray();
        try {
            OutputStream outputStream = socket.getOutputStream();
            outputStream.write(umsgSerialized);
            logger.info(getClass().getSimpleName() + " uMessage Sent");
            return UStatus.newBuilder().setCode(UCode.OK).setMessage("OK").build();
        } catch (IOException e) {
            logger.log(Level.SEVERE, "INTERNAL ERROR: ", e);
            return UStatus.newBuilder().setCode(UCode.INTERNAL).setMessage("INTERNAL ERROR: " + e.getMessage()).build();
        }
    }

    /**
     * Registers the specified listener for the given topic URI.
     *
     * @param topic    The URI of the topic to register the listener for.
     * @param listener The listener to be registered.
     * @return A status indicating the outcome of the registration operation.
     */
    public UStatus registerListener(UUri topic, UListener listener) {
        ValidationResult result = UriValidator.validate(topic);
        if (result.isFailure()) {
            return result.toStatus();
        }
        byte[] uri = topic.toByteArray();
        uri_to_listener.computeIfAbsent(uri, k -> new CopyOnWriteArrayList<>()).add(listener);
        return UStatus.newBuilder().setCode(UCode.OK).setMessage("OK").build();
    }

    /**
     * Unregisters the specified listener from the given topic URI.
     *
     * @param topic    The URI of the topic to unregister the listener from.
     * @param listener The listener to be removed.
     * @return A status indicating the outcome of the unregistration operation.
     */
    public UStatus unregisterListener(UUri topic, UListener listener) {
        ValidationResult result = UriValidator.validate(topic);
        if (result.isFailure()) {
            return result.toStatus();
        }
        byte[] uri = topic.toByteArray();

        CopyOnWriteArrayList<UListener> listeners = uri_to_listener.get(uri);
        if (listeners != null && listeners.remove(listener)) {
            if (listeners.isEmpty()) {
                uri_to_listener.remove(uri);
            }
            return UStatus.newBuilder().setCode(UCode.OK).setMessage("OK").build();
        }
        return UStatus.newBuilder().setCode(UCode.NOT_FOUND).setMessage("Listener not found for the given UUri")
                .build();
    }

    /**
     * Invokes a remote method with provided parameters and returns a CompletableFuture for the response.
     *
     * @param methodUri      The URI identifying the remote method to be invoked.
     * @param requestPayload The payload of the request message.
     * @param options        The call options specifying timeout.
     * @return A CompletableFuture that will hold the response message for the request.
     */
    public CompletionStage<UMessage> invokeMethod(UUri methodUri, UPayload requestPayload, CallOptions options) {
        UAttributes attributes = UAttributesBuilder.request(RESPONSE_URI, methodUri, UPriority.UPRIORITY_CS4,
                options.timeout()).build();
        byte[] requestId = attributes.getId().toByteArray();
        CompletableFuture<UMessage> responseFuture = new CompletableFuture<>();
        reqid_to_future.put(requestId, responseFuture);

        Thread timeoutThread = new Thread(() -> timeoutCounter(responseFuture, requestId, options.timeout()));
        timeoutThread.start();

        UMessage umsg = UMessage.newBuilder().setPayload(requestPayload).setAttributes(attributes).build();
        send(umsg);
        return responseFuture;
    }

    /**
     * Waits for the specified timeout and completes the CompletableFuture exceptionally if no response is received.
     *
     * @param responseFuture The CompletableFuture to complete exceptionally.
     * @param requestId      The request ID associated with the response.
     * @param timeout        The timeout duration.
     */
    private void timeoutCounter(CompletableFuture<UMessage> responseFuture, byte[] requestId, int timeout) {
        try {
            Thread.sleep(timeout);
            if (!responseFuture.isDone()) {
                responseFuture.completeExceptionally(new TimeoutException(
                        "Not received response for request " + new String(requestId) + " within " + timeout + " ms"));
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
