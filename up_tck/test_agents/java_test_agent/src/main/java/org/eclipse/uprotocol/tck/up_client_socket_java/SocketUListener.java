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

import java.io.IOException;
import java.io.OutputStream;
import java.net.Socket;
import java.nio.charset.StandardCharsets;

import org.eclipse.uprotocol.cloudevent.serialize.Base64ProtobufSerializer;
import org.eclipse.uprotocol.tck.testagent.TransportLayer;
import org.eclipse.uprotocol.transport.UListener;
import org.eclipse.uprotocol.v1.UMessageType;
import org.eclipse.uprotocol.v1.UPayload;
import org.eclipse.uprotocol.v1.UUri;
import org.eclipse.uprotocol.v1.UAttributes;
import org.eclipse.uprotocol.v1.UMessage;
import org.eclipse.uprotocol.transport.builder.UAttributesBuilder;
import org.json.JSONObject;

public class SocketUListener implements UListener {
    private Socket testAgentConnection;

    public SocketUListener(Socket testAgentConnection) {
        this.testAgentConnection = testAgentConnection;
    }

    private String protoboufToBase64(UMessage msg) {
        return Base64ProtobufSerializer.deserialize(msg.toByteArray());
    }

    @Override
    public void onReceive(UMessage umsg) {
        System.out.println("Listener onReceived");
        System.out.println(umsg);

        JSONObject json = new JSONObject();
        json.put("action", "onReceive");
        json.put("message", protoboufToBase64(umsg));

        try {

            OutputStream clientOutputStream = testAgentConnection.getOutputStream();
            String jsonString = json.toString();
            byte[] messageBytes = jsonString.getBytes(StandardCharsets.UTF_8);
            clientOutputStream.write(messageBytes);
            clientOutputStream.flush();

        } catch (IOException e) {
            e.printStackTrace();
        }

        if (umsg.getAttributes().getType() == UMessageType.UMESSAGE_TYPE_REQUEST){
            UUri topic = umsg.getAttributes().getSource();
            UPayload payload = umsg.getPayload();
            UAttributes attributes = umsg.getAttributes();
            
            attributes = UAttributesBuilder.response(topic, topic, attributes.getPriority(), attributes.getId()).build();

            UMessage response_umsg = UMessage.newBuilder().setAttributes(attributes).setPayload(payload).build();

            TransportLayer transporter = TransportLayer.getInstance();
            transporter.send(response_umsg);
        }
    }
}