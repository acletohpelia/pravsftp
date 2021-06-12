#!/usr/bin/python3
import socket
import sys
import os
import time
#mput text.txt text1.txt text2.txt
host = '127.0.0.1'
port = 10001
print("Typing help")
while True :
    request = input("vsftp> ")
    req_field = request.split()

    # process user command
    if len(req_field) == 1 :
        cmd = req_field[0]
    elif len(req_field) == 2 :
        cmd = req_field[0]
        filename = req_field[1]
    else :
        cmd = req_field[0]
        filename = req_field[1]

    if len(req_field) == 1 :
        if cmd.upper() == 'QUIT':
            break
        elif cmd.upper() == 'EXIT':
            break
        elif cmd.upper() == "LS":
            pass
        elif cmd.upper() == "LSC":
            pass
        elif cmd.upper() == "HELP":
            print("Usage : vsftp>[command] [filename] [filename] ...")
            print("\tGET :\t>GET\t[filename]\t\t원격지 폴더에서 파일을 다운로드 합니다.")
            print("\tPUT :\t>PUT\t[filename]\t\t원격지 폴더에 파일을 업로드 합니다.")
            print("\tMGET :\t>MGET\t[filename..]\t원격지 폴더에서 여러개 파일을 다운로드 합니다.")
            print("\tMPUT :\t>MPUT\t[filename..]\t원격지 폴더에 여러개 파일을 업로드 합니다.")
            print("\tDEL :\t>DEL\t[filename]\t\t원격지 폴더안의 파일 리스트를 가져옵니다.")
            print("\tLS :\t>LS\t\t[N/A]\t\t\t원격지 폴더안의 파일 리스트를 가져옵니다.")
            print("\tLSC :\t>LS\t\t[N/A]\t\t\t로컬폴더안의 파일 리스트를 가져옵니다.")
            print("\tHELP : \t>HELP\t[N/A]\t\t\t사용법을 출력합니다.")
            print("\tQUIT : \t>QUIT\t[N/A]\t\t\t프로그램을 종료 합니다.[quit, exit]")
            continue
        else :
            print("Unknown Command...Typing help ")
            continue

    try:
        usock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (host, port)
        usock.connect(server_address)
    except:
        print("connection failed...")
        sys.exit(0)
    #이하 함수 다중파일 전송을 위해 분리
    def funcGet(fname, mtrig, msock):
        retmsg = 0
        stime = time.time()
        # make a request line and send it
        if mtrig == 0:
            message = cmd + ' ' + fname + '\n'
            sock = usock
        elif mtrig == 1:
            message = 'get ' + fname + '\n\n'
            sock = msock
            sock.connect(server_address)
        sock.sendall(message.encode())
        # make a file stream out of data socket
        sd = sock.makefile('r')
        # read response line
        resp_line = sd.readline()
        code, phrase = resp_line.split()

        if code == '100':
            # read the split line between response line and message body
            sd.readline()
            # server sent the requested file, create a file and save it
            fd = open(fname, 'w')
            data = sd.readline()
            while data:
                fd.write(data)
                data = sd.readline()
            fd.close()
            resultmsg = "FileSize : " + str(round((os.path.getsize(fname) / 1024), 2)) + "KB"
            resultmsg = resultmsg + "\nExecutionTime : " + str(round((time.time() - stime), 4))
            if mtrig == 0:
                print("vsftp> File Received Successfully")
                print("_________________________________")
                print(resultmsg)
                print("_________________________________\n")
            elif mtrig == 1:
                retmsg = fname + "->File Received Successfully"

            sd.close()

        elif code == '400':
            if mtrig == 0:
                print("vsftp> File Not Found")
            elif mtrig == 1:
                retmsg = fname + "->File Not Found"
        else:
            pass
        return retmsg
    def funcPut(fname, mtrig, msock):
        retmsg = 0
        try:
            fd = open(fname, 'r')
            code = '100'
        except:
            code = '400'

        if code == '100':
            if mtrig == 0:
                message = cmd + ' ' + fname + '\n\n'
                sock = usock
            elif mtrig == 1:
                message = 'put ' + fname + '\n\n'
                sock = msock
                sock.connect(server_address)
            # sock.sendall(message.encode())
            body = fd.read()
            body = body + "\nEOF\n"
            fd.close()
            # sock.sendall(body.encode())
            sd = sock.makefile('r')
            td = sock.makefile('w')
            td.write(message)
            td.write(body)
            td.flush()
            td.close()
            if mtrig == 0:
                print("vsftp>File upload completed\n")
            # read response line
            resp_line = sd.readline()
            code, phrase = resp_line.split()
            resmsg = sd.readline()
            resmsg = sd.readline()
            resfilesize = sd.readline()
            resEtime = sd.readline()
            if mtrig == 0:
                print("_________________________________")
                print("Server -> Client ")
                print("code : " + code + " --> " + phrase)
                print("Messege : " + resmsg + resfilesize + resEtime)
                print("_________________________________\n")
            elif mtrig == 1:
                retmsg = fname + "->File upload completed"
                sock.close()

            sd.close()


        elif code == '400':
            if mtrig == 0:
                print("File Not Found")
            elif mtrig == 1:
                retmsg = fname + "->File Not Found"
        else:
            pass
        return retmsg
    if cmd.upper() == 'GET':
        funcGet(filename, 0, 0)
    elif cmd.upper() == 'PUT':
        funcPut(filename, 0, 0)
    elif cmd.upper() == 'MGET':
        resultstr = ''
        sockli = []
        for j in range(1, len(req_field)):
            sockli.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        for i in range(1, len(req_field)):
            resultstr = resultstr + funcGet(req_field[i], 1, sockli[i - 1]) + "\n"
        print(resultstr)
    elif cmd.upper() == 'MPUT':
        resultstr = ''
        sockli = []
        for j in range(1, len(req_field)):
            sockli.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        for i in range(1, len(req_field)):
            resultstr = resultstr + funcPut(req_field[i], 1, sockli[i-1]) + "\n"
        print(resultstr)
    elif cmd.upper() == 'LS':
        sd = usock.makefile('r')
        message = cmd + ' NA' + '\n'
        usock.sendall(message.encode())
        rescode = sd.readline()
        code, phrase = rescode.split()
        resdata = sd.readline()
        resdata = sd.readline()
        print("_________________________________")
        print("Server -> Client ")
        print("code : " + code + " --> " + phrase)
        print("Files Dir:" + resdata + "---------")
        for rd in sd:
            print("\t" + rd, end='')
        print("\n_________________________________\n")
        sd.close()
    elif cmd.upper() == 'LS':
        sd = usock.makefile('r')
        message = cmd + ' NA' + '\n\n'
        usock.sendall(message.encode())
        rescode = sd.readline()
        code, phrase = rescode.split()
        resdata = sd.readline()
        resdata = sd.readline()
        print("_________________________________")
        print("Server -> Client ")
        print("code : " + code + " --> " + phrase)
        print("Files Dir:" + resdata + "---------")
        for rd in sd:
            print("\t" + rd, end='')
        print("\n_________________________________\n")
        sd.close()
    elif cmd.upper() == 'DEL':
        sd = usock.makefile('r')
        message = 'DEL ' + filename + '\n\n'
        usock.sendall(message.encode())
        rescode = sd.readline()
        code, phrase = rescode.split()

        print("_________________________________")
        print("Server -> Client ")
        print("code : " + code + " --> " + phrase)
        print("_________________________________")
        sd.close()
    elif cmd.upper() == 'LSC':
        dirlist = os.listdir("./")
        print("_________________________________")
        print("Filelist ---------")
        for dl in dirlist:
            print("\t" + dl)
        print("_________________________________\n")
    else :
        print("Unknown Command... ")


    usock.close()

print("Bye!")
