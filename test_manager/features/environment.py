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

import os
import subprocess
import sys
import time
from threading import Thread
from typing import List

import git
from behave import formatter
from behave.runner import Context

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from testmanager import TestManager
from utils import loggerutils

PYTHON_TA_PATH = "/test_agent/python/testagent.py"
JAVA_TA_PATH = "/test_agent/java/target/tck-test-agent-java-jar-with-dependencies.jar"
DISPATCHER_PATH = "/dispatcher/dispatcher.py"


def create_command(filepath_from_root_repo: str) -> List[str]:
    command: List[str] = []
    if sys.platform == "win32":
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
    command.append(os.path.abspath(os.path.dirname(os.getcwd()) + "/" + filepath_from_root_repo))
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
    context.on_receive_msg = {}
    context.on_receive_rpc_response = {}
    loggerutils.setup_logging()
    loggerutils.setup_formatted_logging(context)

    command = create_command(DISPATCHER_PATH)
    process: subprocess.Popen = create_subprocess(command)
    context.dispatcher_process = process
    context.logger.info("Created Dispatcher...")
    time.sleep(5)

    test_manager = TestManager(context, "127.0.0.5", 12345)
    thread = Thread(target=test_manager.listen_for_client_connections)
    thread.start()
    context.tm = test_manager

    context.logger.info("Created Test Manager...")

    command = create_command(PYTHON_TA_PATH)
    process: subprocess.Popen = create_subprocess(command)
    context.python_ta_process = process

    command = create_command(JAVA_TA_PATH)
    process: subprocess.Popen = create_subprocess(command)
    context.java_ta_process = process

    context.logger.info("Created All Test Agents...")


def after_all(context: Context):
    context.ue = None
    context.action = None
    context.json_dict = None
    context.status_json = None
    context.on_receive_msg = {}
    context.on_receive_rpc_response = {}

    context.tm.close_socket(sdk="python")
    context.tm.close_socket(sdk="java")
    context.tm.close()

    try:
        context.dispatcher_process.kill()
        context.dispatcher_process.communicate()
        context.java_ta_process.kill()
        context.java_ta_process.communicate()
        context.python_ta_process.kill()
        context.python_ta_process.communicate()
    except Exception as e:
        context.logger.error(e)
