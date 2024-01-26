import socket
import threading
from collections import defaultdict
from typing import Dict
import json
import base64
from multipledispatch import dispatch
from google.protobuf.any_pb2 import Any
import time
from threading import Thread

from uprotocol.proto.uattributes_pb2 import UAttributes
from uprotocol.proto.uri_pb2 import UUri
from uprotocol.proto.umessage_pb2 import UMessage
from uprotocol.proto.ustatus_pb2 import UStatus, UCode
from uprotocol.proto.cloudevents_pb2 import CloudEvent
from uprotocol.proto.upayload_pb2 import UPayload, UPayloadFormat
from uprotocol.proto.uattributes_pb2 import UPriority
from uprotocol.transport.builder.uattributesbuilder import UAttributesBuilder
from uprotocol.uri.serializer.longuriserializer import LongUriSerializer

from uprotocol.transport.utransport import UTransport
from ulink_socket_python.socket_utransport import SocketUTransport

from uprotocol.transport.ulistener import UListener

# on_receive_items = []
# evt = threading.Event()


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
        # global on_receive_items
        print("Listener onreceived")
        print("MATTHEW is awesome!!!")
        print(f"{payload}")

        # TODO: on_receive response
        # on_receive_items.append((topic, payload, attributes))
        # evt.set()
        # evt.clear()
        #self.tm_socket.send()

        return UStatus(code=UCode.OK, message="all good") 
    
listener: UListener = SocketUListener()
    


def serialize_protobuf_to_base64(obj: Any):
    return base64.b64encode(obj.SerializeToString()).decode('ASCII')


class TestAgent:
    def __init__(self, ip_addr: str, port: int, utransport: UTransport) -> None:
        """
        The test server that the Test Agent will connect to
        Idea: acts as validator to validate data sent in ulink-socket-xxx

        """

        self.utransport: SocketUTransport = utransport

        self.connections : Dict[str, str] = defaultdict(str)
        self.port_to_client : Dict[str, socket.socket] = defaultdict(None)

        self.possible_received_protobufs = [UMessage()]

        self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.clientsocket.connect((ip_addr, port))  

        thread = threading.Thread(target=self.receive_from_tm)
        thread.start()



    def receive_from_tm(self):
        """
        Will always be receiving for clientsocket TA connected to current TM 
        """
        msg_len: int = 32767
        while True:
            recv_data: bytes = self.clientsocket.recv(msg_len)
            
            if recv_data == b"":
                continue

            json_str: str = recv_data.decode()

            json_msg: Dict[str, str] = json.loads(json_str)
            print("json_msg", json_msg)

            action: str = json_msg["action"]
            umsg_base64: str = json_msg["message"]
            protobuf_serialized_data: bytes = base64.b64decode(umsg_base64)
            

            # unpack protobuf
            response_proto: Any = None
            
            for proto in self.possible_received_protobufs:
                try:
                    proto.ParseFromString(protobuf_serialized_data)
                    response_proto = proto
                    print("here:", proto)
                except Exception as err:
                    pass
            print("response_proto:", response_proto)

            if action == "send":
                self.utransport.send(response_proto.source, response_proto.payload, response_proto.attributes)
            elif action == "registerlistener":
                self.utransport.register_listener(response_proto.source, listener)

            # NEED TO HANDLE the message
            if isinstance(response_proto, UMessage):
                print(response_proto)
                response = UStatus(code=UCode.OK, message="OK") 
                self.send(response)
            elif isinstance(response_proto, UStatus):
                print(f"Received UStatus Message: {response_proto}")
            else:
                raise Exception("ERROR: Received message type that's not UMessage nor UStatus.")  
            
    def __send_to_server(self, message: bytes):
        self.clientsocket.send(message)

    @dispatch(UUri, UPayload, UAttributes)
    def send(self, topic: UUri, payload: UPayload, attributes: UAttributes):
        """
        Sends data to Test Agent parameters (action/command and complete Umessage)
        """
        umsg: UMessage = UMessage(source=topic, attributes=attributes, payload=payload)

        #Creates the JSON message
        json_message = {
            "action": "send",
            "message": serialize_protobuf_to_base64(umsg)
        }

        # Converts a dictionary/map -> JSON string
        json_message_str: str = json.dumps(json_message)

         # Sends data over socket in bytes --> Converts JSON string to bytes
        message: bytes = str.encode(json_message_str)
        
        self.__send_to_server(message)

    @dispatch(UStatus)
    def send(self, status: UStatus):
        """
        Sends data to Test Agent parameters (action/command and complete Umessage)
        """

        print(f"UStatus: {status}")
        # create the Json message
        json_message = {
            "action": "uStatus",
            "message": serialize_protobuf_to_base64(status)
        }

        # Converts a dictionary/map -> JSON string
        json_message_str: str = json.dumps(json_message)

        print("sending", json_message)

        # Sends data over socket in bytes --> Converts JSON string to bytes
        message: bytes = str.encode(json_message_str)
        
        self.__send_to_server(message)

    def send_to_TM(self, json_message_str: str):
        message: bytes = str.encode(json_message_str)   # send this to socket in bytes
        
        self.__send_to_server(message)

    def __send_to_client(self, client: socket.socket, json_message: Dict[str, str]):
        json_message_str: str = json.dumps(json_message)
        message: bytes = str.encode(json_message_str)   # send this to socket in bytes
        client.send(message)

    def __send_json_msg_to_TM(self, command: str, umsg: UMessage):
        # Sends to Test Agent
        json_message = {
            "action": command,
            "message": serialize_protobuf_to_base64(umsg)
        }

        self.__send_to_client(self.clientsocket, json_message)

       
    def on_receive_command_TA_to_TM(self, command: str,  topic: UUri, payload: UPayload, attributes: UAttributes):
        # Sends to Test Manager
        umsg: UMessage = UMessage(source=topic, attributes=attributes, payload=payload)
        self.__send_json_msg_to_TM(command, umsg)


    def register_listener(self):
        """
        sends data to TA params (action/command and UURi Umessage)
        """
        pass

    def unregister_listener(self, client_port: int):
        """
        sends data to TA params (action/command and UURi Umessage)
        """
        
        pass

    def ustatus(self):
        """
        sends Ustatus protobuf
        """
        pass

uri: str = "/body.access//door.front_left#Door"

def build_cloud_event():
    return CloudEvent(spec_version="1.0", source="https://example.com", id="HARTLEY IS THE BEST")

def build_upayload():
    any_obj = Any()
    any_obj.Pack(build_cloud_event())
    return UPayload(format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF, value=any_obj.SerializeToString())

def build_uattributes():
    return UAttributesBuilder.publish(UPriority.UPRIORITY_CS4).build()


# def process_on_receive(agent):
#     while True:
#         print("MADe it inside")
#         evt.wait()
#         if len(on_receive_items) > 0:
#             print("item to send...")
#             for on_rec_item in on_receive_items:
#                 agent.on_receive_command_TA_to_TM("on_receive", on_rec_item[0], on_rec_item[1], on_rec_item[2])



if __name__ == "__main__":
    socket_utransport = SocketUTransport("127.0.0.1", 44444)
    agent = TestAgent("127.0.0.5", 12345, socket_utransport)

    # thread = Thread(target = process_on_receive, args = (agent,))
    # thread.start()
    #thread.join()

    topic = LongUriSerializer().deserialize(uri)
    payload: UPayload = build_upayload()
    attributes: UAttributes = build_uattributes()


    agent.send_to_TM(json.dumps({'SDK_name': "java"}))