from ast import Dict
import socket
import time
import json 
from python.utils.socket_message_processing_utils import convert_bytes_to_string, convert_json_to_jsonstring, convert_jsonstring_to_json, convert_str_to_bytes

test_manager_IP: str = "localhost"
test_manager_PORT: int = 1234
test_agent_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
test_agent_socket1.connect((test_manager_IP, test_manager_PORT))  

test_agent_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
test_agent_socket2.connect((test_manager_IP, test_manager_PORT))  

test_agent_socket3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
test_agent_socket3.connect((test_manager_IP, test_manager_PORT))  


recv_size = 1000

json_message = {'SDK_name': "java"}
json_message_str: str = convert_json_to_jsonstring(json_message)
message: bytes = convert_str_to_bytes(json_message_str)
        
        
filler =  b' ' * (recv_size - len(message))
test_agent_socket1.send(message + filler)
# test_agent_socket1.send(message)  

recv_data: bytes = test_agent_socket1.recv(recv_size)

json_str: str = convert_bytes_to_string(recv_data) 
# json_str = json_str.strip()
print("no strip")
print(json_str, len(json_str), type(json_str))
print(json.loads(json_str), type(json.loads(json_str)))
json_msg = convert_jsonstring_to_json(json_str)

print("json_msg", json_msg)
while True:
    pass