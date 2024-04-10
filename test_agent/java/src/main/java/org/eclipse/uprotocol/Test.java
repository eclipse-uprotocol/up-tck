package org.eclipse.uprotocol;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.eclipse.uprotocol.v1.UCode;
import org.eclipse.uprotocol.v1.UStatus;
import org.eclipse.uprotocol.v1.UUri;
import org.json.JSONObject;
import org.eclipse.uprotocol.ProtoConverter;
import org.eclipse.uprotocol.v1.UEntity;
import org.eclipse.uprotocol.v1.UMessage;
import org.eclipse.uprotocol.uuid.serializer.LongUuidSerializer;
import org.eclipse.uprotocol.v1.UAttributes;
import org.eclipse.uprotocol.v1.UResource;
import org.eclipse.uprotocol.v1.UMessageType;
import org.eclipse.uprotocol.v1.UPayload;
import org.eclipse.uprotocol.v1.UPayloadFormat;
import org.eclipse.uprotocol.v1.UUID;

import com.google.gson.Gson;
import com.google.protobuf.ByteString;
import com.google.protobuf.Descriptors.FieldDescriptor;

import org.eclipse.uprotocol.v1.UAuthority;

public class Test {

	public static void main(String[] args) {
		// TODO Auto-generated method stub
		UStatus status = UStatus.newBuilder().setCode(UCode.OK).setMessage("Meow").build();
		Map<String, Object> m = ProtoConverter.convertMessageToMap(status);
		System.out.println(m);
		
		JSONObject responseDict = new JSONObject();
        responseDict.put("data", m);
        
		
		UAuthority auth = UAuthority.newBuilder().setName("name").setId(ByteString.copyFrom("somebytes idk".getBytes())).build();
		UEntity entity = UEntity.newBuilder().setName("entity Name").setId(123).build();
		UResource resource = UResource.newBuilder().setName("body.access").setInstance("front_left").setMessage("Door").build();
		UUri uri = UUri.newBuilder().setAuthority(auth).setEntity(entity).setResource(resource).build();
		
		UAttributes attr = UAttributes.newBuilder().setSource(uri).setType(UMessageType.UMESSAGE_TYPE_PUBLISH).build();
		UPayload pay = UPayload.newBuilder().setValue(ByteString.copyFrom("type.googleapis.com/google.protobuf.Int32Value\\\\x12\\\\x02\\\\x08\\\\x03".getBytes())).setFormat(UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF_WRAPPED_IN_ANY).build();
		UMessage msg = UMessage.newBuilder().setAttributes(attr).setPayload(pay).build();
		Map<String, Object> m1 = ProtoConverter.convertMessageToMap(msg);
		System.out.println(m1);
		
		Map<String, Object> r = new HashMap<>();
		
		r.put("data", m1);
		System.out.println(r);
		UUID uuid = LongUuidSerializer.instance().deserialize("018e5c10-f548-8001-9ad1-7b068c083824");
		System.out.println(uuid);
		Map<String, Object> uuidM = ProtoConverter.convertMessageToMap(uuid);
		System.out.println(uuidM);
	}

}
