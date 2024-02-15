from uprotocol.proto.uuid_pb2 import UUID

id_str = "long encoded string"
id_bytes: bytes = id_str.encode()
id: UUID = UUID(msb=id_bytes)
print(id)