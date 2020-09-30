import sys
import socket
import pickle
import threading
import time

CLIENT_NAME = None
CLIENT_ADDRESS = None
CLIENT_PORTS = []
CLIENT_LISTEN_PORT = None
SERVER_ADDRESS = socket.gethostbyname(socket.gethostname())
SERVER_PORT = 47000
RING_SIZE = None
RING_ID = None
RING_LEADER_NAME = None
RING_LEADER_PORT = None
SEND_MESSAGE = None
RECIEVED_MESSAGE = None

def createMessage(args):
    if args[1] == "register":
        CLIENT_NAME = args[2]
        CLIENT_ADDRESS = args[3]
        CLIENT_PORTS = [int(args[4]), int(args[5]), int(args[6])]
        CLIENT_LISTEN_PORT = int(args[4])
        SEND_MESSAGE = ["register", CLIENT_NAME, CLIENT_ADDRESS, CLIENT_PORTS]
    if args[1] ==  "deregister":
        CLIENT_NAME = args[2]
        SEND_MESSAGE = ["deregister", CLIENT_NAME]
    if args[1] == "setup-ring":
        RING_SIZE = args[2]
        CLIENT_NAME = args[3]
        SEND_MESSAGE = ["setup-ring", RING_SIZE, CLIENT_NAME]
    if args[1] == "setup-complete":
        RING_ID = args[2]
        RING_LEADER_NAME = args[3]
        RING_LEADER_PORT = args[4]
        SEND_MESSAGE = ["setup-complete", RING_ID, RING_LEADER_NAME, RING_LEADER_PORT]
    if args[1] == "--help":
        print("python client.py register <user-name> <IP-address> <port(s)>")
        print("python client.py deregister <user-name>")
        print("python client.py setup-ring <ring-size> <user-name>")
        print("python client.py setup-complete <ring-id> <leader-user-name> <leader-port>")
        sys.exit()

def main():

    print(socket.gethostbyname(socket.gethostname()))
    createMessage(sys.argv)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((CLIENT_ADDRESS, CLIENT_PORTS[0]))
    sock.settimeout(5)

    serial_data = pickle.dumps(SEND_MESSAGE)

    sock.sendto(serial_data, (SERVER_ADDRESS, SERVER_PORT))

    RECIEVED_MESSAGE = sock.recvfrom(1024)[0].decode("utf-8")

    print(RECIEVED_MESSAGE)

if __name__ == "__main__":
    main()