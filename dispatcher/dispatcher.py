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

import logging
import selectors
import socket
import sys
from threading import Lock
from typing import Set

logging.basicConfig(
    format="%(levelname)s| %(filename)s:%(lineno)s %(message)s"
)
logger = logging.getLogger("File:Line# Debugger")
logger.setLevel(logging.DEBUG)
DISPATCHER_ADDR = ("127.0.0.1", 44444)
BYTES_MSG_LENGTH: int = 32767


class Dispatcher:
    """
    Dispatcher class handles incoming connections and forwards messages
    to all connected up-clients.
    """

    def __init__(self):
        self.selector = selectors.DefaultSelector()
        self.connected_sockets: Set[socket.socket] = set()
        self.lock = Lock()
        self.server = None

        # Create server socket
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if sys.platform != "win32":
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(DISPATCHER_ADDR)
        self.server.listen(100)
        self.server.setblocking(False)

        logger.info("Dispatcher server is running/listening")

        # Register server socket for accepting connections
        self.selector.register(
            self.server, selectors.EVENT_READ, self._accept_client_conn
        )

        # Cleanup essentials
        self.dispatcher_exit = False

    def _accept_client_conn(self, server: socket.socket):
        """
        Callback function for accepting up-client connections.

        :param server: The server socket.
        """

        up_client_socket, _ = server.accept()
        logger.info(f"accepted conn. {up_client_socket.getpeername()}")

        with self.lock:
            self.connected_sockets.add(up_client_socket)

        # Register socket for receiving data
        self.selector.register(
            up_client_socket,
            selectors.EVENT_READ,
            self._receive_from_up_client,
        )

    def _receive_from_up_client(self, up_client_socket: socket.socket):
        """
        Callback function for receiving data from up-client sockets.

        :param up_client_socket: The client socket.
        """
        try:

            recv_data: bytes = up_client_socket.recv(BYTES_MSG_LENGTH)

            if recv_data == b"":
                self._close_connected_socket(up_client_socket)
                return

            logger.info(f"received data: {recv_data}")
            self._flood_to_sockets(recv_data)
        except Exception:
            logger.error("Received error while reading data from up-client")
            self._close_connected_socket(up_client_socket)

    def _flood_to_sockets(self, data: bytes):
        """
        Flood data from a sender socket to all other connected sockets.

        :param data: The data to be sent.
        """
        # for up_client_socket in self.connected_sockets.copy():  # copy() to avoid RuntimeError
        for up_client_socket in self.connected_sockets:
            try:
                up_client_socket.sendall(data)
            except ConnectionAbortedError as e:
                logger.error(
                    f"Error sending data to {up_client_socket.getpeername()}: {e}"
                )
                self._close_connected_socket(up_client_socket)

    def listen_for_client_connections(self):
        """
        Start listening for client connections and handle events.
        """
        while not self.dispatcher_exit:
            events = self.selector.select(timeout=0)
            for key, _ in events:
                callback = key.data
                callback(key.fileobj)

    def _close_connected_socket(self, up_client_socket: socket.socket):
        """
        Close a client socket and unregister it from the selector.

        :param up_client_socket: The client socket to be closed.
        """
        logger.info(f"closing socket {up_client_socket.getpeername()}")
        with self.lock:
            self.connected_sockets.remove(up_client_socket)

        self.selector.unregister(up_client_socket)
        up_client_socket.close()

    def close(self):
        self.dispatcher_exit = True
        for utransport_socket in self.connected_sockets.copy():
            self._close_connected_socket(utransport_socket)
        # Close server socket
        try:
            self.selector.unregister(self.server)
            self.server.close()
            logger.info("Server socket closed!")
        except Exception as e:
            logger.error(f"Error closing server socket: {e}")

        # Close selector
        self.selector.close()
        logger.info("Dispatcher closed!")
