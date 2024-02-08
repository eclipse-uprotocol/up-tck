import socket
from collections import defaultdict
import os
from uprotocol.proto.uattributes_pb2 import UAttributes
from uprotocol.proto.cloudevents_pb2 import CloudEvent
from uprotocol.proto.upayload_pb2 import UPayload, UPayloadFormat
from uprotocol.proto.uattributes_pb2 import UPriority
from uprotocol.uri.serializer.longuriserializer import LongUriSerializer

from google.protobuf.any_pb2 import Any
from uprotocol.transport.builder.uattributesbuilder import UAttributesBuilder

print(os.getcwd())

uri: str = "/body.access//door.front_left#Door"

def build_cloud_event(id: str):
    return CloudEvent(spec_version="1.0", source="https://example.com", id="I am " + id)

def build_upayload(id: str):
    any_obj = Any()
    any_obj.Pack(build_cloud_event(id))
    return UPayload(format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF, value=any_obj.SerializeToString())

def build_uattributes():
    return UAttributesBuilder.publish(UPriority.UPRIORITY_CS4).build()

topic = LongUriSerializer().deserialize(uri)
payload: UPayload = build_upayload("JAVA")
attributes: UAttributes = build_uattributes()

print(topic)
print(payload)
print(attributes)
print(UPriority.UPRIORITY_CS4)