# -*- coding: utf-8 -*-
"""
Created on Sat Dec  9 21:50:19 2017

@author: FanXudong
"""


from socket import *
from tkinter import *
import configparser
import threading
import messageclass
import diffiehellman.diffiehellman as diff
import AES_128


class Receiver(object):
    def __init__(self, myconfig,connectionBefore, connectionAfter):
        self.address, self.port = self.config_construct(myconfig)
        self.IPfailed = False
        self.tcpSerSocket = self.creatMySockets()
        self.connectionBefore=connectionBefore
        self.connectionAfter=connectionAfter
        self.key_id_key = {}
        self.diffkey=diff.DiffieHellman()
        self.aeskey=''


        t = threading.Thread(target=self.listen, args=(self,))
        t.start()

    def config_construct(self, file):
        config = configparser.ConfigParser()
        config.read(file)
        ip = config['host']['ip']
        port = int(config['host']['port'])
        return ip,port

    def creatMySockets(self):
        fixHOST = '127.0.0.1'   # if listening socket starts failed use localhost instead

        ADDR1 = (self.address, self.port)
        tcpSerSocket = socket(AF_INET, SOCK_STREAM)  # create listening socket

        try:
            tcpSerSocket.bind(ADDR1)  # bind address to listening socket
        except:
            print('Bob failed to start socket at address: ' + self.address)
            ADDR2 = (fixHOST, self.port)
            print('Bob uses local host instead, listening on: ' + str(ADDR2))
            self.IPfailed=True
            tcpSerSocket.bind(ADDR2)
        return tcpSerSocket

    
    def sendRsp(self, message,type='forward'):
        fixHOST = '127.0.0.1'  # if listening socket starts failed use localhost instead

        if type=='forward':
            # broadcast to successive nodes
            for addr in self.connectionAfter:
                if self.IPfailed==True:
                    ADDR1 = (fixHOST, addr[1])
                else:
                    ADDR1=addr
                tcpClientSocket = socket(AF_INET, SOCK_STREAM)
                tcpClientSocket.connect(ADDR1)
                tcpClientSocket.sendall(message.encode())
                tcpClientSocket.close()

        else:
            # broadcast to precedent nodes
            for addr in self.connectionBefore:
                if self.IPfailed==True:
                    ADDR1 = (fixHOST, addr[1])
                else:
                    ADDR1=addr
                tcpClientSocket = socket(AF_INET, SOCK_STREAM)
                tcpClientSocket.connect(ADDR1)
                tcpClientSocket.sendall(message.encode())
                tcpClientSocket.close()
                print('Bob sent data to destination: ' + str(ADDR1) + '\n')
    def checkData(self,data):
        msgdecoder = messageclass.message()
        try:
            datadecoded = msgdecoder.decode_message(data.decode())
            if datadecoded[0] == 0:  # is key init msg

                if datadecoded[1] == self.address and self.diffkey.key_id != int(datadecoded[2]):
                    print('Bob received: key init msg')
                    self.diffkey.key_id = int(datadecoded[2])
                    self.diffkey.generator = datadecoded[3]
                    self.diffkey.prime = datadecoded[4]
                    self.diffkey.generate_private_key()
                    self.diffkey.generate_public_key()
                    self.diffkey.generate_shared_secret(datadecoded[5])
                    self.aeskey = self.diffkey.shared_key[:16]
                    print('Bob calculated shared secret: ' + str(self.aeskey))
                    B = self.diffkey.public_key
                    sendMode = 'backward'
                    destination = '172.16.1.1'
                    keyRespose = msgdecoder.create_KeyReply(destination, datadecoded[2], B)
                    self.sendRsp(keyRespose, sendMode)

            if datadecoded[0] == 2:  # is msg relay

                seq_num = datadecoded[1]
                key_id = datadecoded[2]
                chiperPart = datadecoded[3]
                if key_id == self.diffkey.key_id:
                    AESObj = AES_128.AES_128(self.aeskey)
                    decruptxt = AESObj.decrypt(chiperPart)

                    nextHob = str(int(decruptxt[0:8], 2)) + '.' + str(int(decruptxt[8:16], 2)) + '.' + str(
                        int(decruptxt[16:24], 2)) + '.' + str(int(decruptxt[24:32], 2))

                    if nextHob == self.address:
                        receivedmsg = decruptxt[32:]

                        print('Bob: My name is Bob, I hereby certify that I received a message: ' + str(receivedmsg))
                        print('Bob: YEAH! ')
                else:
                    errormsg = msgdecoder.create_Error(1, 99)
                    sendMode = 'backward'
                    self.sendRsp(errormsg, sendMode)
        except:
            errormsg = msgdecoder.create_Error(0, 99)
            sendMode = 'backward'
            self.sendRsp(errormsg, sendMode)



    def listen(self,theSystem=''):
        self.tcpSerSocket.listen(10)

        while True:  # waiting foe client connection

            temClientsocket, addr = self.tcpSerSocket.accept()
            dataEnsemble = b''

            while True:
                data = temClientsocket.recv(1024)

                if data:
                    dataEnsemble+=data
                else:
                    temClientsocket.close()
                    break
            self.checkData(dataEnsemble)




    
    
    

