from google.protobuf import any_pb2, empty_pb2
from uprotocol.rpc.calloptions import CallOptions
from uprotocol.rpc.rpcmapper import RpcMapper
from uprotocol.proto.uri_pb2 import UUri
from uprotocol.uri.factory.uresource_builder import UResourceBuilder
from uprotocol.uuid.factory.uuidfactory import Factories
from uprotocol.proto.upayload_pb2 import UPayload
from uprotocol.proto.uattributes_pb2 import *
# from org_eclipse_uprotocol_zenoh.zenoh_utransport import Zenoh
# from sdv_simulation.protofiles.ultifi.vehicle.body.access.v1 import access_topics_pb2, access_service_pb2
from uprotocol.proto.upayload_pb2 import UPayloadFormat
from google.protobuf.wrappers_pb2 import Int32Value
from up_client_socket_python.transport_layer import TransportLayer
from uprotocol.proto.uattributes_pb2 import UAttributes, UPriority, UMessageType

if __name__ == '__main__':
    # Example payload and attributes
    from uprotocol.proto.uri_pb2 import UUri
    from uprotocol.proto.uri_pb2 import UAuthority
    from uprotocol.proto.uri_pb2 import UEntity
    from uprotocol.proto.uri_pb2 import UResource

    hint = UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF
    any_obj = any_pb2.Any()


    any_obj.Pack(Int32Value(value=7))
    payload_data = any_obj.SerializeToString()
    payload = UPayload(value=payload_data,format= hint)
    u_entity = UEntity(name="body.access")
    u_resource = UResourceBuilder.for_rpc_request("ExecuteDoorCommand")
    uri = UUri(entity=u_entity,resource= u_resource)
    from uprotocol.transport.builder.uattributesbuilder import UAttributesBuilder

    id_val = Factories.UPROTOCOL.create()
    attributes = UAttributesBuilder.request(uri, uri, UPriority.UPRIORITY_CS4, 1000000).build()
    transport = TransportLayer()
    transport.set_socket_config("127.0.0.1", 44444)
    res_future = transport.invoke_method(uri, payload, attributes)
    print('after invoke')
    try:
        # result = res_future.result()
        status=RpcMapper.map_response(res_future,Int32Value())
        # any_data = any_pb2.Any()
        # any_data.ParseFromString(result.get_data())
        # print('neelam', result)
        print('data', status)
        
        while not res_future.done():
            continue
        print(res_future.result(), res_future.done())
    except TimeoutError as e:
        print('Timeout Exception-',str(e))
