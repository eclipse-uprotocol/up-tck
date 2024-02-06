package org.tck;

import java.util.Arrays;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

import org.eclipse.uprotocol.cloudevent.serialize.Base64ProtobufSerializer;
import org.eclipse.uprotocol.rpc.RpcMapper;
import org.eclipse.uprotocol.transport.UListener;
import org.eclipse.uprotocol.uri.serializer.LongUriSerializer;
import org.eclipse.uprotocol.v1.UUri;
import org.eclipse.uprotocol.v1.UMessage;

import com.google.protobuf.Any;
import com.google.protobuf.ByteString;
import com.google.protobuf.InvalidProtocolBufferException;

public class test {
	
	private static byte[] base64ToProtobufBytes(String base64) {
    	return Base64ProtobufSerializer.serialize(base64);
    }
	
//	private static byte[] protobufToBase64(Any base64) {
//    	return Base64ProtobufSerializer.deserialize(base64);
//    }
	
	public static void main(String[] args) throws InvalidProtocolBufferException {
		// TODO Auto-generated method stub
		
//		 *!!!!works as intended!!!
//        UUri topic = LongUriSerializer.instance().deserialize( "/body.access//door.front_left#Door");        
//        UMessage umsg = UMessage.newBuilder()
//        		.setSource(topic)
//        		.build();
//        byte[] bytes = umsg.toByteArray();
//        System.out.println(bytes);
//        String message = Base64ProtobufSerializer.deserialize(bytes);
//        System.out.println(message);
        
	    Map<UUri, Integer> topicToListener = new ConcurrentHashMap<>();
	    UUri topic = LongUriSerializer.instance().deserialize( "/body.access//door.front_left#Door");  
	    UUri topic2 = LongUriSerializer.instance().deserialize( "/body.access//door.front_left#Door1");  
	    topicToListener.put(topic, 0);
	    System.out.println(topicToListener.containsKey(topic2));
	}

}
