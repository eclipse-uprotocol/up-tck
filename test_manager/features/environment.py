"""
SPDX-FileCopyrightText: Copyright (c) 2024 Contributors to the Eclipse Foundation
See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
SPDX-FileType: SOURCE
SPDX-License-Identifier: Apache-2.0
"""

import subprocess
import sys
from threading import Thread

import git
from behave.runner import Context

repo = git.Repo(".", search_parent_directories=True)
sys.path.insert(0, repo.working_tree_dir)

from test_manager.testmanager import TestManager
from test_manager.features.utils import loggerutils


def before_all(context):
    """Set up test environment
    Create driver based on the desired capabilities provided.
    Valid desired capabilities can be 'firefox', 'chrome' or 'ie'.
    For adding new drivers add a new static method in DriverFactory class.

    :param context: Holds contextual information during the running of tests
    :return: None
    """

    context.transport = {}
    context.ues = {}
    context.dispatcher = {}

    loggerutils.setup_logging()
    loggerutils.setup_formatted_logging(context)

    test_manager = TestManager(context, "127.0.0.5", 12345)
    thread = Thread(target=test_manager.listen_for_incoming_events)
    thread.start()
    context.tm = test_manager

    context.logger.info("Created Test Manager...")


def after_all(context: Context):
    context.ue = None
    context.action = None
    context.json_dict = None

    context.rust_sender = False
    context.tm.close_test_agent("rust")
    context.tm.close_test_agent("python")
    context.tm.close_test_agent("java")
    context.tm.close()
    context.dispatcher["socket"].close()

    context.logger.info("Closed All Test Agents and Test Manager...")
    try:
        for ue in context.ues:
            for process in context.ues[ue]:
                process.terminate()
    except Exception as e:
        context.logger.error(e)