import socket
import json

host = "127.0.0.1"

with open('ports.json', 'r') as jsonfile:
    ports = json.loads(jsonfile.read())
    jsonfile.close()

for port in ports:
    for i in range(1,2):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        s.connect((host, port))
        s.send("test request".encode())
        s.close()
