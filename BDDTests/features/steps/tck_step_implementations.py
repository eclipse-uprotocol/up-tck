import base64

from google.protobuf import any_pb2
from google.protobuf.any_pb2 import Any

from behave import when, then, given
from behave.runner import Context
import sys

sys.path.append('../../../python/test_manager')
from test_manager import testmanager

sys.path.append('../../../python/up_client_socket_python')
from up_client_socket_python import transport_layer as tl
from uprotocol.transport.ulistener import UListener
from uprotocol.proto.uattributes_pb2 import UAttributes
from uprotocol.proto.uri_pb2 import UUri
from uprotocol.proto.ustatus_pb2 import UStatus
from uprotocol.proto.ustatus_pb2 import UStatus, UCode
from uprotocol.proto.upayload_pb2 import UPayload
from uprotocol.proto.cloudevents_pb2 import CloudEvent


# transport = tl.TransportLayer()
# transport.set_socket_config("127.0.0.1", 44444)
# tm = testmanager.SocketTestManager("127.0.0.5", 12345, transport)

class SocketUListener(UListener):
    def __init__(self, sdk_name: str = "python") -> None:
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
        print("Listener onreceived")
        # logger.info("MATTHEW is awesome!!!")

        print(f"{payload}")

        return UStatus(code=UCode.OK, message="all good")


@given(u'“{sdk_name}” creates data for "{command}"')
@when(u'“{sdk_name}” creates data for "{command}"')
def step_impl(context, sdk_name: str, command: str):
    context.logger.info("Inside create register listener data")
    context.json_array = {}
    context.ue = sdk_name
    context.json_array['ue'] = [sdk_name]
    context.json_array['action'] = [command]


@given(u'sets "{key}" to "{value}"')
@when(u'sets "{key}" to "{value}"')
def step_impl(context: Context, key: str, value: str):
    context.logger.info("Json data: Key is " + str(key) + " value is " + str(value))
    if key not in context.json_array:
        context.json_array[key] = [value]


@given(u'sends "{command}" request')
@when(u'sends "{command}" request')
def step_impl(context, command: str):
    listener: UListener = SocketUListener()
    context.logger.info(f"Json request for {command} -> {str(context.json_array)}")
    context.tm.receive_action_request(context.json_array, listener)


@then(u'uE1 receives the payload')
def step_impl(context):
    context.logger.info("Payload data ")
