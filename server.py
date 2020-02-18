# Echo server program
import socket
import select
import json
import selectors
import time

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 7000             # Arbitrary non-privileged port
sel = selectors.DefaultSelector()
clients = {}

def accept(sock, mask):
    conn, addr = sock.accept()  # Should be ready
    print('accepted', conn, 'from', addr)
    data = conn.recv(1024)
    user = json.loads(data)
    clients[user["user"]]=conn
    sel.register(conn, selectors.EVENT_READ, read)

def read(conn, mask):
    data = conn.recv(1000)  # Should be ready
    msg = json.loads(data)
    if msg["op"] == "register":
        clients[msg["user"]] = conn  # Hope it won't block
    elif msg["op"] == "msg":
        for key in clients:
            if key != msg["user"]:
                clients[key].sendall(data)
    else:
        sel.unregister(conn)
        print(time.ctime(msg["ts"]),": Disconecting...")
        del clients[msg["user"]]
        conn.close()

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

