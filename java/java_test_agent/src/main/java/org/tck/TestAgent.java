package org.tck;

import org.eclipse.uprotocol.cloudevent.serialize.Base64ProtobufSerializer;
import org.eclipse.uprotocol.transport.UListener;
import org.eclipse.uprotocol.v1.*;
import org.eclipse.uprotocol.v1.UMessage;
import org.eclipse.uprotocol.rpc.RpcMapper;
import org.json.JSONObject;

import com.google.protobuf.CodedOutputStream;
import com.google.protobuf.Any;
import com.google.protobuf.ByteString;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import java.util.concurrent.ThreadLocalRandom;

public class TestAgent {
    private SocketUTransport socketUTransport;
    private JSONObject obj;
    private Socket clientSocket;

    public TestAgent(Socket socket, SocketUTransport utransport, SocketUListener listener) {
        try {
        	// Socket Connection to Dispatcher
            this.socketUTransport = utransport;
            
            // Client Socket connection to Test Manager
            clientSocket = socket;
            
            // Listening thread to receive messages from Test Manager
            Thread receiveThread = new Thread(() -> receiveFromTM(listener));
            receiveThread.start();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    private byte[] base64ToProtobufBytes(String base64) {
    	return Base64ProtobufSerializer.serialize(base64);
    }
    
    private String protoboufToBase64(UStatus status) {
    	return Base64ProtobufSerializer.deserialize(status.toByteArray());
    }

    private void receiveFromTM(UListener listener) {
        int msgLen = 32767;
        try {
            InputStream clientInputStream = clientSocket.getInputStream();
            while (true) {
                byte[] recvData = new byte[msgLen];
                int bytesRead = clientInputStream.read(recvData);
                if (bytesRead > 0) {
                    String jsonStr = new String(recvData, 0, bytesRead, StandardCharsets.UTF_8);
                    System.out.println("jsonMsg from TM: " + jsonStr);
                    
                    obj = new JSONObject(jsonStr);
                    System.out.println("json obj:" + obj);

                    String action = obj.getString("action");
                    System.out.println("action ->" + obj);
                    
                    String message = obj.getString("message");
                    byte[] protobuf_bytes = base64ToProtobufBytes(message);
                    System.out.println("message ->" + protobuf_bytes);
                    
//                    Any any = Any.newBuilder().setValue(ByteString.copyFrom(protobuf_bytes)).build();
//                    Any any = Any.parseFrom(protobuf_bytes);
//                    System.out.println("any:");
//                    System.out.println(any);

//                    UMessage umsg = RpcMapper.unpackPayload(any, UMessage.class);
                    UMessage umsg = UMessage.parseFrom(protobuf_bytes);

                    System.out.println(umsg);

                    UStatus status = null;
                    switch (action) {
                        case "send":
                            status = socketUTransport.send(umsg.getSource(), umsg.getPayload(), umsg.getAttributes());
                            break;
                        case "registerlistener":
                            status = socketUTransport.registerListener(umsg.getSource(), listener);
                            break;
                    }
                    this.send(status);
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public void send(UUri topic, UPayload payload, UAttributes attributes) {
        UMessage umsg = UMessage.newBuilder()
                .setSource(topic)
                .setAttributes(attributes)
                .setPayload(payload)
                .build();
        byte[] base64umsg = umsg.toByteArray();
        obj.put("action", "send");
        obj.put("message", Base64ProtobufSerializer.deserialize(base64umsg));

        sendToTM(obj);

    }

    public void send(UStatus status) {
    	JSONObject json = new JSONObject();
        json.put("action", "uStatus");
        json.put("message", protoboufToBase64(status));
        sendToTM(json);
    }

    void sendToTM(JSONObject jsonObject) {
        try {
            OutputStream clientOutputStream = clientSocket.getOutputStream();
            String jsonString = jsonObject.toString();
            byte[] messageBytes = jsonString.getBytes(StandardCharsets.UTF_8);
            clientOutputStream.write(messageBytes);
            clientOutputStream.flush();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public void registerListener(UUri topic, UListener listener) {
        try {
            socketUTransport.registerListener(topic, listener);
            // Additional logic if needed
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public void unregisterListener(int clientPort) {
        try {
            // Additional logic to unregister listener based on clientPort
            // ...
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

}