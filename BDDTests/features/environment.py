from utils.loggerutils import setup_logging, setup_formatted_logging
import subprocess
import os
import sys
from abc import ABC, abstractclassmethod

from up_client_socket_python.utils.file_pathing_utils import get_git_root

def before_all(context):
    """Set up test environment
    Create driver based on the desired capabilities provided.
    Valid desired capabilities can be 'firefox', 'chrome' or 'ie'.
    For adding new drivers add a new static method in DriverFactory class.

    :param context: Holds contextual information during the running of tests
    :return: None
    """

    setup_logging()
    setup_formatted_logging(context)

    path = os.getcwd()
    script_paths = [
        "../python/dispatcher/dispatcher.py",
        "../python/examples/tck_interoperability/test_socket_tm.py",
        "../python/examples/tck_interoperability/test_socket_ta.py"
        #"../java/java_test_agent/out/artifacts/java_test_agent_jar/uprotocol-tck.jar"
    ]
    processes = []

    for script_path in script_paths:
        if script_path.endswith('.jar'):
            #subprocess.Popen(['gnome-terminal', '--', 'java', 'jar', script_path])
            if sys.platform == "win32":
                command = ['start', '/min', 'java', '-jar', os.path.abspath(script_path)]
            else:
                command = ['gnome-terminal', '--', 'java', '-jar', os.path.abspath(script_path)]  
        else:
            # subprocess.Popen(['gnome-terminal', '--', f'python3 {os.path.abspath(script_path)}; while true; do sleep 1; done'])
            if sys.platform == "win32":
                command = ['start', '/min', 'python', os.path.abspath(script_path)]
            else:
                command = ['gnome-terminal', '--', 'python3', os.path.abspath(script_path)]

        print(command)
        process = subprocess.Popen(command, shell=True)
        print("hi")
        processes.append(process)

    # Wait for all terminal windows to close
    for process in processes:
        process.wait()

    #context.logger.info("Running BDD Framework version " + __version__)

    # if not (('venv' in sys.prefix) or (sys.prefix != sys.base_prefix)):
    #     context.logger.error("System is not running inside virtual "
    #                          "environment. Please start with virtual "
    #                          "environment (venv) enabled.")
    #     quit()

# class IRunScripts(ABC):
#     @abstractclassmethod
#     def before_all(self, context):
#         pass

# class RunWindowsTestScript(IRunScripts):
    
#     @staticmethod
#     def before_all(context):
        
#         print("get_git_root():", get_git_root())
#         print(os.path.abspath(get_git_root() + "\python\examples\\tck_interoperability"))
#         p = subprocess.Popen("demo_windows.bat", cwd=os.path.abspath(get_git_root() + "\python\examples\\tck_interoperability"), shell=True)

#         stdout, stderr = p.communicate()

            
# if sys.platform == "win32":
#     RunWindowsTestScript.before_all(None)