import http.client
import threading
import sys
import socket
import time
import os
from queue import Queue

def fuzz(dir):
    pass

def connect_to_host():
    domain = sys.argv[1]
    try:
        addr = socket.getaddrinfo(domain,'80',family=socket.AF_INET,type=socket.SOCK_STREAM)[0][-1]
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.connect(addr)
    except socket.gaierror:
        print("Coudn't find host IPv4 Address...")
        sys.exit(1)
    except ConnectionRefusedError:
        print("Connection refused...")
        sys.exit(1)
    return sock,domain,addr[0]
    
def main():
    sock,domain,ip = connect_to_host()
    sock.close()

if __name__ == '__main__':
    main()