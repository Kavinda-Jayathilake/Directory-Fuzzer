import http.client, threading, sys, socket, time, os,signal
from queue import Queue

def signal_handler(sig,frame):
    print("[ctrl+C] Interrpted by user...")
    sys.exit(0)

def fuzz(domain,ip,que):
    try:
        conn = http.client.HTTPConnection(ip,8000,timeout=2) # when use ip it doesn't asks everytime ip from dns
        while not que.empty():
            try:
                dir = que.get_nowait()
            except:
                break
            conn.request('GET',f"{dir}",headers={"Host":domain})    # Since ip uses for make connection should be provided Host header here to avoid 301 response
            try:
                res1 = conn.getresponse()
                if(res1.status == 200): print(dir,res1.status,res1.reason)
                else:
                    conn.request("GET",f"{dir}/",headers={"Host":domain})
                    res2 = conn.getresponse()
                    print(f"{dir}/",res2.status,res2.reason)
            except http.client.ResponseNotReady:
                pass
            que.task_done()
    except TimeoutError:
        print("Connection declined by host...")
    finally:
        conn.close()



def get_ip():
    domain = sys.argv[1]
    try:
        addr = socket.getaddrinfo(domain,'80',family=socket.AF_INET,type=socket.SOCK_STREAM)[0][-1]
    except socket.gaierror:
        print("Coudn't find host IPv4 Address...")
        sys.exit(1)
    return domain,addr[0]

def get_flags():
    if len(sys.argv) < 4:
        print("Error: py fuzzer.py -h for help")
        sys.exit(1)
    try:
        data = sys.argv[2:]
        id = 0
        file_path, thread_cnt = "",10
        while id<len(data):
            if data[id] == '-w':
                file_path = data[id+1]
            elif data[id] == '-thread':
                match data[id+1]:
                    case '1': thread_cnt = 10
                    case '2': thread_cnt = 20
                    case '3': thread_cnt = 30
                    case '4': thread_cnt = 40
                    case '5': thread_cnt = 50
                    case _  : raise ValueError("Wrong input.Thread range 1-5")
            else:
                raise ValueError("Wrong input")
            id+=2
        return file_path,thread_cnt
    except ValueError:
        print("Error: py fuzzer.py -h for help")

def main():
    signal.signal(signal.SIGINT, signal_handler)
    try:
        domain,ip = get_ip()
        file,cnt = get_flags()
        q = Queue(maxsize=1000)

        try:
            with open(file,'r') as f:
                for word in f.readlines():
                    q.put(word.strip())
        except FileNotFoundError:
            print("Wordlist not found")
            sys.exit(1)

        fuzz(domain,ip,q)

    except KeyboardInterrupt:
        print("Program terminated!")

if __name__ == '__main__':
    main()