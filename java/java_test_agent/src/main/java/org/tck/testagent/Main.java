package org.tck.testagent;

import com.google.protobuf.Any;
import io.cloudevents.v1.proto.CloudEvent;
import org.eclipse.uprotocol.v1.*;
import org.json.JSONObject;
import org.tck.up_client_socket_java.SocketUListener;
import org.tck.up_client_socket_java.SocketUTransport;

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
            SocketUTransport socketUTransport = new SocketUTransport("127.0.0.1", 44444);
            logger.info("Connected in UTransport");
            Socket clientSocket = new Socket("127.0.0.5", 12345);
            logger.info("Connected in TM");

            TestAgent agent = new TestAgent(clientSocket, socketUTransport, new SocketUListener(clientSocket));
            JSONObject obj = new JSONObject();
            obj.put("SDK_name", "java");
            agent.sendToTM(obj);
        } catch (SecurityException | IOException e) {
            e.printStackTrace();
        }
    }

    private static UPayload buildUPayload() {
        CloudEvent cloudEvent = CloudEvent.newBuilder()
                .setSpecVersion("1.0")
                .setSource("https://example.com")
                .setId("HARTLEY IS THE BEST")
                .build();
        Any any_obj = Any.pack(cloudEvent);
        return UPayload.newBuilder()
                .setFormat(UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF)
                .setValue(any_obj.toByteString())
                .build();
    }

    private static UAttributes buildUAttributes() {
        return UAttributes.newBuilder()
                .setPriority(UPriority.UPRIORITY_CS4)
                .build();
    }

    private static CloudEvent buildCloudEvent() {
        return CloudEvent.newBuilder()
                .setSpecVersion("1.0")
                .setSource("https://example.com")
                .setId("HARTLEY IS THE BEST")
                .build();
    }
}
