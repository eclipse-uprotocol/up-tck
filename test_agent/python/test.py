from uprotocol.uuid.factory.uuidfactory import Factories
from uprotocol.proto.uuid_pb2 import UUID
from datetime import datetime, timezone
from uprotocol.uuid.serializer.longuuidserializer import LongUuidSerializer

uprotocol = Factories.UPROTOCOL.create()
print(type(uprotocol))
print(uprotocol)


invalid = UUID(msb=0, lsb=0)
print(type(invalid))
print(invalid)

uprotocol_time = Factories.UPROTOCOL.create(
            datetime.utcfromtimestamp(0).replace(tzinfo=timezone.utc)
        )
print(type(uprotocol_time))
print("time:", uprotocol_time)

uuidv6 = Factories.UUIDV6.create()
print(type(uuidv6))
print(uuidv6)


uuidv4 = LongUuidSerializer().deserialize("195f9bd1-526d-4c28-91b1-ff34c8e3632d")
print(type(uuidv4))
print(uuidv4)