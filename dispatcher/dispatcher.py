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

import logging
import selectors
import socket
from threading import Thread, Lock

logging.basicConfig(format='%(levelname)s| %(filename)s:%(lineno)s %(message)s')
logger = logging.getLogger('File:Line# Debugger')
logger.setLevel(logging.DEBUG)
DISPATCHER_ADDR = ("127.0.0.1", 44444)
BYTES_MSG_LENGTH: int = 32767


class Dispatcher:
    """
       Dispatcher class handles incoming connections and forwards messages
       to all connected up-clients.
       """

    def __init__(self):
        """
        Initialize the Dispatcher class.
        """
        self.selector = selectors.DefaultSelector()
        self.connected_sockets = set()
        self.lock = Lock()

        # Create server socket
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(DISPATCHER_ADDR)
        self.server.listen(100)
        self.server.setblocking(False)

        logger.info("Dispatcher server is running/listening")

        # Register server socket for accepting connections
        self.selector.register(self.server, selectors.EVENT_READ, self._accept_client_conn)

    def _accept_client_conn(self, server):
        """
        Callback function for accepting up-client connections.

        :param server: The server socket.
        """
        up_client_socket, _ = server.accept()
        logger.info(f'accepted conn. {up_client_socket.getpeername()}')

        with self.lock:
            self.connected_sockets.add(up_client_socket)

        # Register socket for receiving data
        self.selector.register(up_client_socket, selectors.EVENT_READ, self._receive_from_up_client)

    def _receive_from_up_client(self, up_client_socket):
        """
        Callback function for receiving data from up-client sockets.

        :param up_client_socket: The client socket.
        """
        recv_data = up_client_socket.recv(BYTES_MSG_LENGTH)

        if not recv_data:
            self._close_socket(up_client_socket)
            return

        logger.info(f"received data: {recv_data}")
        self._flood_to_sockets(up_client_socket, recv_data)

    def _flood_to_sockets(self, sender_socket, data):
        """
        Flood data from a sender socket to all other connected sockets.

        :param sender_socket: The socket from which the data is being sent.
        :param data: The data to be sent.
        """
        with self.lock:
            for up_client_socket in self.connected_sockets.copy():  # copy() to avoid RuntimeError
                # if up_client_socket != sender_socket:
                    try:
                        up_client_socket.sendall(data)
                    except ConnectionAbortedError as e:
                        logger.error(f"Error sending data to {up_client_socket.getpeername()}: {e}")
                        self._close_socket(up_client_socket)

    def listen_for_client_connections(self):
        """
        Start listening for client connections and handle events.
        """
        while True:
            events = self.selector.select()
            for key, _ in events:
                callback = key.data
                callback(key.fileobj)

    def _close_socket(self, up_client_socket):
        """
        Close a client socket and unregister it from the selector.

        :param up_client_socket: The client socket to be closed.
        """
        logger.info(f"closing socket {up_client_socket.getpeername()}")
        with self.lock:
            self.connected_sockets.remove(up_client_socket)
        self.selector.unregister(up_client_socket)
        up_client_socket.close()


if __name__ == '__main__':
    dispatcher = Dispatcher()
    thread = Thread(target=dispatcher.listen_for_client_connections)
    thread.start()
