import websocket

ws = websocket.WebSocket()
ws.connect("ws://192.168.1.113/ws/echo/")  # örnek path
ws.send("ping")
print(ws.recv())
ws.close()
