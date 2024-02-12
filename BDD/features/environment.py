from utils import loggerutils
import subprocess
import os

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
        "../python/examples/tck_interoperability/test_socket_tm.py",
        "out/artifacts/java_test_agent_jar/java_test_agent.jar"
    ]

    for script_path in script_paths:
        if script_path.endswith('.jar'):
            subprocess.Popen(['gnome-terminal', '--', 'java', 'jar', script_path])
        else:
            subprocess.Popen(['gnome-terminal', '--', 'python3', script_path])

    #context.logger.info("Running BDD Framework version " + __version__)

    # if not (('venv' in sys.prefix) or (sys.prefix != sys.base_prefix)):
    #     context.logger.error("System is not running inside virtual "
    #                          "environment. Please start with virtual "
    #                          "environment (venv) enabled.")
    #     quit()