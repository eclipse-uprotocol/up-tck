#!/usr/bin/env python3

from threading import Thread
# from uprotocol.proto.uattributes_pb2 import UMessageType, UPriority
# from uprotocol.proto.ustatus_pb2 import UCode
from dispatcher.dispatcher import Dispatcher

print("after import")

dispatcher = Dispatcher()
thread = Thread(target=dispatcher.listen_for_client_connections)
thread.start()
