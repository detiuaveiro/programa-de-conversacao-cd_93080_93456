# Echo server program
import socket
import json
import selectors

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 5000               # Arbitrary non-privileged port
sel = selectors.DefaultSelector()
clients = {}

def accept(sock, mask):
    conn, addr = sock.accept()  # Should be ready
    print('accepted', conn, 'from', addr)
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, read)

def read(conn, mask):
    data = conn.recv(1000)  # Should be ready
    msg = json.loads(data)
    if msg['op'] == 'register':
        clients[msg['user']] = conn  # Hope it won't block
    elif msg['op'] == 'msg':
        print('closing', conn)
    else:
        sel.unregister(conn)
        conn.close()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)
    sock.setblocking(False)
    conn, addr = s.accept()
    sel.register(conn, selectors.EVENT_READ, accept)
    while True:
        events = sel.select()
        for key, mask in events:
            callback = key.data
            callback(key.fileobj, mask)
