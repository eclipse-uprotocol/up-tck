package org.tck;

import org.eclipse.uprotocol.cloudevent.serialize.Base64ProtobufSerializer;
import org.eclipse.uprotocol.transport.UListener;
import org.eclipse.uprotocol.v1.*;
import org.json.JSONObject;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import java.util.concurrent.ThreadLocalRandom;

public class TestAgent {
    SocketUTransport socketUTransport;
    JSONObject obj;
    Socket clientSocket;
    private ConcurrentMap<String, String> connections = new ConcurrentHashMap<>();
    private ConcurrentMap<String, Socket> portToClient = new ConcurrentHashMap<>();

    public TestAgent(Socket socket, SocketUTransport utransport, SocketUListener listener) {
        try {
            this.socketUTransport = (SocketUTransport) utransport;
            clientSocket = new Socket();
            portToClient.put(Integer.toString(ThreadLocalRandom.current().nextInt(1, 10000)), clientSocket);
            Thread receiveThread = new Thread(() -> receiveFromTM(listener));
            receiveThread.start();
        } catch (Exception e) {
            e.printStackTrace();
        }
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
                    System.out.println("json obj ->" + obj);

                    String action = obj.getString("action");
                    System.out.println("action ->" + obj);
                    String message = obj.getString("message");
                    byte[] base64 = Base64ProtobufSerializer.serialize(message);
                    System.out.println("message ->" + base64);
                    /*UMessage responseProto = RpcMapper.unpackPayload(new Any(base64), org.eclipse.uprotocol.v1.UMessage.class);

                    UStatus status = null;
                    switch (action) {
                        case "send":
                            status = socketUTransport.send(responseProto.getSource(), responseProto.getPayload(), responseProto.getAttributes());
                            break;
                        case "registerlistener":
                            status = socketUTransport.registerListener(responseProto.getSource(), listener);
                            break;
                    }
                    this.send(status);*/
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
        System.out.println("status ->" + status);
        byte[] base64status = status.toByteArray();
        obj.put("action", "uStatus");
        obj.put("message", Base64ProtobufSerializer.deserialize(base64status));
        sendToTM(obj);
    }

    void sendToTM(JSONObject jsonObject) {
        try {
            OutputStream clientOutputStream = clientSocket.getOutputStream();
            String jsonString = jsonObject.toString();
            byte[] messageBytes = jsonString.getBytes(StandardCharsets.UTF_8);
            clientOutputStream.write(messageBytes);
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