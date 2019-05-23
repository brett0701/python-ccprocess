from __future__ import print_function
import socket
import websocket
import ssl
import json
import sys
import time

if __name__ == "__main__":
    ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
    print("Connecting...")
    try:
        ws.connect("wss://localhost:8888")
        print("Receiving...")
        result = ws.recv()
        print("Received '%s'" % result)
        result = ws.recv()
        print("Received '%s'" % result)
        ws.close()
    except:
        print("Error connecting to jSTL websocket. Verify it is running")
        sys.exit()
