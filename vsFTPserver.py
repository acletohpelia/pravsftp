#!/usr/bin/python

import socket
import threading
import sys

buff_size = 128


class EchoThread(threading.Thread):

    def __init__(self, socket, address):
        threading.Thread.__init__(self)
        self.ip, self.port = address
        self.csocket = socket
        print("[+] New service thread started for %s" % self.ip)

    def run(self):
        sd = self.csocket.makefile('r')
        req_line = sd.readline()

        if req_line:
            cmd, filename = req_line.split()
        else:
            cmd = "void"

        if cmd == "get":
            try:
                fd = open(filename, 'r')
                code = '100'
            except:
                code = '400'

            if code == '100':
                resp_line = code + ' ' + 'OK' + '\n\n'
                self.csocket.sendall(resp_line.encode())
                body = fd.read()
                self.csocket.sendall(body.encode())
                fd.close()
                sd.close()
            elif code == '400':
                resp_line = code + ' ' + 'Not_Found' + '\n\n'
                self.csocket.sendall(resp_line.encode())
                sd.close()
            else:
                pass

        elif cmd == "PUT":
            pass

        else:
            pass

        self.csocket.close()
        print("[-] Service thread terminated for %s " % self.ip)


host = ''
port = 10001
BACKLOG = 5

conn_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
conn_sock.bind((host, port))
conn_sock.listen(BACKLOG)

while True:
    print("listening for incoming requests...")
    data_sock, client_address = conn_sock.accept()
    serviceThread = EchoThread(data_sock, client_address)
    serviceThread.setDaemon(True)
    serviceThread.start()