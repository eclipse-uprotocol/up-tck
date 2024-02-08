import time
from subprocess import Popen
from multiprocessing import Pool

dispatcher_command = 'python ./dispatcher/dispatcher.py'
test_manager_command = 'python ./examples/tck_interoperability/test_socket_tm.py'
test_agent_command = 'python ./examples/tck_interoperability/test_socket_ta.py'

def run_process(file_name: str):
    Popen("python " + file_name, shell=True)


# Popen(dispatcher_command, shell=True)
# time.sleep(1)
# Popen(test_manager_command, shell=True)
# time.sleep(1)
# Popen(test_agent_command, shell=True)

if __name__ == '__main__':
    with Pool(3) as p:
        p.map(run_process, ["./dispatcher/dispatcher.py", "./examples/tck_interoperability/test_socket_tm.py", "./examples/tck_interoperability/test_socket_ta.py"])