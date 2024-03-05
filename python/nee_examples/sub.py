import time

from uprotocol.proto.uattributes_pb2 import UAttributes
from uprotocol.transport.ulistener import UListener
from uprotocol.proto.upayload_pb2 import UPayload
from uprotocol.proto.ustatus_pb2 import UStatus

from uprotocol.proto.uri_pb2 import UUri
from uprotocol.proto.uri_pb2 import UAuthority
from uprotocol.proto.uri_pb2 import UEntity
from uprotocol.proto.uri_pb2 import UResource

from up_client_socket_python.transport_layer import TransportLayer


class MyListener(UListener):

    def on_receive(self, topic: UUri, payload: UPayload, attributes: UAttributes) -> UStatus:
        print('on receive called')
        print(payload.value)
        print(attributes.__str__())
        print(topic.__str__())
        return UStatus(message="Received event")


def subscribe():
    from uprotocol.uri.serializer.longuriserializer import LongUriSerializer

    u_authority = UAuthority(name="myremote")
    u_entity = UEntity(name='body.access', version_major=1)
    u_resource = UResource(name="door", instance="front_left", message="Door")
    uri = UUri(authority=u_authority, entity=u_entity, resource=u_resource)
    transport = TransportLayer()
    transport.set_socket_config("127.0.0.1", 44444)
    transport.register_listener(uri, MyListener())


if __name__ == '__main__':
    subscribe()
    time.sleep(30000)
