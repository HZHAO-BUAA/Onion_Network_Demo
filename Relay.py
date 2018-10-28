# -*- coding: utf-8 -*-
"""
Created on Sat Dec  9 21:50:19 2017

@author: HZhao
"""
import configparser
from socket import *
import threading
import messageclass
import diffiehellman.diffiehellman as diff
import AES_128

class Relay:
    def __init__(self, myconfig,connectionBefore, connectionAfter,relayID):
        self.key_id_key = {}
        self.IPfailed = False
        self.myID = relayID
        self.address,self.port=self.config_construct(myconfig)
        self.tcpSerSocket = self.creatMySockets()
        self.connectionBefore=connectionBefore
        self.connectionAfter=connectionAfter
        self.diffkey=diff.DiffieHellman()
        self.aeskey=''

        t = threading.Thread(target=self.listen, args=(self,))
        t.start()

    # constructing internal parameters according to configuration file
    def config_construct(self, file = 'config/host_R2.ini'):
        config = configparser.ConfigParser()
        config.read(file)
        ip = config['host']['ip']
        port = int(config['host']['port'])
        return ip,port

    def creatMySockets(self):
        fixHOST = '127.0.0.1'  # if listening socket starts failed use localhost instead

        ADDR1 = (self.address, self.port)
        tcpSerSocket = socket(AF_INET, SOCK_STREAM)  # create socket

        try:
            tcpSerSocket.bind(ADDR1)  # bind address to listening socket
        except:
            print('Relay ' + str(self.myID) + ' failed to start socket at address: ' + self.address)
            ADDR2 = (fixHOST, self.port)

            print('Relay ' + str(self.myID) + ' uses local host instead, listening on: ' + str(ADDR2))

            tcpSerSocket.bind(ADDR2)
            self.IPfailed = True
        tcpSerSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        return tcpSerSocket
        


    def sendRsp(self, message,type='forward',dest=0):
        fixHOST = '127.0.0.1' # if listening socket starts failed use localhost instead

        if type=='forward':
            # broadcast to successive nodes
            for addr in self.connectionAfter:
                if self.IPfailed==True:
                    ADDR1 = (fixHOST, addr[1])
                else:
                    ADDR1=addr
                tcpClientSocket = socket(AF_INET, SOCK_STREAM)
                try:
                    tcpClientSocket.connect(ADDR1)
                    tcpClientSocket.sendall(message.encode())
                    tcpClientSocket.close()
                except:
                    print('Relay ' + str(self.myID) + ' forward socket connection time out\n')

        if type == 'backward':
            #broadcast to precedent nodes
            for addr in self.connectionBefore:
                try:

                    tcpClientSocket = socket(AF_INET, SOCK_STREAM)

                    if self.IPfailed == True:
                        ADDR1 = (fixHOST, addr[1])
                    else:
                        ADDR1 = addr
                    tcpClientSocket.connect(ADDR1)
                    tcpClientSocket.sendall(message.encode())

                    tcpClientSocket.close()
                except:
                    print('Relay ' + str(self.myID) + ' backward socket connection time out\n')
        if type == 'P2P':
            # broadcast to a certain node
            try:
                tcpClientSocket = socket(AF_INET, SOCK_STREAM)
                if self.IPfailed==True:
                    ADDR1 = (fixHOST, dest[1])
                else:
                    ADDR1=dest
                tcpClientSocket.connect(ADDR1)
                tcpClientSocket.send(message.encode())

                tcpClientSocket.close()
            except:
                print('Relay ' + str(self.myID) + ' P2P socket connection time out\n')


    def checkReceivedData(self,datadecoded,data):
        msgdecoder = messageclass.message()
        if datadecoded[0] == 0:  # is key init msg


            if datadecoded[1] == self.address and self.diffkey.key_id != int(datadecoded[2]):
                print('Relay ' + str(self.myID) + ' received: key init msg')
                self.diffkey.key_id = int(datadecoded[2])
                self.diffkey.generator = datadecoded[3]
                self.diffkey.prime = datadecoded[4]
                self.diffkey.generate_private_key()
                self.diffkey.generate_public_key()
                self.diffkey.generate_shared_secret(datadecoded[5])
                self.aeskey = self.diffkey.shared_key[:16]
                B = self.diffkey.public_key

                print('Relay ' + str(self.myID) + ' calculated shared secret: ' + str(self.aeskey))
                sendMode = 'backward'
                destination = '172.16.1.1'
                keyRespose = msgdecoder.create_KeyReply(destination, datadecoded[2], B)
                self.sendRsp(keyRespose, sendMode)
            if datadecoded[1] != self.address:
                sendMode = 'forward'
                self.sendRsp(data.decode(), sendMode)
        if datadecoded[0] == 1:  # is key reply msg
            sendMode = 'backward'
            self.sendRsp(data.decode(), sendMode)
        if datadecoded[0] == 2:  # is msg relay

            seq_num = datadecoded[1]
            key_id = datadecoded[2]
            chiperPart = datadecoded[3]
            if key_id == self.diffkey.key_id:
                AESObj = AES_128.AES_128(self.aeskey)
                decruptxt = AESObj.decrypt(chiperPart)

                nextHob = str(int(decruptxt[0:8], 2)) + '.' + str(int(decruptxt[8:16], 2)) + '.' + str(
                    int(decruptxt[16:24], 2)) + '.' + str(int(decruptxt[24:32], 2))
                for addr in self.connectionAfter:
                    if addr[0] == nextHob:
                        sendMode = 'P2P'
                        forwardmsg = decruptxt[32:]
                        self.sendRsp(forwardmsg, sendMode, dest=addr)
            else:
                errormsg = msgdecoder.create_Error(1, self.myID)
                sendMode = 'backward'
                self.sendRsp(errormsg, sendMode)
        if datadecoded[0] == 3:  # is error msg
            sendMode = 'backward'
            self.sendRsp(data.decode(), sendMode)



    def listen(self,theSystem=''):
        self.tcpSerSocket.listen(10)


        while True:  # waiting for client connection

            temClientsocket, addr = self.tcpSerSocket.accept()

            dataEnsemble=b''
            while True:
                data = temClientsocket.recv(1024)

                if data.decode():
                    dataEnsemble+=data
                else:
                    temClientsocket.close()
                    break
            if dataEnsemble:
                msgdecoder = messageclass.message()
                try:
                    datadecoded = msgdecoder.decode_message(dataEnsemble.decode())
                    self.checkReceivedData(datadecoded, dataEnsemble)
                except:
                    errormsg = msgdecoder.create_Error(0, self.myID)
                    sendMode = 'backward'
                    self.sendRsp(errormsg, sendMode)









