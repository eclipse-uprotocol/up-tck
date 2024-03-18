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

import org.eclipse.uprotocol.tck.up_client_socket_java.SocketUListener;
import org.json.JSONObject;

import java.io.IOException;
import java.net.Socket;
import java.util.logging.FileHandler;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.logging.SimpleFormatter;

public class Main {
    private static final Logger logger = Logger.getLogger(Main.class.getName());

    public static void main(String[] args) throws IOException {
        try {
            FileHandler fh = new FileHandler("tck_java.log");
            logger.addHandler(fh);
            SimpleFormatter formatter = new SimpleFormatter();
            fh.setFormatter(formatter);

            logger.setLevel(Level.FINE);
            TransportLayer transport = TransportLayer.getInstance();
            
            logger.info("Connected in UTransport");
            Socket clientSocket = new Socket("127.0.0.5", 12345);
            logger.info("Connected in TM");

            TestAgent agent = new TestAgent(clientSocket, transport, new SocketUListener(clientSocket));
            JSONObject obj = new JSONObject();
            obj.put("SDK_name", "java");
            agent.sendToTM(obj);
        } catch (SecurityException | IOException e) {
            e.printStackTrace();
        }
    }
}