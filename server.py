import socket
import sys
import json
import threading
import datetime
import pymysql


with open('setting.json', 'r') as jsonfile:
    setting = json.loads(jsonfile.read())
    jsonfile.close()
    
threads = []
host = "0.0.0.0"
table_name = setting.get("db_table_name")
db_settings = setting.get("db_settings")
lock = threading.Lock()


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
            request = ""

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

    data = [
        "{0}".format(addr),
        "{0}".format(host),
        method,
        datetime.datetime.strftime(timestamp, '%Y-%m-%d %H:%M:%S')
    ]

    clientip = data[0].split(',')
    serverip = data[1].split(',')

    sql = """INSERT INTO %s(Time,IP, ClientPort, ServerPort, Method) VALUES (%s,%s, %d, %d, %s)""" % (
        table_name,
        "'"+data[3]+"'",
        clientip[0].replace('(', ''),
        int(clientip[1].replace(')', '')),
        int(serverip[1].replace(')', '')),
        "'"+request+"'"
    )

    try:
        lock.acquire()  # 上互斥鎖
        db.ping(True)  # MYSQL保持連線
        cursor = db.cursor()
        cursor.execute(sql)
        db.commit()
        lock.release()  # 下互斥鎖

    except Exception as e:
        print(e)


with open('ports.json', 'r') as jsonfile:
    ports = json.loads(jsonfile.read())
    jsonfile.close()

try:
    db = pymysql.connect(**db_settings)
except Exception as e:
    print(e)
    sys.exit(1)

for port in ports:
    t = threading.Thread(target=server, args=(port,))
    threads.append(t)

for t in threads:
    t.start()
