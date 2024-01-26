import socket
import threading
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
from typing import Dict
import json
import base64
from multipledispatch import dispatch
from google.protobuf.any_pb2 import Any
import time

from uprotocol.proto.uattributes_pb2 import UAttributes
from uprotocol.proto.uri_pb2 import UUri
from uprotocol.proto.upayload_pb2 import UPayload
from uprotocol.proto.umessage_pb2 import UMessage
from uprotocol.proto.ustatus_pb2 import UStatus, UCode
from uprotocol.transport.ulistener import UListener

from uprotocol.proto.cloudevents_pb2 import CloudEvent
from uprotocol.proto.upayload_pb2 import UPayload, UPayloadFormat
from uprotocol.proto.uattributes_pb2 import UPriority
from uprotocol.transport.builder.uattributesbuilder import UAttributesBuilder
from uprotocol.uri.serializer.longuriserializer import LongUriSerializer
from ulink_socket_python.socket_utransport import SocketUTransport
from test_ulistener import SocketUListener
from uprotocol.transport.utransport import UTransport
import logging 

logging.basicConfig(format='%(asctime)s %(message)s')
# Create logger
logger = logging.getLogger('simple_example')
logger.setLevel(logging.INFO)

def serialize_protobuf_to_base64(obj: Any):
    return base64.b64encode(obj.SerializeToString()).decode('ASCII')

class SocketUListener(UListener):
    def __init__(self) -> None:
        pass

    def on_receive(self, topic: UUri, payload: UPayload, attributes: UAttributes) -> UStatus:
        """
        Method called to handle/process events.<br><br>
        @param topic: Topic the underlying source of the message.
        @param payload: Payload of the message.
        @param attributes: Transportation attributes.
        @return Returns an Ack every time a message is received and processed.
        """
        logger.info("Listener onreceived")
        logger.info("MATTHEW is awesome!!!")

        # logger.info(f"{topic}")
        # logger.info(f"----")
        logger.info(f"{payload}")
        # logger.info(f"----")
        # logger.info(f"{attributes}")
        # logger.info(f"--END--")

        return UStatus(code=UCode.OK, message="all good") 

class TestManager:
    def __init__(self, ip_addr: str, port: int, utransport: UTransport) -> None:
        """
        The test server that the Test Agent will connect to
        Idea: acts as validator to validate data sent in ulink-socket-xxx

        """

        self.utransport: SocketUTransport = utransport

        self.sdk_to_port: Dict[str, int] = defaultdict(int)
        self.sdk_to_socket: Dict[str, socket.socket] = defaultdict(None)

        self.possible_received_protobufs = [UMessage(), UStatus()]

        # Create test manager socket object.
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind to socket server.
        self.server.bind((ip_addr, port))  

        # Put the socket into listening mode.
        self.server.listen(5)  
    
    def listen_for_client_connections(self):
        while True:
            print("waiting on client connection ...")
            clientsocket, (client_ip, client_port) = self.server.accept()

            thread = threading.Thread(target=self.initialize_new_client_connection, args=(clientsocket, client_port))
            thread.start()

    def initialize_new_client_connection(self, clientsocket: socket.socket, client_port: int):
        recv_data: bytes = clientsocket.recv(32767)

        json_str: str = recv_data.decode() # decode bytes -> str like JSON 
        json_msg: Dict[str, str] = json.loads(json_str)  # conver JSON Str -> JSON/Dictionary/Map

        # during init, should receive a SDK_name json msg immediately after connection
        if "SDK_name" in json_msg:
            sdk: str = json_msg["SDK_name"]
 
            self.sdk_to_port[sdk] = client_port
            self.sdk_to_socket[sdk] = clientsocket
        else:
            raise Exception("new client connection didn't initally send sdk name")
        
        print("Initialized new client socket!")
        print(self.sdk_to_socket)
    
    def __send_to_client(self, client: socket.socket, json_message: Dict[str, str]):
        # convert a dictionary/map -> JSON string
        json_message_str: str = json.dumps(json_message)

        print("sending", json_message)

         # to send data over a socket, we have to send in bytes --> convert JSON STRING into bytes
        message: bytes = str.encode(json_message_str)   # send this to socket in bytes
        
        client.send(message)

    def __parse_socket_received_data(self, recv_data: bytes) -> bytes:
        json_str: str = recv_data.decode() # decode bytes -> str like JSON 
        json_msg: Dict[str, str] = json.loads(json_str)  # conver JSON Str -> JSON/Dictionary/Map

        umsg_base64: str = json_msg["message"]
        protobuf_serialized_data: bytes = base64.b64decode(umsg_base64)  # decode base64 encoding --> serialized protobuf 

        return protobuf_serialized_data
    
    def __send_json_msg_to_TA(self, sdk_name:str, command: str, umsg: UMessage):
        # Send to Test Agent
        json_message = {
            "action": command,
            "message": serialize_protobuf_to_base64(umsg)
        }

        clientsocket: socket.socket = self.sdk_to_socket[sdk_name]
        self.__send_to_client(clientsocket, json_message)

        response_data: bytes = clientsocket.recv(32767)

        protobuf_serialized_data: bytes = self.__parse_socket_received_data(response_data)

        status = UStatus()
        status.ParseFromString(protobuf_serialized_data)

        return status

    def send_command(self, sdk_name: str, command: str,  topic: UUri, payload: UPayload, attributes: UAttributes):
        """
        sends data to TA params (action/command and complete Umessage)
        BLOCKING/SYNCHRONOUS call!!! So wait after send for a UStatus b/c theres no msg id to map it to after its done

        SCenarios (TRUTH):
        SDKS are always unique
        get socket thru the sdk then send
        """
        if sdk_name.lower() == "python":
            # send thru Socket UTransport
            status: UStatus = self.utransport.send(topic, payload, attributes)
        else:
            # Send to Test Agent
            '''
            umsg: UMessage = UMessage(source=topic, attributes=attributes, payload=payload)

            json_message = {
                "action": command,
                "message": serialize_protobuf_to_base64(umsg)
            }

            clientsocket: socket.socket = self.sdk_to_socket[sdk_name]
            self.__send_to_client(clientsocket, json_message)

            response_data: bytes = clientsocket.recv(32767)

            protobuf_serialized_data: bytes = self.__parse_socket_received_data(response_data)

            status = UStatus()
            status.ParseFromString(protobuf_serialized_data)'''
            umsg: UMessage = UMessage(source=topic, attributes=attributes, payload=payload)
            status: UStatus = self.__send_json_msg_to_TA(sdk_name, command, umsg)
        
        return status

    def register_listener_command(self, sdk_name: str, command: str, topic: UUri, listener: UListener):
        """
        sends data to TA params (action/command and UURi Umessage)

        Before registering listener​...
        Create entry in table for given SDK, 
        uURI and register a callback which 
        will be invoked when onReceive event received. For given SDK.​

        (sdk, uuri) --> UListener
        """
        sdk_name = sdk_name.lower().strip()
        if sdk_name == "python":
            # send thru Socket UTransport
            status: UStatus = self.utransport.register_listener(topic, listener)
            print("registered in uTransport python")
        else:
            print("register in uTransport else")

            # Send to Test Agent
            umsg: UMessage = UMessage(source=topic)
            '''
            json_message = {
                "action": command,
                "message": serialize_protobuf_to_base64(umsg)
            }

            clientsocket: socket.socket = self.sdk_to_socket[sdk_name]
            self.__send_to_client(clientsocket, json_message)

            response_data: bytes = clientsocket.recv(32767)

            protobuf_serialized_data: bytes = self.__parse_socket_received_data(response_data)

            status = UStatus()
            status.ParseFromString(protobuf_serialized_data)
            '''
            status: UStatus = self.__send_json_msg_to_TA(sdk_name, command, umsg)

        return status

    def unregister_listener(self, sdk: str, command: str, topic: UUri, listener: UListener):
        """
        sends data to TA params (action/command and UURi Umessage)
        """
        
        umsg: UMessage = UMessage(source=topic)

        # create the Json message
        json_message = {
            "action": "registerListener",
            "message": serialize_protobuf_to_base64(umsg)
        }

        self.__send_to_client(self.port_to_client[client_port], json_message)


    def ustatus(self):
        """
        sends Ustatus protobuf
        """
        pass

# port for Test Agent Connection
socket_utransport = SocketUTransport("127.0.0.1", 44444)
print("starting socket_utransport")
manager = TestManager("127.0.0.5", 12345, socket_utransport)
print("starting TestManager")


uri: str = "/body.access//door.front_left#Door"

def build_cloud_event(id: str):
    return CloudEvent(spec_version="1.0", source="https://example.com", id="I am " + id)

def build_upayload(id: str):
    any_obj = Any()
    any_obj.Pack(build_cloud_event(id))
    return UPayload(format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF, value=any_obj.SerializeToString())

def build_uattributes():
    return UAttributesBuilder.publish(UPriority.UPRIORITY_CS4).build()


listener: UListener = SocketUListener()

with ThreadPoolExecutor(max_workers=1) as executor:
    # submit the task
    future = executor.submit(manager.listen_for_client_connections)
    time.sleep(10)
    # manager.send_to_all_ports(topic, payload, attributes)
    while True:
        sdk: str = input("Enter SDK Language[java/python]: ")
        sdk = sdk.strip()
        command_name = input("Enter Command Name[send/registerlistener]: ")
        command_name = command_name.strip().lower()

        topic = LongUriSerializer().deserialize(uri)
        payload: UPayload = build_upayload(sdk)
        attributes: UAttributes = build_uattributes()

        print(sdk, command_name)
        if command_name == "send": 
            print("SEND COMMAND")
            status: UStatus = manager.send_command(sdk, command_name, topic, payload, attributes)
        elif command_name == "registerlistener":
            status: UStatus = manager.register_listener_command(sdk, command_name, topic, listener)
        else:
            print("in exception!")
            raise Exception("none other commands ")
        print("sdk:", sdk)
        print("status:", status)
        print("---------------")