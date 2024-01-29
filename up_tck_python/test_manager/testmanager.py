# -------------------------------------------------------------------------

# Copyright (c) 2023 General Motors GTO LLC
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
# SPDX-FileCopyrightText: 2023 General Motors GTO LLC
# SPDX-License-Identifier: Apache-2.0

# -------------------------------------------------------------------------

from abc import ABC, abstractmethod

import socket
from typing import Dict

from uprotocol.proto.ustatus_pb2 import UStatus
from uprotocol.proto.uattributes_pb2 import UAttributes
from uprotocol.proto.uri_pb2 import UUri
from uprotocol.proto.upayload_pb2 import UPayload
from uprotocol.proto.umessage_pb2 import UMessage

class TestManager(ABC):
    '''
    TestManager is a component in the up-tck that creates and sends commands to test agents. These commmands will
    trigger tests in the test agents and wait for responses from the test agents. 
    '''

    @abstractmethod
    def send_command(self, sdk_name: str, command: str,  topic: UUri, payload: UPayload, attributes: UAttributes) -> UStatus:
        '''
        Sends command and created UMessage to the test agent associated with the sdk_name parameter.
        @param sdk_name:Language associated with the connected test agent.
        @param command:Command that will be sent to the test agent(s).
        @param topic:Resolved UUri topic to send the payload to.
        @param payload:Actual payload.
        @param attributes:Additional transport attributes.
        @return:Returns OKSTATUS if the payload has been successfully sent (ACK'ed), otherwise it returns FAILSTATUS
        with the appropriate failure.
        '''
        pass
    
    @abstractmethod
    def send_to_client(self, client: socket.socket, json_message: Dict[str, str]) -> None:
        '''
        Calls socket.send() for the client socket associated with the SDK Name.
        @param client:Socket that message is being sent to.
        @param json_message: Message to be sent.
        '''
    
    @abstractmethod
    def send_msg_to_test_agent(self, sdk_name:str, command: str, umsg: UMessage) -> UStatus:
        '''
        Sends the built UMessage to the client socket specified by the sdk_name.
        @param sdk_name:Language associated with the connected test agent.
        @param command:Command that will be sent to the test agent(s).
        @param umsg: constructed UMessage that will be sent to test agent.
        '''
        pass