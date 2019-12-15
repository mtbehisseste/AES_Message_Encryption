#!/usr/bin/env python
import socket 
import select 
import sys 
import math
from thread import *
from aes import AES

if len(sys.argv) != 3: 
    print "Usage: python server.py [IP address] [Port number]"
    exit() 

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
IP_address, Port = str(sys.argv[1]), int(sys.argv[2]) 
server.bind((IP_address, Port)) 
server.listen(5) 

aes_key = 0x2b7e151628aed2a6abf7158809cf4f3c

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

def recvClientThread(client, addr): 
    while True: 
        messageRecvEnc = client.recv(2048)
        if messageRecvEnc:
            print("\033[92mEncrytped message received:\033[0;0m {}".format(messageRecvEnc))
            messageRecvEnc = messageRecvEnc.split('0x')[1:]  # strip first index which is empty
            messageRecvDec = ''
            for msg in messageRecvEnc:
                s = int(msg, 16)
                messageRecvDec += numToString(str(aes.decrypt(s)))
            print "\033[1;33m<Client says> \033[0;0m" +  messageRecvDec.replace('*', '')        

def sendClientThread(client, addr):
    while True:
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
        client.send(messageSendEnc)

while True: 
    conn, addr = server.accept() 

    aes = AES(aes_key)

    print "\033[92m{} Connected!\033[0;0m".format(addr[0])  # addr[0] stands for the IP address

    start_new_thread(recvClientThread,(conn,addr))     
    start_new_thread(sendClientThread,(conn,addr))

conn.close() 
server.close() 
