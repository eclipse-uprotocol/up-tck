import selectors
import socket

sel = selectors.DefaultSelector()

def accept(sock):
    conn, addr = sock.accept()  # Should be ready
    print('accepted', conn, 'from', addr)
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, read)

def read(conn: socket.socket):
    print(conn.getsockname())  # server's ip and port
    print(conn.getpeername())  # client's ip and port

    # problem: if recv is too slow, can receive joined 2 or more sends 
    data = conn.recv(1000)  # Should be ready
    if data:
        print('echoing', repr(data), 'to', conn)
        conn.send(data)  # Hope it won't block
    else:
        print('closing', conn)
        sel.unregister(conn)
        conn.close()

# creates server socket
sock = socket.socket()
sock.bind(('localhost', 1234))
sock.listen(100)
sock.setblocking(False)
sel.register(sock, selectors.EVENT_READ, accept)

while True:
    # Wait until some registered file objects or sockets become ready, or the timeout expires.
    events = sel.select()
    for key, mask in events:
        callback = key.data
        callback(key.fileobj)