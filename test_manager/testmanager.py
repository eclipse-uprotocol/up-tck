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

from collections import defaultdict, deque
import json
import logging
import re
import selectors
import socket
import time
from typing import Any, Deque, Dict, List, Tuple
from typing import Any as AnyType
from threading import Lock
import uuid
from multimethod import multimethod
import sys

logging.basicConfig(
    format="%(levelname)s| %(filename)s:%(lineno)s %(message)s"
)
logger = logging.getLogger("File:Line# Debugger")
logger.setLevel(logging.DEBUG)
BYTES_MSG_LENGTH: int = 32767


def convert_json_to_jsonstring(j: Dict[str, AnyType]) -> str:
    return json.dumps(j)


def convert_str_to_bytes(string: str) -> bytes:
    return str.encode(string)


def send_socket_data(s: socket.socket, msg: bytes):
    s.sendall(msg)


def is_close_socket_signal(received_data: bytes) -> bool:
    return received_data == b""


class TestAgentConnectionDatabase:
    def __init__(self) -> None:
        self.test_agent_address_to_name: Dict[tuple[str, int], str] = (
            defaultdict(str)
        )
        self.test_agent_name_to_address: Dict[str, socket.socket] = {}
        self.lock = Lock()

    def add(self, test_agent_socket: socket.socket, test_agent_name: str):
        test_agent_address: tuple[str, int] = test_agent_socket.getpeername()

        with self.lock:
            self.test_agent_address_to_name[test_agent_address] = (
                test_agent_name
            )
            self.test_agent_name_to_address[test_agent_name] = (
                test_agent_socket
            )

    @multimethod
    def get(self, address: Tuple[str, int]) -> socket.socket:
        test_agent_name: str = self.test_agent_address_to_name[address]
        return self.test_agent_name_to_address[test_agent_name]

    @multimethod
    def get(self, name: str) -> socket.socket:
        return self.test_agent_name_to_address[name]

    def contains(self, test_agent_name: str):
        return test_agent_name in self.test_agent_name_to_address

    @multimethod
    def close(self, test_agent_name: str):
        if test_agent_name is None or test_agent_name == "":
            return
        test_agent_socket: socket.socket = self.get(test_agent_name)
        self.close(test_agent_socket)

    @multimethod
    def close(self, test_agent_socket: socket.socket):
        test_agent_address: tuple[str, int] = test_agent_socket.getpeername()
        test_agent_name: str = self.test_agent_address_to_name.get(
            test_agent_address, None
        )

        if test_agent_name is None:
            return

        with self.lock:
            del self.test_agent_address_to_name[test_agent_address]
            del self.test_agent_name_to_address[test_agent_name]

        test_agent_socket.close()


class DictWithQueue:
    """
    maps a unique topic/keys to a queue for ordered messaging
    """
    def __init__(self) -> None:
        self.key_to_queue: Dict[str, Deque[Dict[str, Any]]] = defaultdict(
            deque
        )
        self.lock = Lock()

    def append(self, key: str, msg: Dict[str, Any]) -> None:
        with self.lock:
            self.key_to_queue[key].append(msg)
            logger.info(f"self.key_to_queue append {self.key_to_queue}")

    def contains(
        self, key: str, inner_key: str, inner_expected_value: str
    ) -> bool:
        queue: Deque[Dict[str, Any]] = self.key_to_queue[key]
        if len(queue) == 0:
            return False

        response_json: Dict[str, Any] = queue[0]
        incoming_req_id: str = response_json[inner_key]

        return incoming_req_id == inner_expected_value

    def popleft(self, key: str) -> Any:
        with self.lock:
            onreceive: Any = self.key_to_queue[key].popleft()
            logger.info(
                f'self.key_to_queue popleft {onreceive["action"]} {self.key_to_queue}'
            )
        return onreceive


class TestManager:
    def __init__(self, bdd_context, ip_addr: str, port: int):
        self.exit_manager = False
        self.socket_event_receiver = selectors.DefaultSelector()
        self.connected_test_agent_sockets: Dict[str, socket.socket] = {}
        self.test_agent_database = TestAgentConnectionDatabase()
        self.action_type_to_response_queue = DictWithQueue()
        self.lock = Lock()
        self.bdd_context = bdd_context

        # Create server socket
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if sys.platform != "win32":
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((ip_addr, port))
        self.server.listen(100)
        self.server.setblocking(False)

        logger.info("TM server is running/listening")

        # Register server socket for accepting connections
        self.socket_event_receiver.register(
            self.server, selectors.EVENT_READ, self._accept_client_conn
        )

    def _accept_client_conn(self, server: socket.socket):
        """
        Callback function for accepting test agent connections.

        :param server: The server socket.
        """
        ta_socket, _ = server.accept()
        logger.info(f"accepted conn. {ta_socket.getpeername()}")

        # Register socket for receiving data
        self.socket_event_receiver.register(
            ta_socket, selectors.EVENT_READ, self._receive_from_test_agent
        )

    def _receive_from_test_agent(self, test_agent: socket.socket):
        """
        Callback function for receiving data from test agent sockets.

        :param test_agent: The client socket.
        """
        recv_data = test_agent.recv(BYTES_MSG_LENGTH)

        if is_close_socket_signal(recv_data):
            self.close_test_agent(test_agent)
            return

        json_str: str = recv_data.decode("utf-8")
        logger.info(f"json_str: {json_str}")
        
        def convert_json_str_to_list_of_nested_dictionaries(flat_concatenated_json: str) -> List[Dict[str, Any]]:
            """in case if json messages are concatenated, we are splitting the json data and handling it separately
            eg: {json, action: ..., messge: "...."}{json, action: status messge: "...."}
            
            Args:
                flat_concatenated_json (str): looks like "{json, action: ..., messge: ....}"

            Returns:
                List[Dict[str, Any]]: list of jsons [{...}, {...}, ...]
            """
            list_of_nested_dictionaries: List[Dict[str, Any]] = []
            open_curly_brace_count: int = 0  # x >= 0
            start_nested_dict_index: int = 0  # x >= 0
            for i, char in enumerate(flat_concatenated_json):
                if char == "}":
                    open_curly_brace_count -= 1
                    
                    if open_curly_brace_count == 0:  # if found an entire nested dict,
                        end_nested_dict_index: int = i + 1
                        
                        # get sub json string
                        sub_flat_json: str = flat_concatenated_json[start_nested_dict_index : end_nested_dict_index]
                        nested_dict: Dict[str, Any] = json.loads(sub_flat_json)
                        list_of_nested_dictionaries.append(nested_dict)
                        
                        # start to find next nested dictionary in jsonstring
                        start_nested_dict_index = end_nested_dict_index
                elif char == "{":
                    open_curly_brace_count += 1

            return list_of_nested_dictionaries
        
        received_jsons: List[Dict[str, Any]] = convert_json_str_to_list_of_nested_dictionaries(json_str)
        for json_data in received_jsons:
            logger.info("Received from test agent: %s", json_data)
            if json_data.get("test_id") is not None:
                json_data["test_id"] = json_data["test_id"].strip('"')
            self._process_receive_message(json_data, test_agent)

    def _process_receive_message(
        self, response_json: Dict[str, Any], ta_socket: socket.socket
    ):
        if response_json["action"] == "initialize":
            test_agent_sdk: str = (
                response_json["data"]["SDK_name"].lower().strip()
            )
            self.test_agent_database.add(ta_socket, test_agent_sdk)
            return

        action_type: str = response_json["action"]
        self.action_type_to_response_queue.append(action_type, response_json)

    def has_sdk_connection(self, test_agent_name: str) -> bool:
        return self.test_agent_database.contains(test_agent_name)

    def listen_for_incoming_events(self):
        """
        Listens for Test Agent connections and messages, then creates a thread to start the init process
        """

        while not self.exit_manager:
            # Wait until some registered file objects or sockets become ready, or the timeout expires.
            events = self.socket_event_receiver.select(timeout=0)
            for key, mask in events:
                callback = key.data
                callback(key.fileobj)

    def request(
        self,
        test_agent_name: str,
        action: str,
        data: Dict[str, AnyType],
        payload: Dict[str, AnyType] = None,
    ):
        """
        Sends a blocking request message to sdk Test Agent (ex: Java, Rust, C++ Test Agent)
        """
        # Get Test Agent's socket
        test_agent_name = test_agent_name.lower().strip()
        test_agent_socket: socket.socket = self.test_agent_database.get(
            test_agent_name
        )

        # Create a request json to send to specific Test Agent
        test_id: str = str(uuid.uuid4())
        request_json = {"data": data, "action": action, "test_id": test_id}
        if payload is not None:
            request_json["payload"] = payload

        # Pack json as binary
        request_str: str = convert_json_to_jsonstring(request_json)
        request_bytes: bytes = convert_str_to_bytes(request_str)

        send_socket_data(test_agent_socket, request_bytes)
        logger.info(f"Sent to TestAgent{request_json}")

        # Wait n secs until get response, or return (exit if got response or time > 10)
        # USocket transport is a TCP connection: reliable, inorder packet delivery
        # -> no need to retransmit or check if messages are received or sent properly
        logger.info(f"Waiting test_id {test_id}")
        start_time: float = time.time()
        wait_time_sec: float = 10.0
        while not self.action_type_to_response_queue.contains(
            action, "test_id", test_id
        ) and time.time() - start_time <= wait_time_sec:
            pass
        
        if time.time() - start_time > wait_time_sec:
            return {"error", f"timed out: did not get an UStatus response within {wait_time_sec} seconds"}
            
        logger.info(f"Received test_id {test_id}")

        # Get response
        response_json: Dict[str, Any] = (
            self.action_type_to_response_queue.popleft(action)
        )
        return response_json

    def get_onreceive(self, test_agent_name: str) -> Dict[str, Any]:
        start_time: float = time.time()
        wait_time_sec: float = 10.0
        while not self.action_type_to_response_queue.contains(
            "onreceive", "ue", test_agent_name
        ) and time.time() - start_time <= wait_time_sec:
            pass
        if time.time() - start_time > wait_time_sec:
            return {"error", f"timed out: did not get an OnReceive message within {wait_time_sec} seconds"}

        return self.action_type_to_response_queue.popleft("onreceive")

    @multimethod
    def close_test_agent(self, test_agent_socket: socket.socket):
        # Stop monitoring socket/fileobj. A file object shall be unregistered prior to being closed.
        self.socket_event_receiver.unregister(test_agent_socket)
        self.test_agent_database.close(test_agent_socket)

    @multimethod
    def close_test_agent(self, test_agent_name: str):
        if self.test_agent_database.contains(test_agent_name):
            test_agent: socket.socket = self.test_agent_database.get(
                test_agent_name
            )
            self.close_test_agent(test_agent)

    def close(self):
        """Close the selector / test manager's server,
        BUT need to free its individual SDK TA connections using self.close_ta(sdk) first
        """
        self.exit_manager = True
        self.socket_event_receiver.close()
        self.server.close()
