import sys
import socket
import pickle
import threading
import time

# Variables
server_ip = socket.gethostbyname(socket.gethostname())
server_port = 47000
free_clients = 0
information_base = dict()
ring_base = []

# Create socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((server_ip, server_port))
sock.setblocking(0)

# Message handling
def message_handler(data, addr):
    global free_clients
    command = data[0]

    if command == "register":
        # Check if name is in information base
        if data[1] in information_base:
            sock.sendto(pickle.dumps("FAILURE"), addr)
            print("Failed to register " + str(addr), flush=True)
        else:
            information_base[data[1]] = data[2:] + ["FREE"]
            free_clients += 1
            sock.sendto(pickle.dumps("SUCCESS"), addr)
            print("Successfully registerd " + str(addr), flush=True)
    elif command == "deregister":
        if data[1] in information_base and information_base[data[1]][4] != "InRing":
            del information_base[data[1]]
            free_clients -= 1
            sock.sendto(pickle.dumps("SUCCESS"), addr)
            print("Successfully deregisterd " + str(addr), flush=True)
        else:
            sock.sendto(pickle.dumps("FAILURE"), addr)
            print("Failed to deregister " + str(addr), flush=True)
    elif command == "setup-ring":
        if (data[2] in information_base) and (information_base[data[2]][4] == "FREE") and (data[1] >= 3) and (data[1]%2 != 0) and (free_clients-1 >= 2):
            ring_data = ()
            # Pick 3 clients to be part of ring (current client is first entry)
            ring_data = [data[2]] + information_base[data[2]][:4],
            information_base[data[2]][4] = "InRing"
            for client,info in information_base.items():
                if client != info[2] and info[4] == "FREE":
                    ring_data += [client] + info[:4],
                    info[4] = "InRing"
                if ring_data.count == data[1]:
                    break
            # Decrease value of free_clients
            free_clients -= data[1]
            # Add to ring base
            ring_base.append(["ring" + str(len(ring_base)), data[1], (data[2], "192.168.56.1",)])
            # Create message
            message = ["SUCCESS", ring_base[len(ring_base)-1][0], data[1], ring_data, 1]
            # Send message
            sock.sendto(pickle.dumps(message), addr)
            print("Setting up ring with users: " + str(ring_data))
        else:
            sock.sendto(pickle.dumps("FAILURE"), addr)
            print("Failed to setup ring!", flush=True)
    elif command == "setup-complete":
        # Update client state to Leader
        information_base[data[2]][4] = "Leader"
        # Store compute port in corresponding ring_base index
        for ring in ring_base:
            if ring[0] == data[1]:
                ring[2] += data[3],
        # Send success
        sock.sendto(pickle.dumps("SUCCESS"), addr)
        print("Succesfully set up ring with leader " + data[2], flush=True)


# Wait for hosts and create threads
def wait_for_clients():
    while(True):
        try:
            data,addr = sock.recvfrom(1024)
            message_handling_thread = threading.Thread(target=message_handler, args=(pickle.loads(data), addr))
            message_handling_thread.start()
        except BlockingIOError:
            pass

# main function
def main():
    try:
        wait_for_clients()
    except KeyboardInterrupt:
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
        sys.exit()
    
if __name__ == "__main__":
    main()