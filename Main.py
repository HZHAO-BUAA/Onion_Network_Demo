# -*- coding: utf-8 -*-
"""
Created on Sat Dec  9 21:50:19 2017

@author: HZhao
"""

from Topology import Topology
import networkx as nx
import Sender
import threading
import Relay
import Receiver

iplist=['172.16.1.1','172.16.2.1','172.16.3.2','172.16.4.2','172.16.5.3','172.16.6.4','172.16.7.5','172.16.8.6']
portList=[9001,9009,9012,9002,9007,9008,9010,9013]
fixHOST = '127.0.0.1'

Topology_1 = Topology()
Topology_1.config_construct('config/topology.ini')

connectionBefore, connectionAfter=Topology_1.getConnectionRelation()
RelaySet=[]

#start three relays
for idx in range(6):
    relayIP=iplist[idx+1]
    connectionBefore1=connectionBefore.get(relayIP)
    connectionAfter1=connectionAfter.get(relayIP)
    connectionAfterwithPort=[]
    for afterIP in connectionAfter1:
        connectionAfterwithPort.append((afterIP, portList[iplist.index(afterIP)]))

    connectionBeforewithPort = []
    for beforeIP in connectionBefore1:
        connectionBeforewithPort.append((beforeIP, portList[iplist.index(beforeIP)]))
    configFile='config/host_R'+str(idx+2)+'.ini'
    RelaySet.append(Relay.Relay(configFile,connectionBeforewithPort,connectionAfterwithPort,idx+2))


#startBob:
BobIP=iplist[7]
connectionBeforeB=connectionBefore.get(BobIP)
connectionAfterB=connectionAfter.get(BobIP)
connectionAfterwithPort = []
for afterIP in connectionAfterB:
    connectionAfterwithPort.append((afterIP, portList[iplist.index(afterIP)]))

connectionBeforewithPort = []
for beforeIP in connectionBeforeB:
    connectionBeforewithPort.append((beforeIP, portList[iplist.index(beforeIP)]))
configFile='config/host_Bob'+'.ini'
SenderBob=Receiver.Receiver(configFile,connectionBeforewithPort,connectionAfterwithPort)


#StartAlice:
AliceIP=iplist[0]
connectionBeforeA=connectionBefore.get(AliceIP)
connectionAfterA=connectionAfter.get(AliceIP)
connectionAfterwithPort = []
for afterIP in connectionAfterA:
    connectionAfterwithPort.append((afterIP, portList[iplist.index(afterIP)]))

connectionBeforewithPort = []
for beforeIP in connectionBeforeA:
    connectionBeforewithPort.append((beforeIP, portList[iplist.index(beforeIP)]))
configFile='config/host_Alice'+'.ini'
SenderAlice=Sender.Sender(configFile,connectionBeforewithPort,connectionAfterwithPort)




