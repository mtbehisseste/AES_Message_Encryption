#!/usr/bin/env python 
import socket 
import select 
import sys 
import math
from aes import AES

if len(sys.argv) != 3: 
    print "Usage: python server.py [IP address] [Port number]"
    exit() 
    
IP_address, Port = str(sys.argv[1]), int(sys.argv[2]) 
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.connect((IP_address, Port)) 
print("\033[92mConnection to server established!\033[0;0m")

aes_key = 0x2b7e151628aed2a6abf7158809cf4f3c
aes = AES(aes_key)

def stringToNum(s):
    tmp = 0
    for index, i in enumerate(s):
       tmp += (ord(i) << 8 * (16-index-1)) 
    return tmp

def numToString(num):
    num = hex(int(num))
    s = ''
    for i in range(2, 33, 2):
        s += chr(int(num[i] + num[i+1], 16))
    return s

while True: 
    sockets_list = [sys.stdin, server] 
    read_sockets, write_socket, error_socket = select.select(sockets_list,[],[]) 

    for socks in read_sockets: 
        if socks == server: 
            messageRecvEnc = server.recv(2048)
            if messageRecvEnc:
                print("\033[92mEncrytped message received:\033[0;0m {}".format(messageRecvEnc))
                messageRecvEnc = messageRecvEnc.split('0x')[1:]  # strip first index which is empty
                messageRecvDec = ''
                for msg in messageRecvEnc:
                    s = int(msg, 16)
                    messageRecvDec += numToString(str(aes.decrypt(s)))
                print "\033[1;31m<Server says> \033[0;0m" +  messageRecvDec.replace('*', '')

        else: 
            message = sys.stdin.readline()
            message = message.strip('\n')
            messageSendEnc = '' 
            for i in range(int(math.ceil(len(message) / 16.))):
                if len(message) < 16:
                    s = message + '*' * (16 - len(message))
                else:
                    s = message[0:16]
                messageSendEnc += hex(aes.encrypt(stringToNum(s))).rstrip('L')
                message = message[16:]

            print("\033[92mMessage encryted as:\033[0;0m {}".format(messageSendEnc))
            server.send(messageSendEnc)
server.close() 

