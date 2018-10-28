# -*- coding: utf-8 -*-
"""
Created on Sat Dec  9 21:50:19 2017

@author: Hzhao
"""


from socket import *
from tkinter import *
import configparser
import threading
import Topology
import networkx as nx
import diffiehellman.diffiehellman as diff
import random
import messageclass
import queue


class Sender(object):
    def __init__(self, myconfig,connectionBefore, connectionAfter):
        self.iplist = ['172.16.1.1', '172.16.2.1', '172.16.3.2', '172.16.4.2', '172.16.5.3','172.16.6.4','172.16.7.5','172.16.8.6']
        self.nameList=['Alice','Relay 2','Relay 3','Relay 4','Relay 5','Relay 6','Relay 7','Bob']
        self.portList = [9001, 9009, 9012, 9002, 9007, 9008, 9010, 9013]
        self.root = Tk()
        self.root.title('Alice')
        self.createWindow(self.root)
        self.keyIDReceivedList=[]
        self.keyMessageQueue=queue.Queue()
        self.path=dict()
        self.IPfailed=False


        self.address, self.port = self.config_construct(myconfig)
        self.tcpSerSocket = self.creatMySocket()
        self.connectionBefore=connectionBefore
        self.connectionAfter=connectionAfter
        self.keyList = []
        self.keyIDList = []

        t = threading.Thread(target = self.listen, args = (self,))
        t.start()

        self.root.mainloop()


    def config_construct(self, file):
        config = configparser.ConfigParser()
        config.read(file)
        ip = config['host']['ip']
        port = int(config['host']['port'])
        return ip,port

    def creatMySocket(self):
        fixHOST = '127.0.0.1'  # If listening socket launch failed, use localhost instead

        ADDR1 = (self.address, self.port)
        tcpSerSocket = socket(AF_INET, SOCK_STREAM)  # create listening socket

        try:
            tcpSerSocket.bind(ADDR1)  # bind address to socket
        except:
            print('Alice failed to start socket at address: ' + self.address)
            ADDR2 = (fixHOST, self.port)
            print('Alice uses localhost instead, listening on: ' + str(ADDR2))
            tcpSerSocket.bind(ADDR2)
            self.IPfailed=True
        return tcpSerSocket

    def createWindow(self, root):
        # text label
        self.lbin = Label(root, text='Input message to Bob: ')
        self.lbin.grid(row=0, column=0, columnspan=2)

        # input message text bar
        self.Data = StringVar()
        self.entry = Entry(root, width=50, textvariable=self.Data)
        self.entry.grid(row=1, column=0, columnspan=2)
        # text label
        self.lbin = Label(root, text='Normal Operation',fg = "blue")
        self.lbin.grid(row=2, column=0)
        self.lbin = Label(root, text='Exception handling test',fg = "blue")
        self.lbin.grid(row=2, column=1)

        # normal send

        self.btsend = Button(root, text='Send msg to Bob', command = lambda: self.sendMsg(self.path,self.keyList,self.keyIDList,self.Data.get()))
        self.btsend.grid(row=3, column=0)

        # abnormal send

        self.btsend = Button(root, text='Send using invalid KeyID',
                             command=lambda: self.sendMsg(self.path, self.keyList, self.path, self.Data.get()))
        self.btsend.grid(row=3, column=1)

        self.btsend = Button(root, text='Calc. direction and distribute key', command=self.distributeKey)
        self.btsend.grid(row=4, column=0)

        self.btsend = Button(root, text='Send invalid format msg',
                             command=lambda: self.sendInvalidMsg(self.path))
        self.btsend.grid(row=4, column=1)

        # log display
        self.textout = Text(root,borderwidth = 3)
        self.textout.grid(row=5, column=0, columnspan=2,
                          sticky=(W, E, N, S), padx=10, pady=10, ipadx=10, ipady=10)


    def sendMsg(self,path,keyList,keyIDList,message,destination=''):
        fixHOST = '127.0.0.1'

        if not message:
            self.textout.insert(END, 'Nothing to send, please input message to monsieur Bob to text box' + '\n')
            return
        if not path:
            self.textout.insert(END,"Please firstly click 'calc. direction and distribute key' bottom "+'\n')
        else:
            for node in range(len(path)-1):


                hob_key=keyList[-(node+1)].shared_key[:16] #AESkey
                hob_keyID = keyIDList[-(node + 1)]
                if node==0:
                    hob_num = path[-1]  # node number
                    hob_IP=self.iplist[hob_num-1]
                else:
                    hob_num = path[-(node)]  # node number
                    hob_IP = self.iplist[hob_num - 1]
                messagetreator=messageclass.message()
                message=messagetreator.create_MessageRelay(hob_keyID,hob_IP,node,message,hob_key)
            hob_num = path[1]  # node number
            nextHobAlice = self.iplist[hob_num - 1]

            senderIdx=self.iplist.index(nextHobAlice)
            if self.IPfailed:
                ADDR1 = (fixHOST, self.portList[senderIdx])
            else:
                ADDR1 = (nextHobAlice, self.portList[senderIdx])
            tcpClientSocket = socket(AF_INET, SOCK_STREAM)

            tcpClientSocket.connect(ADDR1)
            tcpClientSocket.sendall(message.encode())
            tcpClientSocket.close()
            self.textout.insert(END,
                                'Sent relay msg to next hob: ' + str(nextHobAlice) + ' represented by: ' + str(ADDR1) + '\n')

    def sendInvalidMsg(self,path):
        fixHOST = '127.0.0.1'
        message='this is a invalid message'
        if not path:
            self.textout.insert(END,"Please firstly click 'calc. direction and distribute key' bottom "+'\n')
        else:
            hob_num = path[1]  # node number
            nextHobAlice = self.iplist[hob_num - 1]

            senderIdx = self.iplist.index(nextHobAlice)
            if self.IPfailed:
                ADDR1 = (fixHOST, self.portList[senderIdx])
            else:
                ADDR1 = (nextHobAlice, self.portList[senderIdx])
            tcpClientSocket = socket(AF_INET, SOCK_STREAM)

            tcpClientSocket.connect(ADDR1)
            tcpClientSocket.sendall(message.encode())
            tcpClientSocket.close()
            self.textout.insert(END,
                                'Sent invalid msg to next hob: ' + str(nextHobAlice) + ' represented by: ' + str(
                                    ADDR1) + '\n')



    def sendKeyInitMsg(self):
        fixHOST = '127.0.0.1'
        if not self.keyMessageQueue.empty():
            data = self.keyMessageQueue.get()

            for addr in self.connectionAfter:
                if self.IPfailed:
                    ADDR1 = (fixHOST, addr[1])
                else:
                    ADDR1=addr
                tcpClientSocket = socket(AF_INET, SOCK_STREAM)

                tcpClientSocket.connect(ADDR1)
                tcpClientSocket.send(data.encode())
                tcpClientSocket.close()
                self.textout.insert(END, 'Sent key initial msg to : ' +str(ADDR1)+ '\n')



    def listen(self,theSystem=''):
        self.tcpSerSocket.listen(10)

        # waiting for connection
        while True:

            temClientsocket, addr = self.tcpSerSocket.accept()

            while True:
                data = temClientsocket.recv(4096)
                if data:
                    datadecoder=messageclass.message()
                    decodeddata=datadecoder.decode_message(data)
                    if decodeddata[0]==0:
                        self.textout.insert(END, 'Alice Received： '+str('Key init msg') + '\n')
                    if decodeddata[0]==1:
                        nodeNum = self.keyIDList.index(int(decodeddata[2]))

                        if self.keyIDReceivedList[nodeNum]==0:



                            self.keyList[nodeNum].generate_shared_secret(decodeddata[3])
                            self.keyIDReceivedList[nodeNum] = 1
                            targetAESKey = self.keyList[nodeNum].shared_key[:16]
                            self.textout.insert(END, 'Key reply msg from: ' + self.nameList[self.path[nodeNum + 1]-1] + ' Shared secret (AES key): ' + str(
                                targetAESKey) + '\n')
                            self.sendKeyInitMsg()
                            if sum(self.keyIDReceivedList) == len(self.keyIDList):
                                self.textout.insert(END, 'All key replies received ' + '\n')
                    if decodeddata[0]==3:
                        error_code=decodeddata[1]
                        expNode=decodeddata[2]
                        if error_code==1:
                            self.textout.insert(END, 'Invalid KeyID error from Node ' + str(expNode)+'\n')
                        if error_code==0:
                            self.textout.insert(END, 'Message decode error from Node ' + str(expNode)+'\n')

                else:
                    break

            temClientsocket.close()



    def ClickRadiobutton(self):
        pass
    def distributeKey(self):
        Topology_1 = Topology.Topology()
        Topology_1.config_construct('config/topology.ini')

        G1 = nx.DiGraph()
        G1.add_edge(1, 2, weight=Topology_1.costs.get(('172.16.1.1', '172.16.2.1')))
        G1.add_edge(2, 5, weight=Topology_1.costs.get(('172.16.2.1', '172.16.5.3')))
        G1.add_edge(2, 6, weight=Topology_1.costs.get(('172.16.2.1', '172.16.6.4')))
        G1.add_edge(2, 7, weight=Topology_1.costs.get(('172.16.2.1', '172.16.7.5')))

        G1.add_edge(5, 3, weight=Topology_1.costs.get(('172.16.5.3', '172.16.3.2')))


        G1.add_edge(5, 4, weight=Topology_1.costs.get(('172.16.5.3', '172.16.4.2')))
        G1.add_edge(7, 3, weight=Topology_1.costs.get(('172.16.7.5', '172.16.3.2')))

        G1.add_edge(7, 5, weight=Topology_1.costs.get(('172.16.7.5', '172.16.5.3')))

        G1.add_edge(6, 4, weight=Topology_1.costs.get(('172.16.6.4', '172.16.4.2')))
        G1.add_edge(4, 8, weight=Topology_1.costs.get(('172.16.4.2', '172.16.8.6')))
        G1.add_edge(3, 4, weight=Topology_1.costs.get(('172.16.3.2', '172.16.4.2')))



        self.path=self.dijkstra(G1,1,8)
        self.textout.insert(END, 'Random path to Bob： ' + str(self.path) + '\n')

        pathLength=len(self.path)
        self.keyList=[] #list of AES keys
        self.keyIDList=[] #list of keyIDs
        self.keyIDReceivedList=[] # indicates the receiving status of each key reply


        for idx in range(pathLength-1):
            key_id = random.randint(1, 1000000)
            NewKey = diff.DiffieHellman(key_id=key_id)
            NewKey.generate_private_key()
            NewKey.generate_public_key()
            self.keyList.append(NewKey)
            self.keyIDList.append(key_id)
            self.keyIDReceivedList.append(0)

            destination = self.iplist[self.path[idx + 1] - 1]  # get destination ip
            msgGenerator = messageclass.message()
            keyInitMsg = msgGenerator.create_KeyInit(destination, key_id, NewKey.generator, NewKey.prime,
                                                     NewKey.public_key)
            self.keyMessageQueue.put(keyInitMsg)
            if idx==0:
                self.sendKeyInitMsg()





    def dijkstra(self,G, start, end):
        RG = G.reverse()
        dist = {}
        previous = {}
        for v in RG.nodes():
            dist[v] = float('inf')
            previous[v] = 'none'
        dist[end] = 0
        u = end
        while u != start:
            u = min(dist, key=dist.get)
            distu = dist[u]
            del dist[u]
            for u, v in RG.edges(u):
                if v in dist:
                    alt = distu + RG[u][v]['weight']
                    if alt < dist[v]:
                        dist[v] = alt
                        previous[v] = u
        path = (start,)
        last = start
        while last != end:
            nxt = previous[last]
            path += (nxt,)
            last = nxt
        return path
    

