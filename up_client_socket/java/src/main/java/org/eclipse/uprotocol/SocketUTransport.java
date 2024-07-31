/**
 * SPDX-FileCopyrightText: 2024 Contributors to the Eclipse Foundation
 * <p>
 * See the NOTICE file(s) distributed with this work for additional
 * information regarding copyright ownership.
 * <p>
 * This program and the accompanying materials are made available under the
 * terms of the Apache License Version 2.0 which is available at
 * https://www.apache.org/licenses/LICENSE-2.0
 * <p>
 * SPDX-License-Identifier: Apache-2.0
 */

 package org.eclipse.uprotocol;

 import org.eclipse.uprotocol.transport.UListener;
 import org.eclipse.uprotocol.transport.UTransport;
 import org.eclipse.uprotocol.uri.validator.UriFilter;
 import org.eclipse.uprotocol.v1.UCode;
 import org.eclipse.uprotocol.v1.UMessage;
 import org.eclipse.uprotocol.v1.UStatus;
 import org.eclipse.uprotocol.v1.UUri;
 
 import java.io.IOException;
 import java.io.InputStream;
 import java.io.OutputStream;
 import java.net.Socket;
 import java.util.AbstractMap;
 import java.util.Arrays;
 import java.util.HashMap;
 import java.util.Map;
 import java.util.concurrent.CompletableFuture;
 import java.util.concurrent.CompletionStage;
 import java.util.concurrent.ExecutorService;
 import java.util.concurrent.Executors;
 import java.util.logging.Level;
 import java.util.logging.Logger;
 
 /**
  * {@code SocketUTransport} is an implementation of the {@link UTransport} interface that communicates
  * over a TCP socket. It listens for incoming messages from a dispatcher, processes them, and notifies
  * registered listeners based on URI filters. It also supports sending messages and managing listeners.
  * <p>
  * This implementation uses a fixed thread pool to handle incoming messages asynchronously and ensures
  * that socket resources are properly managed and released.
  * </p>
  */
 public class SocketUTransport implements UTransport {
     private static final Logger logger = Logger.getLogger("JavaSocketUTransport");
     private static final String DISPATCHER_IP = "127.0.0.1";
     private static final Integer DISPATCHER_PORT = 44444;
     private static final int BYTES_MSG_LENGTH = 32767;
     private static final String INTERNAL_ERROR = "INTERNAL ERROR : ";
     private final Socket socket;
     private final Object lock = new Object();
     private final UUri source;
     private Map<AbstractMap.SimpleEntry<UUri, UUri>, UListener> uriToListener = new HashMap<>();
 
     /**
      * Constructs a {@code SocketUTransport} instance and establishes a connection to the dispatcher.
      * Initializes the socket and starts listening for incoming messages asynchronously.
      *
      * @param newSource The source URI to be used by this transport.
      * @throws IOException If an I/O error occurs when creating the socket.
      */
     public SocketUTransport(UUri newSource) throws IOException {
         source = newSource;
         uriToListener = new HashMap<>();
         socket = new Socket(DISPATCHER_IP, DISPATCHER_PORT);
         ExecutorService executor = Executors.newFixedThreadPool(5);
         executor.submit(this::listen);
         executor.shutdown();
     }
 
 
     /**
      * Listens for incoming UMessages from the Dispatcher.
      * Processes the incoming data if the listener is registered with a UMessage source and sink UURI filter.
      */
     private void listen() {
         try {
             while (true) {
                 byte[] buffer = new byte[BYTES_MSG_LENGTH];
                 InputStream inputStream = socket.getInputStream();
                 int readSize = inputStream.read(buffer);
 
                 if (readSize < 0) {
                     if (!socket.isClosed()) {
                         socket.close();
                     }
                     return;
                 }
                 UMessage umsg = UMessage.parseFrom(Arrays.copyOfRange(buffer, 0, readSize));
                 String logMessage = " Received uMessage";
                 logger.info(logMessage);
                 notifyListeners(umsg);
             }
         } catch (IOException e) {
             try {
                 if (!socket.isClosed()) {
                     socket.close();
                 }
             } catch (IOException ioException) {
                 logger.log(Level.SEVERE, String.format("Error while closing socket: %s", ioException.getMessage()),
                         ioException);
             }
             logger.log(Level.SEVERE, String.format("Error while listening for messages: %s", e.getMessage()), e);
         }
     }
 
     /**
      * Notifies listeners registered for the source and sink URI filters about the incoming message.
      * The message is matched against the registered URI filters, and the appropriate listeners are
      * invoked asynchronously.
      *
      * @param umsg The message to be processed and dispatched to listeners.
      */
     public void notifyListeners(UMessage umsg) {
         synchronized (lock) {
             boolean isMatch = false;
             for (Map.Entry<AbstractMap.SimpleEntry<UUri, UUri>, UListener> entry : uriToListener.entrySet()) {
                 AbstractMap.SimpleEntry<UUri, UUri> key = entry.getKey();
                 UListener listener = entry.getValue();
                 UriFilter uriFilter = new UriFilter(key.getKey(), key.getValue());
                 boolean match = uriFilter.matches(umsg.getAttributes());
                 if (match && listener != null) {
                     logger.info("Handle Uri");
                     listener.onReceive(umsg);
                     isMatch = true;
                 }
             }
             if (!isMatch) {
                 logger.info("Uri not found in Listener Map, discarding...");
             }
         }
     }
 
     /**
      * Registers a listener for the specified source and sink URI filters.
      *
      * @param sourceFilter The URI filter for the source.
      * @param sinkFilter The URI filter for the sink.
      * @param listener The listener to be registered.
      */
     public void addListener(UUri sourceFilter, UUri sinkFilter, UListener listener) {
         logger.info("listeners: " + sourceFilter + ", " + sinkFilter + ", " + listener);
         AbstractMap.SimpleEntry<UUri, UUri> key = new AbstractMap.SimpleEntry<>(sourceFilter, sinkFilter);
         uriToListener.put(key, listener);
     }
 
     /**
      * Removes the listener registered for the specified source and sink URI filters.
      *
      * @param sourceFilter The URI filter for the source.
      * @param sinkFilter The URI filter for the sink.
      * @return A status indicating the outcome of the removal operation.
      */
     public UStatus removeListener(UUri sourceFilter, UUri sinkFilter) {
         AbstractMap.SimpleEntry<UUri, UUri> key = new AbstractMap.SimpleEntry<>(sourceFilter, sinkFilter);
         UListener listener = uriToListener.remove(key);
         if (listener != null) {
             return UStatus.newBuilder().setCode(UCode.OK).setMessage("Listener removed successfully").build();
 
         } else {
             return UStatus.newBuilder().setCode(UCode.NOT_FOUND).setMessage("Listener not found for the given URI")
                     .build();
         }
     }
 
     /**
      * Sends the provided message over the socket connection.
      *
      * @param message The message to be sent.
      * @return A status indicating the outcome of the send operation.
      */
     public CompletionStage<UStatus> send(UMessage message) {
         byte[] umsgSerialized = message.toByteArray();
         try {
             OutputStream outputStream = socket.getOutputStream();
             outputStream.write(umsgSerialized);
             logger.info("uMessage Sent to dispatcher fron java socket transport");
             return CompletableFuture.completedFuture(
                     UStatus.newBuilder().setCode(UCode.OK).setMessage("uMessage Sent to dispatcher").build());
         } catch (IOException e) {
             logger.log(Level.SEVERE, INTERNAL_ERROR, e);
             return CompletableFuture.completedFuture(
                     UStatus.newBuilder().setCode(UCode.INTERNAL).setMessage(INTERNAL_ERROR + e.getMessage()).build());
         }
     }
 
     /**
      * Registers the specified listener for the given source and sink URI filters.
      *
      * @param sourceFilter The URI filter for the source.
      * @param sinkFilter The URI filter for the sink.
      * @param listener The listener to be registered.
      * @return A status indicating the outcome of the register listener operation.
      */
     public CompletionStage<UStatus> registerListener(UUri sourceFilter, UUri sinkFilter, UListener listener) {
         addListener(sourceFilter, sinkFilter, listener);
         return CompletableFuture.completedFuture(UStatus.newBuilder().setCode(UCode.OK).setMessage("OK").build());
     }
 
 
     /**
      * Unregisters the specified listener from the given source and sink URI filters.
      *
      * @param sourceFilter The URI filter for the source.
      * @param sinkFilter The URI filter for the sink.
      * @param listener The listener to be removed.
      * @return A status indicating the outcome of the unregister listener operation.
      */
     public CompletionStage<UStatus> unregisterListener(UUri sourceFilter, UUri sinkFilter, UListener listener) {
         UStatus status = removeListener(sourceFilter, sinkFilter);
         return CompletableFuture.completedFuture(status);
     }
 
 
     /**
      * Closes the socket connection and releases any resources associated with it.
      */
     @Override
     public void close() {
         try {
             if (!socket.isClosed()) {
                 socket.close();
             }
         } catch (IOException e) {
             logger.log(Level.SEVERE, "INTERNAL ERROR: ", e);
         }
     }
 
     /**
      * Returns the source URI of this transport.
      *
      * @return The source URI.
      */
     public UUri getSource() {
         return source;
     }
 }