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
import json
import logging
import selectors
import socket

from threading import Lock

logging.basicConfig(format='%(levelname)s| %(filename)s:%(lineno)s %(message)s')
logger = logging.getLogger('File:Line# Debugger')
logger.setLevel(logging.DEBUG)
BYTES_MSG_LENGTH: int = 32767


class TestManager:

    def __init__(self, bdd_context, ip_addr: str, port: int):
        self.exit_manager = False
        self.selector = selectors.DefaultSelector()
        self.connected_sockets = {}
        self.lock = Lock()
        self.bdd_context = bdd_context
        # Create server socket
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((ip_addr, port))
        self.server.listen(100)
        self.server.setblocking(False)

        logger.info("TM server is running/listening")

        # Register server socket for accepting connections
        self.selector.register(self.server, selectors.EVENT_READ, self._accept_client_conn)

    def _accept_client_conn(self, server):
        """
        Callback function for accepting test agent connections.

        :param server: The server socket.
        """
        ta_socket, _ = server.accept()
        logger.info(f'accepted conn. {ta_socket.getpeername()}')

        # Register socket for receiving data
        self.selector.register(ta_socket, selectors.EVENT_READ, self._receive_from_test_agent)

    def _receive_from_test_agent(self, ta_socket):
        """
        Callback function for receiving data from test agent sockets.

        :param ta_socket: The client socket.
        """
        recv_data = ta_socket.recv(BYTES_MSG_LENGTH)

        if not recv_data or recv_data == b'':
            return
        json_data = json.loads(recv_data.decode('utf-8'))
        logger.info('Received from test agent: %s', json_data)
        self._process_message(json_data, ta_socket)

    def _process_message(self, json_data, ta_socket):
        if json_data['action'] == 'initialize':
            sdk: str = json_data['data']["SDK_name"].lower().strip()
            with self.lock:
                if sdk not in self.connected_sockets:
                    self.connected_sockets[sdk] = ta_socket
        elif json_data['action'] in ['send', 'registerlistener', 'unregisterlistener']:
            self.bdd_context.status_json = json_data['data']
        elif json_data['action'] == 'onreceive':
            self.bdd_context.on_receive_msg[json_data['ue']] = json_data['data']
        elif json_data['action'] == 'rpcresponse':
            self.bdd_context.on_receive_rpc_response[json_data['ue']] = json_data['data']
        elif json_data['action'] == 'uri_serialize':
            self.bdd_context.on_receive_serialized_uri = json_data['data']
        elif json_data['action'] == 'uri_deserialize':
            self.bdd_context.on_receive_deserialized_uri = json_data['data']
        elif json_data['action'] == 'uri_validate':
            self.bdd_context.on_receive_validation_result[json_data['ue']] = json_data['data']['result']
            self.bdd_context.on_receive_validation_msg[json_data['ue']] = json_data['data']['message']
        elif json_data['action'] == 'uuid_serialize':
            self.bdd_context.on_receive_serialized_uuid = json_data['data']
        elif json_data['action'] == 'uuid_deserialize':
            self.bdd_context.on_receive_deserialized_uuid = json_data['data']

    def close_socket(self, sdk=None, ta_socket=None):
        if ta_socket is not None:
            logger.info(f"closing socket {ta_socket.getpeername()}")
            with self.lock:
                for language, s in self.connected_sockets.items():
                    if s == ta_socket:
                        del self.connected_sockets[language]
                        print(f"Socket associated with {language} removed.")
                        return
                print("Socket not found in the connected sockets.")
            self.selector.unregister(ta_socket)
            ta_socket.close()
        else:
            logger.info(f"closing socket for {sdk}")
            with self.lock:
                if sdk in self.connected_sockets:
                    self.selector.unregister(self.connected_sockets[sdk])
                    self.connected_sockets[sdk].close()
                    del self.connected_sockets[sdk]
                    print(f"Socket associated with {sdk} removed.")
                    return
                print(f"{sdk} not found in the connected sockets.")

    def has_sdk_connection(self, sdk_name: str) -> bool:
        return sdk_name in self.connected_sockets

    def listen_for_client_connections(self):
        while not self.exit_manager:
            # Wait until some registered file objects or sockets become ready, or the timeout expires.
            events = self.selector.select(timeout=0)
            for key, mask in events:
                callback = key.data
                callback(key.fileobj)

    def receive_from_bdd(self, sdk_name, action, data, payload=None):
        ta_socket: socket.socket = self.connected_sockets[sdk_name.lower().strip()]

        # Create a new dictionary
        response_dict = {'data': data, 'action': action}
        if payload is not None:
            response_dict['payload'] = payload
        response_dict = json.dumps(response_dict).encode()
        ta_socket.sendall(response_dict)
        logger.info(f"Sent to TestAgent {response_dict}")

    def close(self):
        """Close the selector / test manager's server,
        BUT need to free its individual SDK TA connections using self.close_ta(sdk) first
        """
        self.exit_manager = True
        self.selector.close()
        self.server.close()
