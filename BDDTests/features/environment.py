import time
from threading import Thread

from utils import loggerutils
import subprocess
import os
import sys
from abc import ABC, abstractclassmethod
from up_client_socket_python.utils.file_pathing_utils import get_git_root

# sys.path.append('../../python/test_manager')
from test_manager.testmanager import SocketTestManager

# sys.path.append('../../python/up_client_socket_python')
from up_client_socket_python.transport_layer import TransportLayer

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
    
    #set up dispatcher
    print("prerunning dispatcher")
    command = ['start', '/min', 'python', get_git_root() + "/python/dispatcher/dispatcher.py"]
    process = subprocess.Popen(command, shell=True)
    processes.append(process)
    print("postrunning dispatcher")
    time.sleep(5)
    # set up TM
    transport = TransportLayer()
    transport.set_socket_config("127.0.0.1", 44444)
    time.sleep(5)
    print("prerunning testmanager")
    context.tm = SocketTestManager("127.0.0.5", 12345, transport)
    thread = Thread(target = context.tm.listen_for_client_connections)  
    thread.start()
    print("postrunning testmanager")
    time.sleep(5)
    
    # setup test agent
    print("prerunning test agent")
    command = ['start', '/min', 'python', get_git_root() + "/python/examples/tck_interoperability/test_socket_ta.py"]
    process = subprocess.Popen(command, shell=True)
    processes.append(process)
    print("postrunning test agent")
    time.sleep(5)

    '''
    if sys.platform == "win32":
        paths_from_root_repo = [
            "/python/dispatcher/dispatcher.py",
            # "/python/examples/tck_interoperability/test_socket_tm.py",
            # "/python/examples/tck_interoperability/test_socket_ta.py"
            #"../java/java_test_agent/out/artifacts/java_test_agent_jar/uprotocol-tck.jar"
        ]
        
        for script_path in paths_from_root_repo:
            if script_path.endswith('.jar'):
                command = ['gnome-terminal', '--', 'java', '-jar', os.path.abspath(script_path)]  
            else:
                # start /min python ../../dispatcher/dispatcher.py
                command = ['start', '/min', 'python', get_git_root() + script_path]

            print("RunWindowsTestScript")
            print(command)
            process = subprocess.Popen(command, shell=True)
            processes.append(process)
            time.sleep(1)
    else:
        for script_path in script_paths:
            if script_path.endswith('.jar'):
                #subprocess.Popen(['gnome-terminal', '--', 'java', 'jar', script_path])
                command = ['gnome-terminal', '--', 'java', '-jar', os.path.abspath(script_path)]  
            else:
                # subprocess.Popen(['gnome-terminal', '--', f'python3 {os.path.abspath(script_path)}; while true; do sleep 1; done'])
                command = ['gnome-terminal', '--', 'python3', os.path.abspath(script_path)]

            print(command)
            process = subprocess.Popen(command)
            processes.append(process)
        '''

    # Wait for all terminal windows to close
    for process in processes:
        process.wait()




    #context.logger.info("Running BDD Framework version " + __version__)

    # if not (('venv' in sys.prefix) or (sys.prefix != sys.base_prefix)):
    #     context.logger.error("System is not running inside virtual "
    #                          "environment. Please start with virtual "
    #                          "environment (venv) enabled.")
    #     quit()

class IRunScripts(ABC):
    @abstractclassmethod
    def before_all(self, context):
        pass

class RunWindowsTestScript(IRunScripts):
    
    @staticmethod
    def before_all(context):
        
        paths_from_root_repo = [
            "/python/dispatcher/dispatcher.py",
            # "../python/examples/tck_interoperability/test_socket_tm.py",
            # "../python/examples/tck_interoperability/test_socket_ta.py"
            #"../java/java_test_agent/out/artifacts/java_test_agent_jar/uprotocol-tck.jar"
        ]
        processes = []

        for script_path in paths_from_root_repo:
            if script_path.endswith('.jar'):
                #subprocess.Popen(['gnome-terminal', '--', 'java', 'jar', script_path])
                command = ['gnome-terminal', '--', 'java', '-jar', os.path.abspath(script_path)]  
            else:
                # subprocess.Popen(['gnome-terminal', '--', f'python3 {os.path.abspath(script_path)}; while true; do sleep 1; done'])
                # start /min python ../../dispatcher/dispatcher.py

                command = ['start', '/min', 'python', get_git_root() + script_path]

            print("RunWindowsTestScript")
            print(command)
            process = subprocess.Popen(command, shell=True)
            processes.append(process)

        # Wait for all terminal windows to close
        for process in processes:
            process.wait()

        transport = TransportLayer()
        transport.set_socket_config("127.0.0.1", 44444)
        time.sleep(2)
        context.tm = SocketTestManager("127.0.0.5", 12345, transport)
    

            
# if sys.platform == "win32":
#     RunWindowsTestScript.before_all(None)