import http.client, threading, sys, socket, time,signal
from queue import Queue, Empty, Full

stop_event = threading.Event()  # for handle keyboard interrupt
terminated = False
host_active = True

def signal_handler(sig,frame):
    global terminated
    terminated = True
    stop_event.set()

def fuzz(domain,port,ip,que):
    global host_active
    try:
        conn = http.client.HTTPConnection(ip,port,timeout=2) # when use ip it doesn't asks everytime ip from dns
        while not stop_event.is_set() or not que.empty():
            try:
                dir = que.get(timeout=0.2)
            except Empty:
                if not stop_event.is_set() or not que.empty():
                    continue
                break
            conn.request('GET',f"{dir}",headers={"Host":domain})    # Since ip uses for make connection should be provided Host header here to avoid 301 response
            try:
                res1 = conn.getresponse()
                res1.read()
                if(res1.status == 200): print(dir.ljust(15),res1.status,res1.reason)
                else:
                    conn.request("GET",f"{dir}/",headers={"Host":domain})
                    res2 = conn.getresponse()
                    res2.read()
                    if res2.status==200:
                        print(f"{dir}/".ljust(15),res2.status,res2.reason)
            except http.client.ResponseNotReady:
                pass
            que.task_done()
    except (TimeoutError,ConnectionRefusedError):
        host_active = False
    finally:
        if conn:
            conn.close()

def get_ip(target_data,raw_data):
    full_arg = raw_data.split(":")
    target_data.append("".join(full_arg[:-1]))
    try:
        port = int(full_arg[-1])
        target_data.append(port)
    except ValueError:
        port = 80
        target_data.append(port)
    try:
        addr = socket.getaddrinfo(target_data[0],port,family=socket.AF_INET,type=socket.SOCK_STREAM)[0][-1]
    except socket.gaierror:
        print("Coudn't find host IPv4 Address...")
        sys.exit(1)
    target_data.append(addr[0])
        

def get_flags(lst1):
    if len(sys.argv) < 7:
        print("Error: py fuzzer.py -h for help")
        sys.exit(1)
    try:
        data = sys.argv[1:]
        id = 0
        file_path, thread_cnt = "",10
        while id<len(data):
            if data[id] == '-u':
                get_ip(lst1,data[id+1])
            elif data[id] == '-w':
                file_path = data[id+1]
            elif data[id] == '-thread':
                match data[id+1]:
                    case '1': thread_cnt = 1
                    case '2': thread_cnt = 3
                    case '3': thread_cnt = 6
                    case '4': thread_cnt = 10
                    case '5': thread_cnt = 15
                    case _  : raise ValueError("Wrong input.Thread range 1-5")
            else:
                raise ValueError("Wrong input")
            id+=2
        return file_path,thread_cnt
    except ValueError:
        print("Error: py fuzzer.py -h for help")
        sys.exit(1)

def load_words(file_path,que):
    try:
        with open(file_path,'r') as f:
            file = f.readlines()
            id = 0
            while not stop_event.is_set() and id<len(file):
                try:
                    que.put(file[id].strip(),timeout=0.1)
                except Full:
                    continue
                id+=1
            stop_event.set()                            # tell fuzzing threads to all words are used
    except FileNotFoundError:
        print("Wordlist is not found")
        sys.exit(1)

def main():
    global host_active
    start = time.perf_counter()
    signal.signal(signal.SIGINT, signal_handler)
    q = Queue(maxsize=200)
    target = []
    path,count = get_flags(target)
    
    prod = threading.Thread(target=load_words, args=(path,q))
    prod.daemon = True                                  # if host not active auto die
    prod.start()

    for i in range(count):
        t = threading.Thread(target=fuzz, args=(target[0],target[1],target[2],q))
        t.daemon = True                                 # terminate when main thread die
        t.start()
    
    time.sleep(2.5)                                     # give enough time to fuzz threads find out host active or not
    if not host_active:
        print("Couldn't connect to host...")
        sys.exit(0)
    while prod.is_alive():
        time.sleep(0.2)
    q.join()                                            # wait until q empty

    if terminated:
        print("[ctrl+C] KeyboardInterrupt by user...")
    end = time.perf_counter()
    print(f"Scanned for {round(end-start,2)} seconds...")


if __name__ == '__main__':
    main()