import socket
import json
from google.protobuf.any_pb2 import Any
from typing import Dict

from uprotocol.cloudevent.serialize.base64protobufserializer import Base64ProtobufSerializer

def send_socket_data(s: socket.socket , msg: bytes):
    s.send(msg)

def receive_socket_data(s: socket.socket) -> bytes:
    bytes_mesg_len: int = 32767
    return s.recv(bytes_mesg_len)

def protobuf_to_base64(obj: Any) -> str:
    serial_proto: bytes = obj.SerializeToString()
    return Base64ProtobufSerializer().deserialize(serial_proto)  # base64.b64encode(obj.SerializeToString()).decode('ASCII')  

def base64_to_protobuf_bytes(base64str: str) -> bytes:
    return Base64ProtobufSerializer().serialize(base64str)

def convert_bytes_to_string(data: bytes) -> str:
    return data.decode()

def convert_jsonstring_to_json(jsonstring: str) -> Dict[str, str]:
    return json.loads(jsonstring) 

def convert_json_to_jsonstring(j: Dict[str, str]) -> str:
    return json.dumps(j)

def convert_str_to_bytes(string: str) -> bytes:
    return str.encode(string) 