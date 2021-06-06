#!/usr/bin/python3
import socket
import sys

host = '127.0.0.1'
port = 10001

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
        continue

    if len(req_field) == 1 :
        if cmd.upper() == 'QUIT':
            break
        else :
            print("Unknown Command... ")
            continue

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (host, port)
        sock.connect(server_address)
    except:
        print("connection failed...")
        sys.exit(0)

    if cmd.upper() == 'GET' :
        # make a request line and send it
        message = cmd + ' ' + filename + '\n'
        sock.sendall(message.encode())

        # make a file stream out of data socket
        sd = sock.makefile('r')
        # read response line
        resp_line = sd.readline()
        code, phrase = resp_line.split()

        if code == '100' :
            # read the split line between response line and message body
            sd.readline()
            # server sent the requested file, create a file and save it
            fd = open(filename, 'w')
            data = sd.readline()
            while data:
                fd.write(data)
                data = sd.readline()

            print("vsftp> File Received Successfully")
            fd.close()
            sd.close()

        elif code == '400' :
            print("vsftp> File Not Found")
        else :
            pass

    elif cmd.upper() == 'PUT' :
        print("Command Not Implemented... ")
        # PUT command code
    else :
        print("Unknown Command... ")

    sock.close()

print("Bye!")
