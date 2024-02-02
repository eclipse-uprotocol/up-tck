package org.tck;

import java.io.IOException;
import java.io.OutputStream;
import java.net.Socket;
import java.nio.charset.StandardCharsets;

import org.eclipse.uprotocol.cloudevent.serialize.Base64ProtobufSerializer;
import org.eclipse.uprotocol.transport.UListener;
import org.eclipse.uprotocol.v1.*;
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
    public void onReceive(UUri topic, UPayload payload, UAttributes attributes) {
        System.out.println("Listener onReceived");
        System.out.println(payload);

        UMessage umsg = UMessage.newBuilder()
                .setSource(topic)
                .setAttributes(attributes)
                .setPayload(payload)
                .build();

        JSONObject json = new JSONObject();
        json.put("action", "uStatus");
        json.put("message", protoboufToBase64(umsg));

        try {

            OutputStream clientOutputStream = testAgentConnection.getOutputStream();
            String jsonString = json.toString();
            byte[] messageBytes = jsonString.getBytes(StandardCharsets.UTF_8);
            clientOutputStream.write(messageBytes);
            clientOutputStream.flush();

        } catch (IOException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
    }
}