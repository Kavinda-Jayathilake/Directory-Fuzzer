import http.client
import threading
import sys
import socket
import time
import os
from queue import Queue

def fuzz(domain,ip,dir):
    conn = http.client.HTTPConnection(ip,80,timeout=2) # when use ip it doesn't asks everytime ip from dns
    conn.request('GET','/',headers={"Host":domain})  # if i use ip first i should provide Host header here to avoid 301 response
    res = conn.getresponse()
    print(res.status,res.reason)


def connect_to_host():
    domain = sys.argv[1]
    try:
        addr = socket.getaddrinfo(domain,'80',family=socket.AF_INET,type=socket.SOCK_STREAM)[0][-1]
    except socket.gaierror:
        print("Coudn't find host IPv4 Address...")
        sys.exit(1)
    return domain,addr[0]
    
def main():
    domain,ip = connect_to_host()
    fuzz(domain,ip,'test')

if __name__ == '__main__':
    main()