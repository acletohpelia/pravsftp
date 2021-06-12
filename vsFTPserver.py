#!/usr/bin/python

import socket
import threading
import os
import time
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
        cmd = cmd.upper()
        if cmd == "GET":
            try:
                fd = open("./pwd/" + filename, 'r')
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
            # read the split line between response line and message body
            stime = time.time()
            sd.readline()
            # server sent the requested file, create a file and save it
            fd = open("./pwd/" + filename, 'w')
            for req in sd:
                if str(req) == "EOF\n":
                    print(req)
                    break
                fd.write(req)

            fd.close()
            fd = open("./pwd/" + filename, 'r')
            fdd = fd.read()
            fd.close()
            if os.path.isfile("./pwd/d" + filename):
                os.remove("./pwd/d" + filename)
            fdd = fdd[:-1]
            wfd = open("./pwd/" + filename, 'w')
            wfd.write(fdd)
            wfd.close()
            sd.close()
            resmessage = "100 FileSaved \n\nFile Received Successfully\n"
            resmessage = resmessage + "FileSize : " + str(round((os.path.getsize("./pwd/" + filename) / 1024), 2)) + "KB"
            resmessage = resmessage + "\nExecutionTime : " + str(round((time.time() - stime), 4))
            self.csocket.sendall(resmessage.encode())

            pass
        elif cmd == "LS":
            dirlist = os.listdir("./pwd/")
            resp_line = '300 FileListFetched' + '\n\n'
            self.csocket.sendall(resp_line.encode())
            body = '\n'.join(dirlist)
            body = "pwd\n" + body
            self.csocket.sendall(body.encode())
            pass
        elif cmd == "DEL":
            try:
                os.remove("./pwd/" + filename)
                resp_line = '301 FileisDeleted' + '\n\n'
            except:
                resp_line = '400 Not_Found' + '\n\n'


            self.csocket.sendall(resp_line.encode())
            pass
        else:
            print("not worked")
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