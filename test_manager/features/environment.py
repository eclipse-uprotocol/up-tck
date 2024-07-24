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

import random
import sys
import time
from threading import Thread

import git
from behave.model import Scenario
from behave.runner import Context

repo = git.Repo(".", search_parent_directories=True)
sys.path.insert(0, repo.working_tree_dir)

from dispatcher.dispatcher import Dispatcher
from test_manager.features.utils import loggerutils
from test_manager.testmanager import TestManager


def environment_generate_uri(transport_name: str) -> dict:
    """Generate a random URI for the test environment.
    :param transport_name: The name of the transport.
    :return: A dictionary containing the URI.
    """
    while True:
        ue_id = random.randrange(1, 0x7FFFFFFF)
        if (ue_id & 0xFFFF) != 0xFFFF:
            return {
                "authority_name": transport_name + "_authority",
                "ue_id": ue_id,
                "ue_version_major": str(1),
                "resource_id": str(0),
            }


def before_all(context):
    """Set up test environment
    Create driver based on the desired capabilities provided.
    Valid desired capabilities can be 'firefox', 'chrome' or 'ie'.
    For adding new drivers add a new static method in DriverFactory class.

    :param context: Holds contextual information during the running of tests
    :return: None
    """

    Scenario.continue_after_failed_step = True

    context.transport = {}
    context.ues = {}
    context.dispatcher = None

    context.ue_tracker = []

    loggerutils.setup_logging()
    loggerutils.setup_formatted_logging(context)

    context.logger.info("Setting up Test Environment...")

    test_manager = TestManager(context, "127.0.0.5", 33333)
    thread = Thread(target=test_manager.listen_for_incoming_events)
    thread.start()
    context.tm = test_manager

    counter = 1
    all_languages = []
    all_transports = []
    all_uris = []
    while context.config.userdata.get(f"uE{str(counter)}") is not None:
        all_languages.append(context.config.userdata[f"uE{str(counter)}"])
        all_transports.append(context.config.userdata[f"transport{str(counter)}"])
        context.logger.info(all_languages)

        # Build the transport name, which includes the language and the number UE of that language that it is.
        test_agent_name = (
            context.config.userdata[f"uE{str(counter)}"]
            + "_"
            + str(all_languages.count(context.config.userdata[f"uE{str(counter)}"]))
        )

        current_uri = environment_generate_uri(test_agent_name)
        while current_uri in all_uris:
            current_uri = environment_generate_uri(test_agent_name)

        all_uris.append(current_uri)
        context.ue_tracker.append(
            (
                test_agent_name,
                context.config.userdata[f"transport{str(counter)}"],
                current_uri,
                False,
            )
        )
        counter += 1

    if "socket" in all_transports:
        context.logger.info("Creating Dispatcher...")
        dispatcher = Dispatcher()
        thread = Thread(target=dispatcher.listen_for_client_connections)
        thread.start()
        context.dispatcher = dispatcher
        time.sleep(5)
    else:
        context.logger.info("No Dispatcher Required...")

    context.logger.info("Created Test Manager...")


def after_all(context: Context):
    context.ue = None
    context.action = None
    context.json_dict = None

    context.rust_sender = False

    for ue in context.ue_tracker:
        context.tm.close_test_agent(ue[0])
    context.tm.close()

    context.logger.info(context.dispatcher)
    if context.dispatcher is not None:
        context.logger.info("Closing Dispatcher...")
        context.dispatcher.close()

    context.logger.info("Closed All Test Agents and Test Manager...")

    try:
        for ue in context.ues:
            for process in context.ues[ue]:
                process.terminate()
    except Exception as e:
        context.logger.error(e)
