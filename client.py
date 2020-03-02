# Echo client program
import socket
import select
import json
import selectors
import sys
import time

HOST = 'localhost'      # Address of the host running the server  
PORT = 3700            # The same port as used by the server
sel = selectors.DefaultSelector()
name = input("Nome do cliente: ")
channel=input("Nome do canal: ")

def read(conn, mask):
    data = conn.recv(1000)  # Should be ready
    msg = json.loads(data)
    print(time.ctime(msg["ts"]),msg["user"]," said: ",msg["data"])

def got_keyboard_data(arg1, mask):
    msg = arg1.readline()
    msg = msg.rstrip()
    if msg == 'quit':
        z = {
            "op":"unregister",
            "user":name,
            "ts":time.time()
        }
        w = json.dumps(z).encode('utf-8')
        s.sendall(w)
        s.close()
        exit()
    else:
        z = {
            "op":"msg",
            "data":msg,
            "user":name,
            "channel":channel,
            "ts":time.time()
        }
        w = json.dumps(z).encode('utf-8')
        s.sendall(w)
    

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    strjson = json.dumps({"op":"register","user":name,"channel":channel})
    s.sendall(strjson.encode("utf-8"))
    sel.register(s, selectors.EVENT_READ, read)
    sel.register(sys.stdin, selectors.EVENT_READ, got_keyboard_data)
    while True:
        print("Digite a sua mensagem: ")
        events = sel.select()
        for key, mask in events:
            callback = key.data
            callback(key.fileobj, mask)
