import time
import socket
from abc import ABC
from threading import Thread

from utils import loggerutils
import subprocess
import os
import sys
sys.path.append('../../python/')
from python.test_manager import testmanager
# sys.path.append('../../python/up_client_socket_python')
from python.up_client_socket_python import transport_layer as tl
from python.test_agent import testagent as testagent
from uprotocol.transport.ulistener import UListener




def before_all(context):
    """Set up test environment
    Create driver based on the desired capabilities provided.
    Valid desired capabilities can be 'firefox', 'chrome' or 'ie'.
    For adding new drivers add a new static method in DriverFactory class.

    :param context: Holds contextual information during the running of tests
    :return: None
    """

    loggerutils.setup_logging()
    loggerutils.setup_formatted_logging(context)
    path = os.getcwd()
    script_paths = [
        "../python/dispatcher/dispatcher.py",
       # "../python/examples/tck_interoperability/test_socket_tm.py",
       # "../python/examples/tck_interoperability/test_socket_ta.py"
        #"../java/java_test_agent/out/artifacts/java_test_agent_jar/uprotocol-tck.jar"
    ]
    processes = []

    for script_path in script_paths:
        if script_path.endswith('.jar'):
            #subprocess.Popen(['gnome-terminal', '--', 'java', 'jar', script_path])
            command = ['gnome-terminal', '--', 'java', '-jar', os.path.abspath(script_path)]
        else:
            # subprocess.Popen(['gnome-terminal', '--', f'python3 {os.path.abspath(script_path)}; while true; do sleep 1; done'])
            command = ['gnome-terminal', '--', 'python3', os.path.abspath(script_path)]

        process = subprocess.Popen(command)
        processes.append(process)

    # Wait for all terminal windows to close
    for process in processes:
        process.wait()
    time.sleep(2)
    transport = tl.TransportLayer()
    transport.set_socket_config("127.0.0.1", 44444)
    time.sleep(2)
    context.tm = testmanager.SocketTestManager("127.0.0.5", 12345, transport)
    thread = Thread(target=context.tm.listen_for_client_connections)
    thread.start()

    time.sleep(5)
    #script_path = "../python/examples/tck_interoperability/test_socket_ta.py"
    #subprocess.Popen(['gnome-terminal', '--', 'python3', os.path.abspath(script_path)])
    script_path = "../java/java_test_agent/out/artifacts/java_test_agent_jar/uprotocol-tck.jar"
    subprocess.Popen(['gnome-terminal', '--', 'java', '-jar', os.path.abspath(script_path)])
    time.sleep(5)


    #context.logger.info("Running BDD Framework version " + __version__)

    # if not (('venv' in sys.prefix) or (sys.prefix != sys.base_prefix)):
    #     context.logger.error("System is not running inside virtual "
    #                          "environment. Please start with virtual "
    #                          "environment (venv) enabled.")
    #     quit()