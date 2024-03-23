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
import com.google.protobuf.ByteString;
import com.google.protobuf.Descriptors;
import com.google.protobuf.InvalidProtocolBufferException;
import com.google.protobuf.Message;
import com.google.protobuf.util.JsonFormat;

import java.util.HashMap;
import java.util.Map;

public class ProtoConverter {

    public static Message dictToProto(Map<String, Object> parentJsonObj, Message.Builder parentProtoObj) {
        populateFields(parentJsonObj, parentProtoObj);
        return parentProtoObj.build();
    }

    private static void populateFields(Map<String, Object> jsonObj, Message.Builder protoObj) {
        for (Map.Entry<String, Object> entry : jsonObj.entrySet()) {
            String key = entry.getKey();
            Object value = entry.getValue();
            Descriptors.FieldDescriptor fieldDescriptor = protoObj.getDescriptorForType().findFieldByName(key);

            if (fieldDescriptor != null) {
                if (value instanceof String && ((String) value).startsWith("BYTES:")) {
                    String byteString = ((String) value).substring(7); // Remove 'BYTES:' prefix
                    ByteString byteValue = ByteString.copyFromUtf8(byteString);
                    protoObj.setField(fieldDescriptor, byteValue);
                } else {
                    setFieldValue(protoObj, fieldDescriptor, value);
                }
            }
        }
    }

    private static void setFieldValue(Message.Builder protoObj, Descriptors.FieldDescriptor fieldDescriptor,
                                      Object value) {
        switch (fieldDescriptor.getJavaType()) {
            case INT:
                protoObj.setField(fieldDescriptor, Integer.parseInt(value.toString()));
                break;
            case LONG:
                try {
                    protoObj.setField(fieldDescriptor, Long.parseLong(value.toString()));
                } catch (NumberFormatException ex) {
                    protoObj.setField(fieldDescriptor, Long.parseUnsignedLong(value.toString()));
                }
                break;
            case FLOAT:
                protoObj.setField(fieldDescriptor, Float.parseFloat(value.toString()));
                break;
            case DOUBLE:
                protoObj.setField(fieldDescriptor, Double.parseDouble(value.toString()));
                break;
            case BOOLEAN:
                protoObj.setField(fieldDescriptor, Boolean.parseBoolean(value.toString()));
                break;
            case STRING:
                protoObj.setField(fieldDescriptor, value.toString());
                break;
            case ENUM:
                protoObj.setField(fieldDescriptor, fieldDescriptor.getEnumType().findValueByName(value.toString()));
                break;
            case MESSAGE:
                if (value instanceof Map) {
                    Message.Builder nestedBuilder = protoObj.newBuilderForField(fieldDescriptor);
                    populateFields((Map<String, Object>) value, nestedBuilder);
                    protoObj.setField(fieldDescriptor, nestedBuilder.build());
                }
                break;
            default:
                // Handle other types as needed
                break;
        }
    }

    public static Map<String, Object> convertMessageToMap(Message message) {
        Map<String, Object> map;
        JsonFormat.Printer printer = JsonFormat.printer().includingDefaultValueFields().preservingProtoFieldNames();
        Gson gson = new Gson();

        try {
            String jsonString = printer.print(message);
            map = gson.fromJson(jsonString, Map.class);
        } catch (InvalidProtocolBufferException ex) {
            map = new HashMap<>();
        }
        return map;
    }


}