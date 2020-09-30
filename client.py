import sys
import socket
import pickle
import threading
import argparse
import time

# Handle command-line arguments(argparser)
parser = argparse.ArgumentParser(description = 'Initialize a client')
parser.add_argument('-n', '--name', type=str, metavar='', required=True, help='Client name(maximum 15 characters)')
parser.add_argument('-cip', '--client_ip', type=str, metavar='', required=False, default=socket.gethostbyname(socket.gethostname()), help='Client IP address')
parser.add_argument('-sip', '--server_ip', type=str, metavar='', required=False, default=socket.gethostbyname(socket.gethostname()), help='Server IP address')
parser.add_argument('-lcp', '--left_communication_port', type=int, metavar='', required=True, help='Client port number for left communication socket')
parser.add_argument('-scp', '--server_communication_port', type=int, metavar='', required=True, help='Client port number for server communication socket')
parser.add_argument('-rcp', '--right_communication_port', type=int, metavar='', required=True, help='Client port number for right communication socket')
args = parser.parse_args()

# Variables(initially instantiated)
client_name = args.name
client_ip = args.client_ip
server_ip = args.server_ip
server_port = 47000
left_communication_port = args.left_communication_port
server_communication_port = args.server_communication_port
right_communication_port = args.right_communication_port

# Variables(remaining)
client_list = None
rclient_ip = None
rclient_port = None
ring_id = None
ring_size = None
compute_port = None

# Create sockets
left_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
left_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
left_socket.bind((client_ip, left_communication_port))
#left_socket.settimeout(5)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((client_ip, server_communication_port))
#server_socket.settimeout(5)

right_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
right_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
right_socket.bind((client_ip, right_communication_port))
right_socket.settimeout(5)

# Message handler function
def message_handler(message):
    global rclient_ip,rclient_port,ring_id,ring_size
    
    if message == "SUCCESS":
        pass
        #print("SUCCESS", flush=True)
    elif message == "FAILURE":
        pass
        #print("FAILURE", flush=True)
    elif message[0] == "SUCCESS" and len(message) == 5: # Initialize ring setup
        # Store ring and index
        ring_id, ring_size = message[1], message[2]
        client_list = message[3]
        next_index = message[4]
        # Store right client information
        rclient_ip = client_list[next_index][1]
        rclient_port = client_list[next_index][2]
        # Increment index
        next_index += 1
        # Create message
        setup_message = pickle.dumps(["setup", client_list, next_index])
        # Send message to right socket
        client_rclient(setup_message)
    elif message[0] == "setup": # During setup
        client_list = message[1]
        next_index = message[2]
        if next_index == 1: # client is the leader
            # Create setup-complete message
            setup_complete_message = message_creator("setup-complete" + " " + ring_id + " " + client_name + " " + str(left_communication_port))
            # send confirmation to server
            server_socket.sendto(setup_complete_message, (server_ip, server_port))
        else: # client is not leader
            if next_index == len(client_list): # Final client
                # Store right client information
                rclient_ip = client_list[0][1]
                rclient_port = client_list[0][2]
                # Set nextindex to 1
                next_index = 1
            else: # Client isn't first or last 
                # Store right client information
                rclient_ip = client_list[next_index][1]
                rclient_port = client_list[next_index][2]
                # Increment index
                next_index += 1
            # Create message
            setup_message = pickle.dumps(["setup", client_list, next_index])
            # Send message to right socket
            client_rclient(setup_message)

# Message creator function
def message_creator(command):
    global ring_size,ring_id,compute_port
    final_message = None
    message = None

    tmp_arr = command.split(" ")
    funct = tmp_arr[0]

    # Check first index for desired command and formats message accordingly
    if funct == "exit":
        sys.exit()
    elif funct == "register":
        message = [funct, client_name, client_ip, left_communication_port, server_communication_port, right_communication_port]
    elif funct == "deregister":
        message = [funct, client_name]
    elif funct == "setup-ring":
        ring_size = int(tmp_arr[1])
        message = [funct, ring_size, client_name]
    elif funct == "setup-complete":
        ring_id,compute_port = tmp_arr[1],int(tmp_arr[3])
        message = [funct, ring_id, client_name, compute_port]

    # Pickle the message
    final_message = pickle.dumps(message)

    # Return message
    return final_message

# Client-LClient function
def client_lclient():
    while(True):
        # Recieve data
        data, addr = left_socket.recvfrom(1024)
        print("Message Recieved from " + str(addr), flush=True)

        # Send acknowledgement
        left_socket.sendto(pickle.dumps("SUCCESS"), addr)
        print("Acknowledgement sent to " + str(addr), flush=True)

        # Start thread for message handling
        #message_handling_thread = threading.Thread(target=message_handler, args=[pickle.loads(data)])
        #message_handling_thread.start()
        #message_handling_thread.join()

        message_handler(pickle.loads(data))

# Client-RClient function
def client_rclient(message):
    # Send acknowledgement
    print("Message sent to " + str((rclient_ip, rclient_port)), flush=True)
    right_socket.sendto(message, (rclient_ip, rclient_port))

    # Recieve data
    data, addr = right_socket.recvfrom(1024)
    print("Acknowledgement recieved from " + str(addr), flush=True)

    # Handle message
    message_handler(pickle.loads(data))

# Client-Server function
def client_server():
    while(True):
        # Create message from input command
        message = message_creator(input())

        # Send message to server
        server_socket.sendto(message, (server_ip, server_port))

        # Recieve message
        data = server_socket.recv(1024)

        # Start thread for message handling
        #message_handling_thread = threading.Thread(target=message_handler, args=[pickle.loads(data)])
        #message_handling_thread.start()

        # Wait for server to respond  and send to message handler
        message_handler(pickle.loads(data))

# main function
def main():
    # Create threads for server and left sockets
    server_thread = threading.Thread(target=client_server)
    left_thread = threading.Thread(target=client_lclient)

    try:
        # Start execution of threads for server and left sockets
        server_thread.start()
        left_thread.start()
    except KeyboardInterrupt:
        # Close threads
        server_thread.join()
        left_thread.join()

        # Close sockets and exit
        left_socket.shutdown(socket.SHUT_RDWR)
        right_socket.shutdown(socket.SHUT_RDWR)
        server_socket.shutdown(socket.SHUT_RDWR)
        left_socket.close()
        right_socket.close()
        server_socket.close()
        sys.exit()

if __name__ == "__main__":
    main()