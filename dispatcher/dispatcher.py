# -------------------------------------------------------------------------
#
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
#
# -------------------------------------------------------------------------


import socket
from typing import Dict, List
from constants import HEADER, PORT, SERVER, ADDR, FORMAT, DISCONNECT_MESSAGE 
from threading import Thread
from threading import Lock
import uuid
import logging 

logging.basicConfig(format='%(asctime)s %(message)s')
# create logger
logger = logging.getLogger('simple_example')
logger.setLevel(logging.INFO)


# Holds all client connections
clients: Dict[str, socket.socket] = {}
# Create the shared lock
lock = Lock()

def close_socket(client_id: str, locket: Lock):
    with locket:
        clients[client_id].close()
        del clients[client_id]

def handle_client(clientsocket: socket.socket, client_id: str, locket: Lock):
    while True: 
        
        try: 
            msg_len_bytes: bytes = clientsocket.recv(HEADER) 

            if msg_len_bytes == b'':
                # Client closed connection
                logger.info (f"stop handling client")
                close_socket(client_id, locket)
                break

            if msg_len_bytes is not None:
                # Client sends actual data
                
                msg_len: int = int(msg_len_bytes)
                recv_data: bytes = clientsocket.recv(msg_len) 

                logger.info (f"received data: {recv_data}")
                
                print(clients.keys())
                for peer_id, peer_socket in clients.items():
                    # Send if peer client is connected... 
                    try:
                        peer_socket.send(msg_len_bytes) 
                        peer_socket.send(recv_data) 
                        
                    except ConnectionAbortedError:
                        # Close and delete peer socket if peer client closed...
                        print("Inner Except")
                        close_socket(client_id, locket)

                        if peer_id == client_id:
                            return 
                        continue 

        except ConnectionAbortedError:
            # If client socket cannot receive, then close client 
            print("Outer Except")
            close_socket(client_id, locket)
            return


def run_server():
    # Create a socket object 
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         
    logger.info("Server Socket successfully created")

    # Prerequisite for server to listen for incoming conn. requests
    server.bind(ADDR)  
    logger.info("socket binded to " + str(ADDR)) 

    # Put the socket into listening mode 
    # NOTE: 5 connections are kept waiting 
    # if the server is busy and if a 6th socket tries to connect, then the connection is refused.
    server.listen(5)  
    logger.info ("socket is listening")  

    # Where server is always listening for incoming clients
    while True:
        # Establish connection with client. 
        clientsocket, addr = server.accept()   
        print(clientsocket)
        client_id: str = str(uuid.uuid4())
        clients[client_id] = clientsocket

        thread = Thread(target=handle_client, args=(clientsocket, client_id, lock))
        thread.start()
    
    server.close()


run_server()

    