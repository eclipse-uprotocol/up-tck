import socket
import logging
from constants import HEADER, PORT, SERVER, ADDR, FORMAT, DISCONNECT_MESSAGE 
from threading import Thread

logging.basicConfig(format='%(asctime)s %(message)s')
# create logger
logger = logging.getLogger('simple_example')
logger.setLevel(logging.INFO)

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

def handle_client(clientsocket: socket.socket,):
    while True: 
        msg_len_bytes: bytes = clientsocket.recv(4096) 
        print(msg_len_bytes)
        print(len(msg_len_bytes))
        print("----------")

while True:
    # Establish connection with client. 
    clientsocket, addr = server.accept()   

    thread = Thread(target=handle_client, args=(clientsocket, ))
    thread.start()
