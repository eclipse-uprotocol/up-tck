import time
import socket
from abc import ABC
from threading import Thread
from typing import List

from utils import loggerutils
import subprocess
import os
import sys
from up_client_socket_python.utils.file_pathing_utils import get_git_root

# sys.path.append('../../python/test_manager')
from test_manager.testmanager import SocketTestManager

# sys.path.append('../../python/up_client_socket_python')
from up_client_socket_python.transport_layer import TransportLayer

SYS_PLATFORM_COMMAND_PREFIXES = {
    "win32": ["start"], #['start', '/min'],
    "linux": ['gnome-terminal', '--']
}

def create_file_path(filepath_from_root_repo: str) -> str:
    return get_git_root() + filepath_from_root_repo

def create_command(filepath_from_root_repo: str) -> List[str]:
    command: List[str] = []
    
    if sys.platform == "win32":
        command.append("start")
    elif sys.platform == "linux" or sys.platform == "linux2":
        command.append('gnome-terminal')
        command.append('--')
    else:
        raise Exception("only handle Windows and Linux commands for now")
    
    if filepath_from_root_repo.endswith('.jar'):
        command.append("java")
        command.append("-jar")
    elif filepath_from_root_repo.endswith('.py'):
        if sys.platform == "win32":
            command.append("python")
        elif sys.platform == "linux" or sys.platform == "linux2":
            command.append("python3")
    else:
        raise Exception("only accept .jar and .py files")
    
    abs_file_path: str = create_file_path(filepath_from_root_repo)
    command.append(abs_file_path)
    
    return command


def create_subprocess(command: List[str]) -> subprocess.Popen:
    process = subprocess.Popen(command, shell=True)
    return process


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
        
    command = create_command("/python/dispatcher/dispatcher.py")
    process: subprocess.Popen = create_subprocess(command)
    
    print("created Dis")
    time.sleep(2)


    transport = TransportLayer()
    transport.set_socket_config("127.0.0.1", 44444)
    test_manager = SocketTestManager("127.0.0.5", 12345, transport)
    thread = Thread(target=test_manager.listen_for_client_connections)
    thread.start()
    context.tm = test_manager
    
    print("created TM")
    
    command = create_command("/python/examples/tck_interoperability/test_socket_ta.py")
    process: subprocess.Popen = create_subprocess(command)
    process.wait()
    
    
    command = create_command("/python/examples/tck_interoperability/test_socket_ta.py")
    process: subprocess.Popen = create_subprocess(command)
    process.wait()
    
    command = create_command("/java/java_test_agent/out/artifacts/java_test_agent_jar/uprotocol-tck.jar")
    process: subprocess.Popen = create_subprocess(command)
    process.wait()

    
    print("post wait")
    print("env tm connections", test_manager.sdk_to_test_agent_socket.keys())
    # while not test_manager.has_sdk_connection("python"):
    #     continue
    print("env tm connections", test_manager.sdk_to_test_agent_socket.keys())
    
    '''

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

        print(command)
        process = subprocess.Popen(command, shell=True)
        print("hi")
        processes.append(process)

    # Wait for all terminal windows to close
    for process in processes:
        process.wait()
    time.sleep(2)
    transport = TransportLayer()
    transport.set_socket_config("127.0.0.1", 44444)
    time.sleep(2)
    context.tm = SocketTestManager("127.0.0.5", 12345, transport)
    thread = Thread(target=context.tm.listen_for_client_connections)
    thread.start()

    time.sleep(5)
    #script_path = "../python/examples/tck_interoperability/test_socket_ta.py"
    #subprocess.Popen(['gnome-terminal', '--', 'python3', os.path.abspath(script_path)])
    script_path = "../java/java_test_agent/out/artifacts/java_test_agent_jar/uprotocol-tck.jar"
    subprocess.Popen(['gnome-terminal', '--', 'java', '-jar', os.path.abspath(script_path)])
    time.sleep(5)

    '''
    #context.logger.info("Running BDD Framework version " + __version__)

    # if not (('venv' in sys.prefix) or (sys.prefix != sys.base_prefix)):
    #     context.logger.error("System is not running inside virtual "
    #                          "environment. Please start with virtual "
    #                          "environment (venv) enabled.")
    #     quit()

'''
if __name__ == "__main__":
    command = create_command("/python/dispatcher/dispatcher.py")
    process: subprocess.Popen = create_subprocess(command)
    print(process.wait())
    
    transport = TransportLayer()
    transport.set_socket_config("127.0.0.1", 44444)
    test_manager = SocketTestManager("127.0.0.5", 12345, transport)
    thread = Thread(target=test_manager.listen_for_client_connections)
    thread.start()
    
    command = create_command("/python/examples/tck_interoperability/test_socket_ta.py")
    process: subprocess.Popen = create_subprocess(command)
    process.wait()
    
    print("post wait")'''