# -------------------------------------------------------------------------
#
# Copyright (c) 2024 General Motors GTO LLC
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
# SPDX-FileType: SOURCE
# SPDX-FileCopyrightText: 2024 General Motors GTO LLC
# SPDX-License-Identifier: Apache-2.0
#
# -------------------------------------------------------------------------

import time
from threading import Thread
from typing import List
from utils import loggerutils
import subprocess
import sys
from behave.runner import Context

from up_client_socket_python.utils.file_pathing_utils import get_git_root
from up_client_socket_python.transport_layer import TransportLayer
from test_manager.testmanager import SocketTestManager

def create_file_path(filepath_from_root_repo: str) -> str:
    return get_git_root() + filepath_from_root_repo

def create_command(filepath_from_root_repo: str) -> List[str]:
    command: List[str] = []
    
    if sys.platform == "win32":
        # command.append("start")
        pass
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
    if sys.platform == "win32":
        process = subprocess.Popen(command, shell=True)
    elif sys.platform == "linux" or sys.platform == "linux2":
        process = subprocess.Popen(command)
    else:
        raise Exception("only handle Windows and Linux commands for now")
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

    context.logger.info("Created Dispatcher...")
    time.sleep(5)


    transport = TransportLayer()
    transport.set_socket_config("127.0.0.1", 44444)
    test_manager = SocketTestManager("127.0.0.5", 12345, transport)
    thread = Thread(target=test_manager.listen_for_client_connections)
    thread.start()
    context.tm = test_manager

    context.logger.info("Created Test Manager...")
    
    command = create_command("/python/examples/tck_interoperability/test_socket_ta.py")
    process: subprocess.Popen = create_subprocess(command)
    # process.wait()
    context.python_ta_process = process

    command = create_command("/java/java_test_agent/target/JavaTestAgent-jar-with-dependencies.jar")
    process: subprocess.Popen = create_subprocess(command)
    # process.wait()
    context.java_ta_process = process

    context.logger.info("Created All Test Agents...")

def after_all(context: Context):
    # Closes sockets and releases memory
    test_manager: SocketTestManager = context.tm
    
    test_manager.close_ta_socket("python")
    test_manager.close_ta_socket("java")

    test_manager.close()
    
    try:
        
        # The os.setsid() is passed in the argument preexec_fn so
        # it's run after the fork() and before  exec() to run the shell.


        # print(os.getpid())
        # print(context.java_ta_process.pid)

        # print(context.python_ta_process.pid)
        # print(context.java_ta_process.terminate())
        # print(context.java_ta_process.wait())

        # subprocess.Popen("TASKKILL /F /PID {pid} /T".format(pid=context.java_ta_process.pid))
        # subprocess.Popen("TASKKILL /F /PID {pid} /T".format(pid=context.python_ta_process.pid))

        # os.killpg(os.getpid, signal.SIGTERM)  # Send the signal to all the process groups


        # pobj = psutil.Process(context.python_ta_process.pid)
        # print(pobj)
        # # list children & kill them
        # for c in pobj.children(recursive=True):
        #     c.kill()
        # pobj.kill()

        context.java_ta_process.kill()
        context.java_ta_process.communicate()
        context.python_ta_process.kill()
        context.python_ta_process.communicate()

        # pidvalue=context.java_ta_process.pid
        # print(context.java_ta_process)
        # subprocess.Popen('taskkill /F /T /PID %i' % pidvalue)
        
        # pidvalue=context.python_ta_process.pid
        # subprocess.Popen('taskkill /F /T /PID %i' % pidvalue)
        pass
    except Exception as e:
        context.logger.error(e)
