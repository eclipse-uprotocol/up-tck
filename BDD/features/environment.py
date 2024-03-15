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

import subprocess
import sys
import time
from threading import Thread
from typing import Dict, List
import os
import git
from behave.runner import Context
from utils import loggerutils
import socket

from up_tck.test_manager.testmanager import SocketTestManager
from up_tck.test_agents.python_test_agent.testagent import SocketTestAgent
from up_tck.test_agents.python_test_agent.test_ta import SocketUListener
from up_tck.test_agents.python_test_agent.transport_layer import TransportLayer
from up_tck.up_client_socket_python.dispatcher.dispatcher import Dispatcher
from up_tck.python_utils.constants import TEST_MANAGER_ADDR

from uprotocol.proto.ustatus_pb2 import UStatus
from uprotocol.transport.ulistener import UListener

JAVA_TA_PATH = "/up_tck/test_agents/java_test_agent/target/tck-test-agent-java-jar-with-dependencies.jar"

def get_git_root():
    curr_path = os.getcwd()
    git_repo = git.Repo(curr_path, search_parent_directories=True)
    git_root = git_repo.git.rev_parse("--show-toplevel")
    return git_root


def create_file_path(filepath_from_root_repo: str) -> str:
    return get_git_root() + filepath_from_root_repo


def create_command(filepath_from_root_repo: str) -> List[str]:
    command: List[str] = []

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

    # create global json data storage
    context.initialized_data = {}

    # create global received response status storage
    sdk_to_status: Dict[str, UStatus] = {}
    context.sdk_to_status = sdk_to_status
    
    dispatcher = Dispatcher()
    thread = Thread(target=dispatcher.listen_for_client_connections)
    thread.start()
    context.dispatcher = dispatcher

    context.logger.info("Created Dispatcher...")
    time.sleep(5)

    test_manager = SocketTestManager("127.0.0.5", 12345)
    thread = Thread(target=test_manager.listen_for_client_connections)
    thread.start()
    context.tm = test_manager

    context.logger.info("Created Test Manager...")

    transport = TransportLayer()
    context.test_agent_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    context.test_agent_socket.connect(TEST_MANAGER_ADDR)
    listener: UListener = SocketUListener(context.test_agent_socket)
    agent = SocketTestAgent(context.test_agent_socket, transport, listener)
    agent.send_to_TM({'SDK_name': "python"})

    command = create_command(JAVA_TA_PATH)
    process: subprocess.Popen = create_subprocess(command)
    context.java_ta_process = process

    context.logger.info("Created All Test Agents...")


def after_all(context: Context):
    # bandaid on race condition between onReceive mesg Test vs. closing sockets
    time.sleep(3)

    # Closes sockets and releases memory
    test_manager: SocketTestManager = context.tm
    dispatcher: Dispatcher = context.dispatcher

    test_manager.close_ta_socket("python")
    test_manager.close_ta_socket("java")

    test_manager.close()
    dispatcher.close()
    context.test_agent_socket.close()

    try:
        context.java_ta_process.kill()
        context.java_ta_process.communicate()
        pass
    except Exception as e:
        context.logger.error(e)