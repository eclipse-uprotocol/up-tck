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

import com.google.protobuf.ByteString;
import com.google.protobuf.Descriptors;
import com.google.protobuf.Message;
import com.google.protobuf.Descriptors.EnumValueDescriptor;
import com.google.protobuf.Descriptors.FieldDescriptor;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.logging.Logger;

import org.json.JSONArray;
import org.json.JSONObject;

import java.nio.charset.StandardCharsets;

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
                setFieldValue(protoObj, fieldDescriptor, value);
            }
        }
    }

    private static void setFieldValue(Message.Builder protoObj, Descriptors.FieldDescriptor fieldDescriptor,
                                      Object value) {

        if (value instanceof String && ((String) value).startsWith("BYTES:")) {
            String byteString = ((String) value).substring(6); // Remove 'BYTES:' prefix
            value = ByteString.copyFromUtf8(byteString);
        }

        try {
            switch (fieldDescriptor.getJavaType()) {
                case INT:
                    int integer = Caster.toInt(value);
                    if (fieldDescriptor.getType() == Descriptors.FieldDescriptor.Type.UINT32 && integer < 0) {
                        throw new IllegalArgumentException("Field type is an unsigned int");
                    }
                    protoObj.setField(fieldDescriptor, integer);
                    break;
                case LONG:
                    long longVal = Caster.toLong(value);
                    protoObj.setField(fieldDescriptor, longVal);     
                    break;
                case FLOAT:
                    float f = Caster.toFloat(value); 
                    protoObj.setField(fieldDescriptor, f);
                    break;
                case DOUBLE:
                    double d = Caster.toDouble(value);
                    protoObj.setField(fieldDescriptor, d);
                    break;
                case BOOLEAN:
                    protoObj.setField(fieldDescriptor, Boolean.parseBoolean(value.toString()));
                    break;
                case STRING:
                    // by default, the value's data type should be a string
                    protoObj.setField(fieldDescriptor, value);
                    break;
                case BYTE_STRING:
                    protoObj.setField(fieldDescriptor, value);
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
                    else {
                        throw new IllegalArgumentException("If given a protobuf key, should be expecting a map/json typed value");
                    }
                    break;
                default:
                    break;
            }
        }catch (NumberFormatException e) {
            throw new IllegalArgumentException("incorrect value type to field type");
        }
    }

    public static JSONObject convertMessageToJSON(Message message) {
    	JSONObject result = new JSONObject();
    	
    	List<FieldDescriptor> allFields = message.getDescriptorForType().getFields();
    	for (FieldDescriptor field : allFields) {
    		String fieldName = field.getName();
    		Object defaultOrSetValue = message.getField(field);
    		Object value = getattr(message, field, defaultOrSetValue);

    		if (value instanceof byte[]) {
    			value = new String((byte[]) value, StandardCharsets.UTF_8);
    		}

    		if (value instanceof Message) {
    			result.put(fieldName, convertMessageToJSON((Message) value));
    		}
    		else if (field.isRepeated()) {
    			JSONArray repeated = new JSONArray();
    			for(Object subMsg: (List<Object>) value) {
    				if (subMsg instanceof Message) {
    					repeated.put( convertMessageToJSON((Message) subMsg) );
    				}
                    // if a primitive type
    				else{
    					repeated.put(subMsg);
    				}
    			}
    			result.put(fieldName, repeated);

    		}
    		else if (field.isRequired() || field.isOptional()) {
    			result.put(fieldName, value);
    		}
    	}
    	
    	return result;
    }
    
    public static Map<String, Object> convertMessageToMap(Message message) {
    	Map<String, Object> result = new HashMap<>();
    	
    	List<FieldDescriptor> allFields = message.getDescriptorForType().getFields();
    	for (FieldDescriptor field : allFields) {
    		String fieldName = field.getName();
    		Object defaultOrSetValue = message.getField(field);
    		Object value = getattr(message, field, defaultOrSetValue);
    		if (value instanceof EnumValueDescriptor) {
    			value = ((EnumValueDescriptor) value).getNumber();
    		}
    		
    		if (value instanceof ByteString) {
    			value = ((ByteString) value).toStringUtf8();
    		}
			

    		if (value instanceof Message) {
    			result.put(fieldName, convertMessageToMap((Message) value));
    		}
    		else if (field.isRepeated()) {
    			List<Object> repeated = new ArrayList<>();
    			for(Object subMsg: (List<Object>) value) {
    				if (subMsg instanceof Message) {
    					repeated.add( convertMessageToMap((Message) subMsg) );
    				}
                    // if a primitive type
    				else{
    					repeated.add(subMsg);
    				}
    			}
    			result.put(fieldName, repeated);

    		}
    		else if (field.isRequired() || field.isOptional()) {
    			result.put(fieldName, value);
    		}
    	}
    	
    	return result;
    }
    
    public static Object getattr(Message message, FieldDescriptor field, Object defaultValue) {
    	try {
    		Map<FieldDescriptor, Object> fields2Values = message.getAllFields();
            Object value = fields2Values.get(field);
            
            if (value == null) {
            	return defaultValue;
            }
            else {
            	return value;
            }
            
    	}catch (Exception e) {
            return defaultValue;  // Return default value if field not found or cannot be accessed
        }
    }


}