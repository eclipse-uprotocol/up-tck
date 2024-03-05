from google.protobuf import any_pb2

from uprotocol.uuid.factory.uuidfactory import Factories
from uprotocol.proto.uri_pb2 import UUri
from uprotocol.proto.uri_pb2 import UAuthority
from uprotocol.proto.uri_pb2 import UEntity
from uprotocol.proto.uri_pb2 import UResource
from uprotocol.proto.uattributes_pb2 import *
from uprotocol.transport.builder.uattributesbuilder import UAttributesBuilder
from uprotocol.uri.serializer.longuriserializer import LongUriSerializer
from google.protobuf.wrappers_pb2 import Int32Value

from up_client_socket_python.transport_layer import TransportLayer


def publish():
    # Example payload and attributes

    from uprotocol.proto.upayload_pb2 import UPayloadFormat, UPayload
    hint = UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF

    from uprotocol.proto.uattributes_pb2 import UPriority

    any_obj = any_pb2.Any()
    any_obj.Pack(Int32Value(value=5))
    payload_data = any_obj.SerializeToString()
    payload = UPayload(value=payload_data, format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF)
    u_authority = UAuthority(name="myremote")
    u_entity = UEntity(name='body.access', version_major=1)
    u_resource = UResource(name="door", instance="front_left", message="Door")
    uri = UUri(authority=u_authority, entity=u_entity, resource=u_resource)
    attributes = UAttributesBuilder.publish(uri, UPriority.UPRIORITY_CS4).build()
    transport = TransportLayer()
    transport.set_socket_config("127.0.0.1", 44444)
    transport.send(uri, payload, attributes)


if __name__ == '__main__':
    publish()
