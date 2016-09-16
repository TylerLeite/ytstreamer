import socket

#server_address = ('127.0.0.1', 8888)

host = socket.gethostbyaddr('ws://austindoes.work')
server_address = (host, 42069)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.connect(server_address)

data = sock.recv(512)
print data

sock.send("This is fake status")

sock.shutdown(socket.SHUT_RDWR)
sock.close()
