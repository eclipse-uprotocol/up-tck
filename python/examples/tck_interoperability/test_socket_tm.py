import time
from threading import Thread
from typing import Dict, List
from google.protobuf.any_pb2 import Any
from concurrent.futures import ThreadPoolExecutor

from uprotocol.proto.uattributes_pb2 import UAttributes
from uprotocol.proto.uri_pb2 import UUri
from uprotocol.proto.ustatus_pb2 import UStatus
from uprotocol.proto.ustatus_pb2 import UStatus, UCode
from uprotocol.transport.ulistener import UListener

from uprotocol.proto.cloudevents_pb2 import CloudEvent
from uprotocol.proto.upayload_pb2 import UPayload, UPayloadFormat
from uprotocol.proto.uattributes_pb2 import UPriority
from uprotocol.transport.builder.uattributesbuilder import UAttributesBuilder
from uprotocol.uri.serializer.longuriserializer import LongUriSerializer
from up_client_socket_python.transport_layer import TransportLayer
from test_manager.testmanager import SocketTestManager

from multipledispatch import dispatch
import logging 
import re


logging.basicConfig(format='%(asctime)s %(message)s')
# Create logger
logger = logging.getLogger('simple_example')
logger.setLevel(logging.DEBUG)


class SocketUListener(UListener):
    def __init__(self, sdk_name: str ="python") -> None:
        pass

    def on_receive(self, topic: UUri, payload: UPayload, attributes: UAttributes) -> UStatus:
        """
        ULIstener is for each TA
        ADD SDK NAME in constructor or something
        
        Method called to handle/process events.<br><br>
        @param topic: Topic the underlying source of the message.
        @param payload: Payload of the message.
        @param attributes: Transportation attributes.
        @return Returns an Ack every time a message is received and processed.
        """
        logger.info("Listener onreceived")
        # logger.info("MATTHEW is awesome!!!")

        logger.info(f"{payload}")

        return UStatus(code=UCode.OK, message="all good") 

 
def get_progress_commands():
    with open('test_runner.txt', 'r') as file:
        input_lines = []
        for line in file:
            line = line.strip()
            if line != "" and (len(line) > 0 and line[0] != "#"):
                input_lines.append(line)
    
    return input_lines

def get_uri_value(uri_line: str) -> str:
    if not("uri" in uri_line or "URI" in uri_line):
        raise Exception("Need to have URI assignment following register_listener_command()!")

    words_wrapped_between_quotes: List[str] = re.findall('"([^"]*)"', uri_line)
    
    if len(words_wrapped_between_quotes) == 0:
        raise Exception("Didn't find URI string wrapped in quotes \" \"")
    elif len(words_wrapped_between_quotes) != 1:
        raise Exception("Found more than one string wrapped quotes \" \"")

    uri: str = words_wrapped_between_quotes[0]
    return uri

def print_action(action: str):
    print(f">>>>> {action.upper()} >>>>>")


def get_next_string(token: str) -> str:
    words_wrapped_between_quotes: List[str] = re.findall('"([^"]*)"', token)
    return words_wrapped_between_quotes[0]

def check_variable_initialization(parameters: dict, param: str):
    if param not in parameters:
        raise Exception(f"{param} parameter not initialized")
        
def parse_param(parameters: dict, progress_commands: List[str], step_i: int) -> int:
    """
    <param> := <variable> = "string" | <variable> = { <param-list> }
    """
    # RETURNS STEP Index!!
    
    # ex: URI = "/body.access//door.front_left#Door" | UPAYLOAD = {
    command_ordered_tokens = progress_commands[step_i].split(" ")  
    
    # get variable
    variable_id: str = command_ordered_tokens[0].upper()
    
    assigned_value: str = command_ordered_tokens[-1]
    
    # check which branch to go: " " or {<param-list>} 
    # check first character of next token
    token: str = progress_commands[step_i]
    if assigned_value == "{":
        step_i += 1

        # all params parsed in recursion should be saved in Dict parameters
        step_i = parse_param_list(parameters, progress_commands, step_i)
        
        # skip "}"
        step_i += 1
    elif assigned_value[-1][0] == "\"":
        value = get_next_string(token)
        
        # save value
        parameters[variable_id] = value
        step_i += 1
    else:
        raise Exception("Only accept \"strings\" wrapped in quotes OR inner parameter brackets \{ \}")
        
    # put arguments into variable
    if variable_id == "UURI":
        check_variable_initialization(parameters, "UURI")
        
        topic: UUri = LongUriSerializer().deserialize(parameters["UURI"])
        parameters["UURI"] = topic
        
    elif variable_id == "UPAYLOAD":   
        check_variable_initialization(parameters, "UPAYLOAD")

        
        payload: UPayload = build_upayload(parameters["CLOUDEVENT"])

        parameters["UPAYLOAD"] = payload
    elif variable_id == "CLOUDEVENT":   
        check_variable_initialization(parameters, "ID")
        check_variable_initialization(parameters, "SOURCE")
        cloud_event: CloudEvent = build_cloud_event(parameters["ID"], parameters["SOURCE"])

        parameters["CLOUDEVENT"] = cloud_event
    elif variable_id == "UATTRIBUTES":   
        
        if parameters["UATTRIBUTES"] == "5":
            parameters["UATTRIBUTES"] = build_uattributes()
        else:
            raise Exception("Cant handling other UAttributes yet")

    return step_i
    
def parse_param_list(parameters: dict, progress_commands: List[str], step_i: int) -> int:
    # RETURNS STEP Index!!

    # Checks if more arguments created
    while step_i < len(progress_commands) and progress_commands[step_i] != "}":
        step_i = parse_param(parameters, progress_commands, step_i)
    
    if step_i == len(progress_commands) and progress_commands[step_i - 1] != "}":
        raise Exception(" Need to end block with }")
    
    return step_i
 
def handle_progress_commands(progress_commands: List[str], tm: SocketTestManager):
    step_i = 0
    while step_i < len(progress_commands):
        # eg: "java_test_agent connect_to test_manager", "test_manager register_listener java_test_agent"
        # formula: <actor> <action/verb> <receiver>
        command_line = progress_commands[step_i]  
        command = command_line.split(" ")
        action = command[1]
        
        if action == "connect_to":
            print_action(action)
            ta_enactor: str = command[0]
            tm_receiver: str = command[2]
            
            sdk_name: str = ta_enactor.split("_")[0]
            
            print("waiting for", sdk_name, "...")            
            while not tm.has_sdk_connection(sdk_name):
                time.sleep(1)
                continue
            print("got connection from", sdk_name)
            
            step_i += 1
            
        elif action == "register_listener_command":
            print_action(action)

            # get ta's sdk type
            ta_receiver: str = command[2]
            sdk: str = ta_receiver.split("_")[0]
            
            if not tm.has_sdk_connection(sdk_name):
                raise Exception(f"{sdk} Test Agent was never connected!")
            step_i += 1
            
            # enter params bracket "{"
            step_i += 1
            
            parameters = dict()
            step_i = parse_param_list(parameters, progress_commands, step_i)
            
            # exit params bracket "}"
            step_i += 1
            
            check_variable_initialization(parameters, "UURI")


            register_listener_status: UStatus = tm.register_listener_command(sdk, "registerlistener", parameters["UURI"], listener)
            

        elif action == "send_command":
            print_action(action)

            # get ta's sdk type
            ta_receiver: str = command[2]
            sdk: str = ta_receiver.split("_")[0]
            
            if not tm.has_sdk_connection(sdk_name):
                raise Exception(f"{sdk} Test Agent was never connected!")
            step_i += 1
            
            # enter params bracket "{"
            step_i += 1
            
            parameters = dict()
            step_i = parse_param_list(parameters, progress_commands, step_i)
            
            # exit params bracket "}"
            step_i += 1
            
            check_variable_initialization(parameters, "UURI")
            check_variable_initialization(parameters, "UPAYLOAD")
            check_variable_initialization(parameters, "UATTRIBUTES")

            send_status: UStatus = tm.send_command(sdk, "send", parameters["UURI"], parameters["UPAYLOAD"], parameters["UATTRIBUTES"])
            
            
        elif action == "responds_ustatus":
            print_action(action)

            enactor: str = command[0]
            receiver: str = command[2]
            
            if receiver == "test_manager":
                if register_listener_status is not None:
                    print("register_listener_status:", register_listener_status)
                    register_listener_status = None
                elif send_status is not None:
                    print("send_status:", send_status)
                    send_status = None
                else:
                    raise Exception("did not receive any Status!")
                
            else:
                raise Exception("Only handles Test Manager for receiving data!")
            
            step_i += 1
        
        else:
            raise Exception(f"Action {action} not handle!")


transport = TransportLayer()
transport.set_socket_config("127.0.0.1", 44444)
manager = SocketTestManager("127.0.0.5", 12345, transport)

uri: str = "/body.access//door.front_left#Door"

def build_cloud_event(id: str, source: str):
    return CloudEvent(spec_version="1.0", source=source, id="I am " + id)

@dispatch(str, str)
def build_upayload(id: str, source: str):
    any_obj = Any()
    any_obj.Pack(build_cloud_event(id, source))
    return UPayload(format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF, value=any_obj.SerializeToString())

@dispatch(CloudEvent)
def build_upayload(cloud_event: CloudEvent):
    any_obj = Any()
    any_obj.Pack(cloud_event)
    return UPayload(format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF, value=any_obj.SerializeToString())


def build_uattributes():
    return UAttributesBuilder.publish(UPriority.UPRIORITY_CS4).build()

listener: UListener = SocketUListener()
# with ThreadPoolExecutor(max_workers=1) as executor:
#     # submit the task
#     future = executor.submit(manager.listen_for_client_connections)
thread = Thread(target = manager.listen_for_client_connections)  
thread.start()

print("----------------------------------------")
print("-             Running                  -")
print("-             Test Manager             -")
print("----------------------------------------")



handle_progress_commands(get_progress_commands(), manager)    
'''
while True:
    sdk: str = input("Enter SDK Language[java/python]: ")
    sdk = sdk.strip()
    command_name = input("Enter Command Name[send/registerlistener]: ")
    command_name = command_name.strip().lower()

    topic = LongUriSerializer().deserialize(uri)
    payload: UPayload = build_upayload(sdk)
    attributes: UAttributes = build_uattributes()

    if command_name == "send": 
        print("SEND COMMAND")
        status: UStatus = manager.send_command(sdk, command_name, topic, payload, attributes)
    elif command_name == "registerlistener":
        print("RegisterListener COMMAND")

        status: UStatus = manager.register_listener_command(sdk, command_name, topic, listener)
    else:
        print("in exception!")
        continue
    print("received status:", status)
    print("---------------")
    time.sleep(1)
'''
