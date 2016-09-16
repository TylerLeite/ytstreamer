from websocket import create_connection
ws = create_connection("ws://austindoes.work:42069/ws")

result = ws.recv()

ws.close()
