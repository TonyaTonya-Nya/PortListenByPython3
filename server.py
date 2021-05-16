import socket
import sys
import json
import asyncio
import threading
import datetime

threads = []
host = "0.0.0.0"


def server(port):

    try:
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        print("Error creating server socket: %s" % e)
        sys.exit(1)

    try:
        serversocket.bind((host, port))
    except socket.error as e:
        print("Bind server socket failed: %s" % e)
        sys.exit(1)

    # 允許同時最大socket量
    serversocket.listen(10)
    print('Listening on port %s ...' % port)

    while True:
        # 建立客户端連接
        clientsocket, addr = serversocket.accept()
        print("Client:{0}".format(addr))

        try:
            request = clientsocket.recv(4096).decode("utf-8", "ignore")
        except socket.error as e:
            print("Error receiving data: %s" % e)
            sys.exit(1)

        if not len(request):
            request=""

        print(request)

        # 寫入Log
        log(addr, request, serversocket.getsockname())

        # 關閉客户端連接
        clientsocket.close()


# 回傳值
'''
        fin = open('index.html')
        content = fin.read()
        fin.close()
        response = 'HTTP/1.0 200 OK\n\n' + content
        clientsocket.sendall(response.encode())
        clientsocket.close()
'''


def log(addr, request, host):

    timestamp = datetime.datetime.now()

    arr = []
    method = ''
    if request:
        arr = request.split('\r\n')

    for ele in arr:
        if ("HTTP" in ele) | ("http" in ele):
            method = ele
            break

    data = {
        "clientIP": "{0}".format(addr),
        "serverIP": "{0}".format(host),
        "method": method,
        "timeStamp": datetime.datetime.strftime(timestamp, '%Y-%m-%d %H:%M:%S')
    }

    with open(datetime.datetime.today().strftime("%Y-%m-%d")+".json", 'a') as logfile:
        json.dump(data, logfile, indent=4)


def main():
    for port in ports:
        t = threading.Thread(target=server, args=(port,))
        threads.append(t)

    for t in threads:
        t.start()


with open('setting.json', 'r') as jsonfile:
    ports = json.loads(jsonfile.read())
    jsonfile.close()
main()
