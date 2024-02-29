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
import socket
from typing import Callable, Dict, Tuple
from threading import Thread
from threading import Lock
import sys
import selectors

from logger.logger import logger

from up_client_socket_python.utils.socket_message_processing_utils import receive_socket_data

PORT = 44444
IP = "127.0.0.1" 
ADDR = (IP, PORT)

    
class Dispatcher:
    def __init__(self) -> None:
        # holds all SocketUTransporters: client's (ip, port) -> socket conn.
        self.utransport_clients: Dict[Tuple[str, int], socket.socket] = {}
        
        # locks for writers priority and thread safe performance
        self.count_writers_lock: Lock = Lock()
        self.count_readers_lock: Lock = Lock()
        self.block_readers_lock: Lock = Lock()
        self.access_clients_lock: Lock = Lock()
        self.num_writers: int = 0
        self.num_readers: int = 0
        
        # Creates Dispatcher socket server so it can accept connections from SocketUTransports
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Give server an IP and Port, so other clients can conn to
        self.server.bind(ADDR)  
        # Prerequisite to listen for incoming conn. requests
        self.server.listen(100)  
        
        logger.info ("Dispatcher server is running/listening")  
        
        self.server.setblocking(False)
        
        # Selector allows high-level and efficient I/O multiplexing, built upon the select module primitives.
        self.selector = selectors.DefaultSelector()
        # Register server socket so selector can monitor for incoming client conn. and calls provided callback() in listen_for_client_connections()
        self.selector.register(self.server, selectors.EVENT_READ, self.__accept_client_conn)
        
    def listen_for_client_connections(self):
        """
        Listens for Socket UTransport Connections and creates a thread to start the init process
        """
        
        while True:
            # Wait until some registered file objects or sockets become ready, or the timeout expires.
            events = self.selector.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj)
                
    def __accept_client_conn(self, server: socket.socket):
        socket_utransport, addr = server.accept() 
        logger.info(f'accepted conn. {addr}')
        
        self.__writer_priority_write_sockets(self.__save_socket, socket_utransport)

        # Never wait for the operation to complete. 
        # So when call send(), it will put as much data in the buffer as possible and return.
        socket_utransport.setblocking(False)
        # Register client socket so selector can monitor for incoming TA data and calls provided callback()
        self.selector.register(socket_utransport, selectors.EVENT_READ, self.__receive_from_socketutransport)
    
    def __save_socket(self, socket_utransport: socket.socket):
        """saves newly connected Socket UTransport client sockets

        Args:
            socket_utransport (socket.socket): Socket UTransport client socket
        """
        addr: Tuple[str, int] = socket_utransport.getpeername()
        self.utransport_clients[addr] = socket_utransport
        
    def __writer_priority_write_sockets(self, write_func: Callable, socket_utransport: socket.socket):
        """gives write priority when changing add or remove sockets

        Args:
            write_func (Callable): save or close/remove sockets
            socket_utransport (socket.socket): 
        """
        with self.count_writers_lock:
            if self.num_writers == 0:
                self.block_readers_lock.acquire()
            self.num_writers += 1
        
        with self.access_clients_lock:
            write_func(socket_utransport)  # writing 
            
        with self.count_writers_lock:
            self.num_writers -= 1
            if self.num_writers == 0:
                self.block_readers_lock.release()
    
    def __close_socket(self, socket_utransport: socket.socket):
        """
        closes socket connection and dont listen to incoming messages anymore from respective socket
        """        
        utransport_addr: Tuple[str, int] = socket_utransport.getpeername()
        logger.info(f"closing socket {utransport_addr}")

        client_socket: socket.socket = self.utransport_clients.pop(utransport_addr, None)
        
        if client_socket:
            client_socket.close()
            self.selector.unregister(client_socket)
    
    def __writer_priority_read_sockets(self, read_func: Callable, data: bytes):
        """when doing any reading/iterating over connected SocketUTransports, we give writer priority using locks/mutexes
        Reasoning is if socket is closed/added, we want it to be updated 1st before we read/send data again

        Args:
            read_func (Callable): reading functions (e.g. iteration sending)
            data (bytes): data used to send (so far...)
        """
        with self.block_readers_lock:
            with self.count_readers_lock:
                if self.num_readers == 0:
                    self.access_clients_lock.acquire()
                self.num_readers += 1
                
        read_func(data)
        
        with self.count_readers_lock:
            self.num_readers -= 1
            if self.num_readers == 0:
                self.access_clients_lock.release()
            
                
    def __flood_to_sockets(self, data: bytes):
        """sends data to all connected SocketUTransport client sockets

        Args:
            data (bytes): data sent
        """
        for peer_addr, peer_socket in self.utransport_clients.items():
            # Send if peer client is connected... 
            try:
                peer_socket.sendall(data) 
                
            except ConnectionAbortedError as i_e:
                # Close and delete peer socket if peer client closed...
                logger.error(f"Peer socket exception: {i_e}")
                
                # queues close socket thru mutex
                self.__writer_priority_write_sockets(self.__close_socket, peer_socket)
    
    def __receive_from_socketutransport(self, utransport: socket.socket):
        """floods incoming data from one client to every connected clients

        Args:
            utransport (socket.socket): SocketUTransport client socket
        """
            
        recv_data: bytes = receive_socket_data(utransport)
        
        if recv_data == b"":
            try: 
                self.__writer_priority_write_sockets(self.__close_socket, utransport)
                
            except OSError as oserr:
                logger.error(oserr)
            return
        
        logger.info (f"received data: {recv_data}")
        
        self.__writer_priority_read_sockets(self.__flood_to_sockets, recv_data)
        
        
if __name__ == '__main__':

    logger.info(f"endian: {sys.byteorder}")
    dispatcher = Dispatcher()
    thread = Thread(target=dispatcher.listen_for_client_connections)
    thread.start()
    
    