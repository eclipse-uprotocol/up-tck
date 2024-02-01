package org.tck;

import com.google.protobuf.Any;
import com.google.protobuf.Int32Value;
import io.cloudevents.v1.proto.CloudEvent;
import org.eclipse.uprotocol.v1.UAttributes;
import org.eclipse.uprotocol.v1.UPayload;
import org.eclipse.uprotocol.v1.UPayloadFormat;
import org.eclipse.uprotocol.v1.UPriority;
import org.eclipse.uprotocol.v1.*;
import org.eclipse.uprotocol.uri.serializer.LongUriSerializer;
import org.json.JSONObject;

import java.io.IOException;
import java.net.Socket;

public class Main {
    public static void main(String[] args) throws IOException {
        // how to merge and sync forked repo: https://www.freecodecamp.org/news/how-to-sync-your-fork-with-the-original-git-repository/
        SocketUTransport socketUTransport = new SocketUTransport("127.0.0.1", 44444);
        System.out.println("Connected in UTransport");
        Socket clientSocket = new Socket("127.0.0.5", 12345);
        System.out.println("Connected in TM");

        TestAgent agent = new TestAgent(clientSocket, socketUTransport, new SocketUListener(clientSocket));
        JSONObject obj = new JSONObject();
        obj.put("SDK_name", "java");
//        UUri topic = LongUriSerializer.instance().deserialize("/body.access//door.front_left#Door");
//        UPayload payload = buildUPayload();
//        UAttributes attributes = buildUAttributes();

        agent.sendToTM(obj);
    }

    private static UPayload buildUPayload() {
//        Any anyObj = Any.pack(Int32Value.of(3));
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
