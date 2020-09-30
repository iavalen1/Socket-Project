#!python

import sys
import socket
import threading
import time

def main():

    SERVER_ADDRESS = socket.gethostbyname(socket.gethostname())
    SERVER_PORT = 47000
    CLIENT_PORT = None
    CLIENT_ADDRESS = None
    sendMessage = "SUCCESS"
    messageRecieved = None

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((SERVER_ADDRESS, SERVER_PORT))
    #sock.settimeout(5)
    
    messageRecieved, (CLIENT_ADDRESS,CLIENT_PORT) = sock.recvfrom(1024)

    print(messageRecieved.decode("utf-8"))

    sock.sendto(sendMessage.encode("utf-8"), (CLIENT_ADDRESS, CLIENT_PORT))

if __name__ == "__main__":
    main()