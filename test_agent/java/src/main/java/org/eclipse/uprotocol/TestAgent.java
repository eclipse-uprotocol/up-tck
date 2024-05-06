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
import org.eclipse.uprotocol.transport.UListener;
import org.eclipse.uprotocol.transport.builder.UAttributesBuilder;
import org.eclipse.uprotocol.transport.validate.UAttributesValidator;
import org.eclipse.uprotocol.uri.serializer.LongUriSerializer;
import org.eclipse.uprotocol.uri.validator.UriValidator;
import org.eclipse.uprotocol.validation.ValidationResult;
import org.eclipse.uprotocol.uuid.serializer.LongUuidSerializer;
import org.eclipse.uprotocol.uri.serializer.MicroUriSerializer;
import org.eclipse.uprotocol.uuid.factory.UuidFactory;
import org.eclipse.uprotocol.uuid.factory.UuidUtils;
import org.eclipse.uprotocol.uuid.validate.UuidValidator;
import org.eclipse.uprotocol.v1.*;
import org.json.JSONObject;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.UnsupportedEncodingException;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.CompletionStage;
import java.util.function.Function;
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
        actionHandlers.put(Constant.SERIALIZE_URI, TestAgent::handleLongSerializeUriCommand);
        actionHandlers.put(Constant.DESERIALIZE_URI, TestAgent::handleLongDeserializeUriCommand);
        actionHandlers.put(Constant.VALIDATE_URI, TestAgent::handleValidateUriCommand);
        actionHandlers.put(Constant.VALIDATE_UUID, TestAgent::handleValidateUuidCommand);
        actionHandlers.put(Constant.SERIALIZE_UUID, TestAgent::handleLongSerializeUuidCommand);
        actionHandlers.put(Constant.DESERIALIZE_UUID, TestAgent::handleLongDeserializeUuidCommand);
        actionHandlers.put(Constant.VALIDATE_UATTRIBUTES, TestAgent::handleUAttributesValidateCommand);
        actionHandlers.put(Constant.MICRO_SERIALIZE_URI, TestAgent::handleMicroSerializeUuriCommand);
        actionHandlers.put(Constant.MICRO_DESERIALIZE_URI, TestAgent::handleMicroDeserializeUuriCommand);
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
                String testID = (String) jsonData.get("test_id");
                sendToTestManager(status, action, testID);
            }
        }
    }

    private static void sendToTestManager(Object json, String action) {
        sendToTestManager(json, action, null);
    }
    
    private static void sendToTestManager(Message proto, String action) {
        sendToTestManager(proto, action, null);
    }
    
    private static void sendToTestManager(Object json, String action, String received_test_id) {
        JSONObject responseDict = new JSONObject();
        responseDict.put("data", json);
        if (received_test_id != null) {
            responseDict.put("test_id", received_test_id);
        }
        writeDataToTMSocket(responseDict, action);
    }
    
    private static void sendToTestManager(Message proto, String action, String received_test_id) {
        JSONObject responseDict = new JSONObject();
        responseDict.put("data", ProtoConverter.convertMessageToMap(proto));
        if (received_test_id != null) {
            responseDict.put("test_id", received_test_id);
        }
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

    private static UStatus handleSendCommand(Map<String, Object> jsonData) {
        UMessage uMessage = (UMessage) ProtoConverter.dictToProto((Map<String, Object>) jsonData.get("data"),
                UMessage.newBuilder());
        UAttributes uAttributesWithId = uMessage.getAttributes().toBuilder().setId(UuidFactory.Factories.UPROTOCOL.factory().create()).build();
        UMessage uMessageWithId = uMessage.toBuilder().setAttributes(uAttributesWithId).build();
        return transport.send(uMessageWithId);
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
                CallOptions.newBuilder().setTtl(10000).build());
        responseFuture.whenComplete((responseMessage, exception) -> {
            sendToTestManager(responseMessage, Constant.INVOKE_METHOD_COMMAND, (String) jsonData.get("test_id"));
        });
        return null;
    }

    private static Object handleLongSerializeUriCommand(Map<String, Object> jsonData) {
        Map<String, Object> data = (Map<String, Object>) jsonData.get("data");
        UUri uri = (UUri) ProtoConverter.dictToProto(data, UUri.newBuilder());
        String serializedUuri = LongUriSerializer.instance().serialize(uri);
        String testID = (String) jsonData.get("test_id");
        sendToTestManager(serializedUuri, Constant.SERIALIZE_URI, testID);
        return null;
    }

    private static Object handleLongDeserializeUriCommand(Map<String, Object> jsonData) {
    	UUri uri = LongUriSerializer.instance().deserialize(jsonData.get("data").toString());
        String testID = (String) jsonData.get("test_id");
        sendToTestManager(uri, Constant.DESERIALIZE_URI, testID);
        return null;
    }

    private static Object handleValidateUriCommand(Map<String, Object> jsonData) {
        Map<String, Object> data = (Map<String, Object>) jsonData.get("data");
        String valType = (String) data.get("type");
        String uriValue = (String) data.get("uri");

        UUri uri = LongUriSerializer.instance().deserialize(uriValue);

        Function<UUri, ValidationResult> validatorFunc = null;
        Function<UUri, Boolean> validatorFuncBool = null;

        switch (valType) {
            case "uri":
                validatorFunc = UriValidator::validate;
                break;
            case "rpc_response":
                validatorFunc = UriValidator::validateRpcResponse;
                break;
            case "rpc_method":
                validatorFunc = UriValidator::validateRpcMethod;
                break;
            case "is_empty":
                validatorFuncBool = UriValidator::isEmpty;
                break;
            case "is_resolved":
                validatorFuncBool = UriValidator::isResolved;
                break;
            case "is_micro_form":
                validatorFuncBool = UriValidator::isMicroForm;
                break;
            case "is_long_form_uuri":
                validatorFuncBool = UriValidator::isLongForm;
                break;
            case "is_long_form_uauthority":
                validatorFuncBool = UriValidator::isLongForm;
                break;
        }

        if (validatorFunc != null) {
            ValidationResult status = validatorFunc.apply(uri);
            String result = status.isSuccess() ? "True" : "False";
            String message = status.getMessage();
            String testID = (String) jsonData.get("test_id");
            sendToTestManager(Map.of("result", result, "message", message), Constant.VALIDATE_URI, testID);
        } else if (validatorFuncBool != null) {
            Boolean status = validatorFuncBool.apply(uri);
            String result = status ? "True" : "False";
            String testID = (String) jsonData.get("test_id");
            sendToTestManager(Map.of("result", result, "message", ""), Constant.VALIDATE_URI, testID);
        }

        return null;
    }

    public static Object handleUAttributesValidateCommand(Map<String, Object> jsonData) {
        Map<String, Object> data = (Map<String, Object>) jsonData.get("data");
        String valMethod = (String) data.getOrDefault("validation_method", "default");
        String valType = (String) data.getOrDefault("validation_type", "default");

        UAttributes attributes = null;
        if (data.get("attributes") != null) {
            attributes = (UAttributes) ProtoConverter.dictToProto((Map<String, Object>)data.get("attributes"), UAttributes.newBuilder());
            if ("default".equals(attributes.getSink().getAuthority().getName())) {
                attributes = attributes.toBuilder().setSink(UUri.getDefaultInstance()).build();
            }
        } else {
            attributes = UAttributes.newBuilder().build();
        }

        if ("uprotocol".equals(data.get("id"))) {
            attributes = attributes.toBuilder().setId(UuidFactory.Factories.UPROTOCOL.factory().create()).build();
        } else if ("uuid".equals(data.get("id"))) {
            attributes = attributes.toBuilder().setId(UuidFactory.Factories.UUIDV6.factory().create()).build();
        }

        if ("uprotocol".equals(data.get("reqid"))) {
            attributes = attributes.toBuilder().setReqid(UuidFactory.Factories.UPROTOCOL.factory().create()).build();
        } else if ("uuid".equals(data.get("reqid"))) {
            attributes = attributes.toBuilder().setReqid(UuidFactory.Factories.UUIDV6.factory().create()).build();
        }

        String str_result = null;
        Boolean bool_result = null;
        ValidationResult val_result = null;

        UAttributesValidator pub_val = UAttributesValidator.Validators.PUBLISH.validator();
        UAttributesValidator req_val = UAttributesValidator.Validators.REQUEST.validator();
        UAttributesValidator res_val = UAttributesValidator.Validators.RESPONSE.validator();
        UAttributesValidator not_val = UAttributesValidator.Validators.NOTIFICATION.validator();

        if (attributes != null && attributes.getTtl() == 1) {
            try {
                Thread.sleep(800);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }

        if (valType.equals("get_validator")){
            str_result = UAttributesValidator.getValidator(attributes).toString();
        }

        switch (valMethod) {
            case "publish_validator":
                switch (valType) {
                    case "is_expired":
                        bool_result = pub_val.isExpired(attributes);
                        break;
                    case "validate_ttl":
                        val_result = pub_val.validateTtl(attributes);
                        break;
                    case "validate_sink":
                        val_result = pub_val.validateSink(attributes);
                        break;
                    case "validate_req_id":
                        val_result = pub_val.validateReqId(attributes);
                        break;
                    case "validate_id":
                        val_result = pub_val.validateId(attributes);
                        break;
                    case "validate_permission_level":
                        val_result = pub_val.validatePermissionLevel(attributes);
                        break;
                    default:
                        val_result = pub_val.validate(attributes);
                }
                break;
            case "request_validator":
                switch (valType) {
                    case "is_expired":
                        bool_result = req_val.isExpired(attributes);
                        break;
                    case "validate_ttl":
                        val_result = req_val.validateTtl(attributes);
                        break;
                    case "validate_sink":
                        val_result = req_val.validateSink(attributes);
                        break;
                    case "validate_req_id":
                        val_result = req_val.validateReqId(attributes);
                        break;
                    case "validate_id":
                        val_result = req_val.validateId(attributes);
                        break;
                    default:
                        val_result = req_val.validate(attributes);
                }
                break;
            case "response_validator":
                switch (valType) {
                    case "is_expired":
                        bool_result = res_val.isExpired(attributes);
                        break;
                    case "validate_ttl":
                        val_result = res_val.validateTtl(attributes);
                        break;
                    case "validate_sink":
                        val_result = res_val.validateSink(attributes);
                        break;
                    case "validate_req_id":
                        val_result = res_val.validateReqId(attributes);
                        break;
                    case "validate_id":
                        val_result = res_val.validateId(attributes);
                        break;
                    default:
                        val_result = res_val.validate(attributes);
                }
                break;
            case "notification_validator":
                switch (valType) {
                    case "is_expired":
                        bool_result = not_val.isExpired(attributes);
                        break;
                    case "validate_ttl":
                        val_result = not_val.validateTtl(attributes);
                        break;
                    case "validate_sink":
                        val_result = not_val.validateSink(attributes);
                        break;
                    case "validate_req_id":
                        val_result = not_val.validateReqId(attributes);
                        break;
                    case "validate_id":
                        val_result = not_val.validateId(attributes);
                        break;
                    case "validate_type":
                        val_result = not_val.validateType(attributes);
                        break;
                    default:
                        val_result = not_val.validate(attributes);
                }
                break;
            default:
                break;
        }

        String result = "";
        String message = "";

        if (bool_result != null){
            result = bool_result ? "True" : "False";
            message = "";
        } else if (val_result != null) {
            result = val_result.isSuccess() ? "True" : "False";
            message = val_result.getMessage();
        } else if (str_result != null) {
            result = "";
            message = str_result;
        }

        String testID = (String) jsonData.get("test_id");
        sendToTestManager(Map.of("result", result, "message", message), Constant.VALIDATE_UATTRIBUTES, testID);
        return null;
    }


    public static Object handleValidateUuidCommand(Map<String, Object> jsonData) {
        String uuidType = ((Map<String, Object>) jsonData.get("data")).getOrDefault("uuid_type", "default").toString();
        String validatorType = ((Map<String, Object>) jsonData.get("data")).getOrDefault("validator_type", "default").toString();

        UUID uuid;
        switch (uuidType) {
            case "uprotocol":
                uuid = UuidFactory.Factories.UPROTOCOL.factory().create();
                break;
            case "invalid":
                uuid = UUID.newBuilder().setMsb(0L).setLsb(0L).build();
                break;
            case "uprotocol_time":
                Instant epochTime = Instant.ofEpochMilli(0);
                uuid = UuidFactory.Factories.UPROTOCOL.factory().create(epochTime);
                break;
            case "uuidv6":
                uuid = UuidFactory.Factories.UUIDV6.factory().create();
                break;
            case "uuidv4":
                java.util.UUID uuid_java = java.util.UUID.randomUUID();
                uuid = UUID.newBuilder().setMsb(uuid_java.getMostSignificantBits())
                        .setLsb(uuid_java.getLeastSignificantBits()).build();
                break;
            default:
                uuid = null;
        }

        UStatus status;
        switch (validatorType) {
            case "get_validator":
                status = UuidValidator.getValidator(uuid).validate(uuid);
                break;
            case "uprotocol":
                status = UuidValidator.Validators.UPROTOCOL.validator().validate(uuid);
                break;
            case "uuidv6":
                status = UuidValidator.Validators.UUIDV6.validator().validate(uuid);
                break;
            case "get_validator_is_uuidv6":
                status = UuidUtils.isUuidv6(uuid) ? UStatus.newBuilder().setCode(UCode.OK).setMessage("").build()
                        : UStatus.newBuilder().setCode(UCode.FAILED_PRECONDITION).setMessage("").build();
                break;
            default:
                status = UStatus.newBuilder().setCode(UCode.FAILED_PRECONDITION).setMessage("").build();
        }

        String result = (status.getCode() == UCode.OK) ? "True" : "False";
        String message = status.getMessage();
        String testID = (String) jsonData.get("test_id");
        sendToTestManager(Map.of("result", result, "message", message), Constant.VALIDATE_UUID, testID);
        return null;
    }


    private static Object handleLongSerializeUuidCommand(Map<String, Object> jsonData) {
        Map<String, Object> data = (Map<String, Object>) jsonData.get("data");
        UUID uuid = (UUID) ProtoConverter.dictToProto(data, UUID.newBuilder());
        String serializedUUid = LongUuidSerializer.instance().serialize(uuid);
        String testID = (String) jsonData.get("test_id");
        sendToTestManager(serializedUUid, Constant.SERIALIZE_UUID, testID);
        return null;
    }

    private static Object handleLongDeserializeUuidCommand(Map<String, Object> jsonData) {
    	UUID uuid = LongUuidSerializer.instance().deserialize(jsonData.get("data").toString());
        String testID = (String) jsonData.get("test_id");
        sendToTestManager(uuid, Constant.DESERIALIZE_UUID, testID);
        return null;
    }

    private static Object handleMicroSerializeUuriCommand(Map<String, Object> jsonData) {
        Map<String, Object> data = (Map<String, Object>) jsonData.get("data");
        UUri uri = (UUri) ProtoConverter.dictToProto(data, UUri.newBuilder());
        byte[] serializedUuri = MicroUriSerializer.instance().serialize(uri);
        String serializedUuriAsStr = "";
        try {
			serializedUuriAsStr = new String(serializedUuri, "ISO-8859-1");
		} catch (UnsupportedEncodingException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			return null;
		}
        String testID = (String) jsonData.get("test_id");
        sendToTestManager(serializedUuriAsStr, Constant.MICRO_SERIALIZE_URI, testID);
        return null;
    }
    
    private static Object handleMicroDeserializeUuriCommand(Map<String, Object> jsonData) {
    	String microSerializedUuriAsStr = (String) jsonData.get("data");
    	byte[] microSerializedUuri = microSerializedUuriAsStr.getBytes(StandardCharsets.ISO_8859_1);
        UUri uri = MicroUriSerializer.instance().deserialize(microSerializedUuri);
 
        String testID = (String) jsonData.get("test_id");
        sendToTestManager(uri, Constant.MICRO_DESERIALIZE_URI, testID);
        return null;
    }

    private static void handleOnReceive(UMessage uMessage) {
        logger.info("Java on_receive called: " + uMessage);
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

                String jsonData = new String(buffer, 0, readSize);

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
