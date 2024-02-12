from behave import when, then, given
from behave.runner import Context
from up_client_socket_python.transport_layer import TransportLayer
import sys
sys.path.append('../../../python/test_manager')
from test_manager import testmanager
from uprotocol.transport.ulistener import UListener
from uprotocol.proto.uattributes_pb2 import UAttributes
from uprotocol.proto.uri_pb2 import UUri
from uprotocol.proto.ustatus_pb2 import UStatus
from uprotocol.proto.ustatus_pb2 import UStatus, UCode
from uprotocol.proto.upayload_pb2 import UPayload


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

        print.info(f"{payload}")

        return UStatus(code=UCode.OK, message="all good")

@given(u'“{sdk_name}” creates uuri data to register a listener')
def step_impl(context, sdk_name:str):
    context.logger.info("Inside create register listener data")
    context.register_json_array = {}
    context.ue = sdk_name


@given(u'sets uuri "{key}" to "{value}"')
def step_impl(context: Context, key: str, value: str):
    context.logger.info("RegisterListener json data: Key is " + str(key) + " value is " + str(value))
    if key not in context.register_json_array:
        context.register_json_array[key] = [value]


@given(u'sends "{command}" request')
def step_impl(context, command:str):
    listener: UListener = SocketUListener()
    transport = TransportLayer()
    transport.set_socket_config("127.0.0.1", 44444)
    context.tm = testmanager.SocketTestManager("127.0.0.5", 12345, transport)
    context.logger.info("Register listener " + str(context.register_json_array))
    def register_listener_handler():
        print("Register Listener handler")
    context.tm.receive_action_request(context.register_json_array,listener)


@when(u'“uE2” test agent creates send data')
def step_impl(context):
    context.logger.info("Inside")
    context.send_json_array = {}


@when(u'sets "{key}" to "{value}"')
def step_impl(context: Context, key: str, value: str):
    context.logger.info("Send Api json data: Key is " + str(key) + " value is " + str(value))
    if key not in context.send_json_array:
        context.send_json_array[key] = [value]
    context.logger.info("Inside")


@when(u'sends data')
def step_impl(context):
    context.logger.info("Send data " + str(context.send_json_array))


@then(u'uE1 receives the payload')
def step_impl(context):
    context.logger.info("Payload data ")
