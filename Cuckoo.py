# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 14:35:30 2020

@author: Florian  Richter
"""

from pm4py.objects.log.log import EventLog, Trace
import numpy as np
from datetime import timezone


class Node():
    def __init__(self, caseid, trace, timestamp):
        self.caseid  = caseid 
        self.last_update = timestamp
        self.trace = trace

    def __str__(self):
        return "(" + str(self.caseid) + ", " + self.last_update + ", " + str(self.trace) + ")"
    
class HashTable():
    def __init__(self, height, width):
        self.__array = [[None for x in range(width)] for y in range(height)] 
        self.__numRecords = 0
        self.__width = width
        self.__height = height
        self.__size = width*height
        self.last_update = None
        
    def __len__(self): return self.__numRecords

    def hash_func(self, caseid):
        caseid = str(caseid)
        return hash(caseid) % self.__height, hash(caseid[::-1]) % self.__height
    

    def insert(self, event):
        caseid = event['caseid']
        timestamp = event['time:timestamp']
        h1,h2 = self.hash_func(event['caseid'])
        x1 = self.__array[h1]
        x2 = self.__array[h2]
        self.last_update = timestamp
        
        for i in range(self.__width):
            if x1[i] != None and x1[i].caseid == caseid:
                x1[i].trace.append(event)
                x1[i].last_update = timestamp
                return
            if x2[i] != None and x2[i].caseid == caseid:
                x2[i].trace.append(event)
                x2[i].last_update = timestamp
                return
        
        node = Node(caseid, [event], timestamp)
        self.rehash(node, h2, 10)

    def rehash(self, node, old_pos, rehashes):
        if rehashes == 0:
            return
        
        caseid = node.caseid
        #print("rehash", caseid, old_pos, rehashes)
        h1,h2 = self.hash_func(caseid)
        
    
        
        if h1 == old_pos:
            x = self.__array[h2]
            other_pos = h2
        else:
            x = self.__array[h1]
            other_pos = h1
    
        
        # Looking for empty space
        for i in range(self.__width):
            if x[i] == None:
                x[i] = node
                return
        
        #print("deprecation")
        # no empty space
        deprecation = []
        for i in range(self.__width):
            deprecation.append((x[i].last_update, i))
        deprecation.sort(key=lambda x:x[0])
        node_rehash = x[deprecation[0][1]]
        #print(node_rehash.caseid, node_rehash.last_update)
        #print(node.caseid, node.last_update)
        # maybe the actual node is older than all others? then discard
        if node.last_update < node_rehash.last_update:
            return
        
        x[deprecation[0][1]] = node
        node, node_rehash = node_rehash, node
        
        
        
        #rehash node
        self.rehash(node, other_pos, rehashes-1)


    def __str__(self):
        string = "Table: [ \n"
        for h in self.__array:
            string += "["
            for w in h:
                string += "   "
                if w == None:
                    string += str(None)
                else:
                    string += str(w.caseid) 
                
            string += "]\n"
        
        string += "]"
        return string




    def get_log(self):
        log = EventLog()
        for i in range(self.__height):
            for j in range(self.__width):
                node = self.__array[i][j]
                if node != None:
                    new_trace = Trace()
                    new_trace.attributes['concept:name'] = node.caseid
                    for event in node.trace:
                        new_trace.append(event)
                    log.append(new_trace)
        return log
        
    def get_temporal_stats(self):
        timestamps = []
        for i in range(self.__height):
            for j in range(self.__width):
                node = self.__array[i][j]
                if node != None:
                    timestamps.append((self.last_update-node.last_update).total_seconds())
        return np.mean(timestamps), np.std(timestamps)
        
        
        
        
        