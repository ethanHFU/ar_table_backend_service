import os
import sys
from service.utils.platform_info import CURRENT_OS, OS

import socket
import json

HOST = "127.0.0.1"   # or server IP
PORT = 9999

with socket.create_connection((HOST, PORT)) as sock:
    print("Connected to server")

    file = sock.makefile("r")  # line-buffered text mode

    try:
        for line in file:
            data = json.loads(line)
            print(data)
    except KeyboardInterrupt:
        print("Client exiting")

# print(CURRENT_OS)
# print(os.environ.get("OPENCV_LOG_LEVEL"))
# print(sys.path)