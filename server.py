# Echo server program
import socket
import select
import json
import selectors
import time

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 3725            # Arbitrary non-privileged port
sel = selectors.DefaultSelector()
clients = {}
channels = {}

def accept(sock, mask):
    conn, addr = sock.accept()  # Should be ready
    print('accepted', conn, 'from', addr)
    sel.register(conn, selectors.EVENT_READ, read)

def read(conn, mask):
    data = conn.recv(4096)  # Should be ready
    a_data=data.decode('utf-8')
    index=a_data.find("\r\m")
    while (index !=-1 and a_data[:index] !=""):
        this_data = a_data[:index]
        a_data = a_data[index:]
        this_data =json.loads(this_data)
        print('echoing', repr(this_data), 'to', conn)
        if this_data["op"] == "register":
            print("resgistering")
            clients[this_data["user"]] = conn  # Hope it won't block
            channels[this_data["user"]] = this_data["channel"]
        elif this_data["op"] == "msg":
            for key in clients:
                if channels[key] == this_data["channel"] and key != this_data["user"]:
                    clients[key].sendall((json.dumps(this_data)+"\r\m").encode('utf-8'))
        else:
            sel.unregister(conn)
            print(time.ctime(this_data["ts"]),": Disconecting...")
            del clients[this_data["user"]]
            conn.close()
        index = a_data.find("\r\m")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(100)
    s.setblocking(False)
    sel.register(s, selectors.EVENT_READ, accept)
    while True:
        events = sel.select()
        for key, mask in events:
            callback = key.data
            callback(key.fileobj, mask)

