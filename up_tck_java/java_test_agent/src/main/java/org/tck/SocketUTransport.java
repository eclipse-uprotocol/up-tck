package org.tck;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.Socket;
import java.util.Arrays;
import java.util.Map;
import java.util.logging.Logger;
import java.util.concurrent.ConcurrentHashMap;

import org.eclipse.uprotocol.transport.UListener;
import org.eclipse.uprotocol.transport.UTransport;
import org.eclipse.uprotocol.v1.*;
import org.eclipse.uprotocol.v1.UMessage;

public class SocketUTransport implements UTransport {

    private final Socket socket;
    private final Map<byte[], UListener> topicToListener = new ConcurrentHashMap<>();
    private static final int MSG_LEN = 32767;
    private static final Logger logger = Logger.getLogger("simple_example");

    public SocketUTransport(String hostIp, int port) throws IOException {
        socket = new Socket(hostIp, port);
        Thread thread = new Thread(this::listen);
        thread.start();
    }

    private void listen() {
        try {
            while (true) {
                InputStream inputStream = socket.getInputStream();
                byte[] buffer = new byte[32767];  //new byte[174];
                int readSize = inputStream.read(buffer);
                System.out.println(readSize);

                UMessage umsg = UMessage.parseFrom(Arrays.copyOfRange(buffer, 0, readSize) );
                System.out.println("Received uMessage: " + umsg);

                UUri topic = umsg.getSource();
                UPayload payload = umsg.getPayload();
                UAttributes attributes = umsg.getAttributes();
                if (topicToListener.containsKey(topic)) {
                    topicToListener.get(topic).onReceive(topic, payload, attributes);
                } else {
                    System.out.println("Topic not found in Listener Map, discarding...");
                }
            }
        } catch (IOException e) {
            try {
                socket.close();
            } catch (IOException ioException) {
                ioException.printStackTrace();
            }
        }
    }

    @Override
    public UStatus send(UUri topic, UPayload payload, UAttributes attributes) {
        UMessage umsg = UMessage.newBuilder()
                .setSource(topic)
                .setAttributes(attributes)
                .setPayload(payload)
                .build();

        byte[] umsgSerialized = umsg.toByteArray();

        try {
            OutputStream outputStream = socket.getOutputStream();
            outputStream.write(umsgSerialized);
            outputStream.flush();
            System.out.println("uMessage Sent");
        } catch (IOException e) {
            return UStatus.newBuilder()
                    .setCode(UCode.INTERNAL)
                    .setMessage("INTERNAL ERROR: IOException sending UMessage")
                    .build();
        }

        return UStatus.newBuilder()
                .setCode(UCode.OK)
                .setMessage("OK")
                .build();
    }

    @Override
    public UStatus registerListener(UUri topic, UListener listener) {
        byte[] topicSerialized = topic.toByteArray();
        topicToListener.put(topicSerialized, listener);

        return UStatus.newBuilder()
                .setCode(UCode.OK)
                .setMessage("OK")
                .build();
    }

    @Override
    public UStatus unregisterListener(UUri topic, UListener listener) {
        byte[] topicSerialized = topic.toByteArray();
        topicToListener.remove(topicSerialized);

        return UStatus.newBuilder()
                .setCode(UCode.OK)
                .setMessage("OK")
                .build();
    }
}
