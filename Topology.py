# -*- coding: utf-8 -*-
"""
Created on Sat Dec  9 21:51:19 2017

@author: Hzhao
"""

import configparser
import random

class Topology(object):
    """
    This class contains the list of all relays and the topology.
    Each line of the topology contains the IP of a relay and the IP list of its neighbours.
    """
    def __init__(self):
        self.nodes = set()
        self.connections = dict()
        self.costs = dict()
        self.connections_before=dict()
        self.connections_after=dict()

    def config_construct(self, file='config/topology.ini'):
        config = configparser.ConfigParser()
        config.read(file)     
        for relay in config['relays']:
            ip, port = config['relays'][relay].split(' ')
            self.nodes.add(ip)

        for link in config['topology']:
            link = config['topology'][link].split(' ')
            self.connections[link[0]] = link[1:]          
        self.cost()
    
    # Set randomly the cost between relays
    def cost(self):
        for link in self.connections:
            connection_number = len(self.connections[link])
            for i in range(connection_number):
                if (link, self.connections[link][i]) not in self.costs and (self.connections[link][i], link) not in self.costs:
                    self.costs[link,self.connections[link][i]]=random.randint(1,16)
                else:
                    self.costs[link,self.connections[link][i]] = self.costs[self.connections[link][i],link]

    def getConnectionRelation(self):
        connections = self.connections
        connections_before = dict()
        connections_after = dict()
        keys = connections.keys()
        keys = list(keys)
        length = len(keys)


        #Get the connecters before the relay and after the relay

        nodes = set()
        for i in range(length):
            connection_number = len(connections[keys[i]])
            local_connection = connections[keys[i]]
            connection_node1 = set()
            connection_node2 = set()
            for j in range(connection_number):
                if local_connection[j] not in nodes:
                    connection_node1.add(local_connection[j])
                elif local_connection[j] in nodes:
                    connection_node2.add(local_connection[j])
            connection_node1 = list(connection_node1)
            connection_node2 = list(connection_node2)
            connections_after[keys[i]] = connection_node1[:]
            connections_before[keys[i]] = connection_node2[:]
            nodes.add(keys[i])

        self.connections_before=connections_before
        self.connections_after=connections_after
        return connections_before,connections_after
