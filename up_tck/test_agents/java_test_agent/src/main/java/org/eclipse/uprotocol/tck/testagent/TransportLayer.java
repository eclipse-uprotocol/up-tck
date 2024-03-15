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
import java.io.IOException;
import java.util.concurrent.CompletionStage;
import java.util.logging.Logger;

import org.eclipse.uprotocol.v1.UMessage;
import org.eclipse.uprotocol.v1.UPayload;
import org.eclipse.uprotocol.v1.UStatus;
import org.eclipse.uprotocol.v1.UUri;
import org.eclipse.uprotocol.rpc.CallOptions;
import org.eclipse.uprotocol.tck.up_client_socket_java.IUTransport;
import org.eclipse.uprotocol.tck.up_client_socket_java.SocketUTransport;
import org.eclipse.uprotocol.transport.UListener;


public class TransportLayer {
    
    private static class SingletonCreator {
        private static final TransportLayer INSTANCE = new TransportLayer();
    }
    public static TransportLayer getInstance(){
        return SingletonCreator.INSTANCE;
    }

    private String utransport_type = "";
    private IUTransport utransport;
    

    private TransportLayer(){
        //default uTransport (SocketUTransport)
        this.utransport_type = "SOCKET";

        try {
            updateInstance();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void updateInstance() throws IOException{
        if (this.utransport_type == "SOCKET"){
            this.utransport = new SocketUTransport();
        }
    }

    public void setTransport(String transport_type) throws IOException{
        if (this.utransport_type != transport_type){
            Logger.getLogger(String.format("Set transport: previously was %s, now is %s", this.utransport_type, transport_type));
            this.utransport_type = transport_type;
            updateInstance();
        }
    }

    public String getTransport(){
        return this.utransport_type;
    }

    public UStatus send(UMessage umsg){
        return this.utransport.send(umsg);
    }

    public UStatus registerListener(UUri topic, UListener listener){
        return this.utransport.registerListener(topic, listener);
    }

    public UStatus unregisterListener(UUri topic, UListener listener){
        return this.utransport.unregisterListener(topic, listener);
    }

    public CompletionStage<UMessage> invokeMethod(UUri topic, UPayload payload, CallOptions options){
        return this.utransport.invokeMethod(topic, payload, options);
    }
}
