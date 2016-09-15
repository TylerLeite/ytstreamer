import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_address = ('127.0.0.1', 8081)
sock.bind(server_address)
sock.listen(5)

conn, addr = sock.accept()
print addr
data = conn.recv(1024)

command = data.split("GET /")[1].split(" HTTP")[0].split("/")
uid = command[0]
cmd = command[1]
args = command[2:-1]

print command
