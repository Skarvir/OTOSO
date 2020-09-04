# -*- coding: utf-8 -*-
"""
Created on Fri Jan  3 15:16:45 2020

@author: richter
"""

import itertools
import numpy as np
import pandas as pd
from pyclustering.cluster.optics import optics
from pm4py.objects.log.importer.xes import factory as xes_importer
import matplotlib.pyplot as plt
import Cuckoo


# parameters #
eps = 0.1           # max density for OPTICS
h = 100             # height of hash table
w = 10              # width of hash table
stepsize = 10000    # interval of result requests
##############


log = xes_importer.import_log("BPIC2017_Offer.xes")

def get_time(elem):
    return elem['time:timestamp']

def eventStream(log):
    es = []
    rels = {}
    for trace in log:
        cid = trace.attributes['concept:name']
        for event in trace:
            event['caseid'] = cid
            es.append(event)
            
        for (e1,e2) in list(itertools.combinations(trace, 2)):
            a1 = e1['concept:name']
            a2 = e2['concept:name']
            rels[a1+"->"+a2] = 1            
            
    es.sort(key=get_time)
    return es, list(rels.keys())

es, rels = eventStream(log)






def optics_plot(log, rels):

    d = {}
    Z = {}
    
    
    for trace in log:
        tid = trace.attributes['concept:name']
        
        
        z = {}
        for (e1,e2) in list(itertools.combinations(trace, 2)):
            a1 = e1['concept:name']
            t1 = e1['time:timestamp']
            a2 = e2['concept:name']
            t2 = e2['time:timestamp']
            
            rel = a1+"->"+a2
            
            
            diff = (t2 - t1).total_seconds()
            
    
            if rel in d:
                d[rel].append(diff)
            else:
                d[rel] = [diff]
    
            z[rel] = diff
            
        
        Z[tid] = z
    
    
    avg = {}
    std = {}
    ext = {}
    
    for rel, values in d.items():
        avg[rel] = np.mean(values)
        std[rel] = np.std(values)
        ext[rel] = np.max(np.abs(values))
        
    

    
    
    
    
        
    # standardizing
    Zstd = {}
    for tid, trace in Z.items():
        vstd = {}
        for rel, value in trace.items():
            vstd[rel] = (value-avg[rel])
            if std[rel] == 0:
                vstd[rel] = 0
            else:
                vstd[rel] /= std[rel]
        Zstd[tid] = vstd
        
        
    tids = Z.keys()
    
    Zvectors = []
    
    for tid in tids:
        temp = Zstd[tid]
        dummy = []
        for rel in rels:
            if rel in temp:
                dummy.append(temp[rel])
            else:
                #dummy.append(100.0)
                dummy.append(0.0)
        Zvectors.append(dummy)
            
    
    
    
    print("Number of traces: ", len(Zvectors))
    print("Number of relations: ", len(rels))
    
    
    
    
    
    optics_instance = optics(Zvectors, eps, 20)
    optics_instance.process()
    clusters = optics_instance.get_clusters()
    objects = optics_instance.get_optics_objects()


    
    reach = pd.Series(optics_instance.get_ordering())
    

    fig, ax1 = plt.subplots(figsize=(4,2),  dpi=100)
    plt.plot(reach, color='black')
    thresh = [eps]*len(reach)
    plt.plot(thresh, color='blue')
    ax1.fill_between(range(len(reach)), np.maximum(thresh, reach), reach, color='blue', alpha=0.3)
    plt.ylabel('Reachability Distance')
    plt.xlabel('Traces')
    plt.show()
    

    result = []
    for c in clusters:
        c_attr = [len(c)]
        c_attr.append(np.average([(objects[item]).reachability_distance for item in c if (objects[item]).reachability_distance != None]))
        c_attr.append(np.mean([Zvectors[i] for i in c], axis=0))
        result.append(c_attr)
    
    return result

    
    
    
def cluster_member(xs,eps):
    result = []
    candidate = []
    for i in range(len(xs)):
        if xs[i] < eps:
            candidate.append(i)
        elif candidate != list():
            result.append(candidate)
            candidate = []
    return result
    
    
c = Cuckoo.HashTable(h,w)

dots_t = []
dots_n = []
dots_density = []
dots_representation = []

j = 0
ticks = []
for i in es:
    c.insert(i)
    j += 1
    if j%stepsize == 0:
        print("j:", j)
        ticks.append(j)
        clusters = optics_plot(c.get_log(), rels)
        for n,d,r in clusters:
            dots_n.append(n)
            dots_density.append(d)
            dots_representation.append(r)
            dots_t.append(j)


   
plt.figure(figsize=(10, 2), dpi=300)
max_distance = 0.2
min_distance = 0.0
for p1 in range(len(dots_n)):
    for p2 in range(len(dots_n)):
        if abs(dots_t[p1]-dots_t[p2]) == stepsize:
            d = np.linalg.norm(dots_representation[p1]-dots_representation[p2])
            if min_distance < d < max_distance:
                plt.plot([dots_t[p1],dots_t[p2]], [dots_density[p1],dots_density[p2]], 'k-', linewidth=1-d)
        if abs(dots_t[p1]-dots_t[p2]) == stepsize:
            if  min_distance < d < max_distance:
                plt.plot([dots_t[p1],dots_t[p2]], [dots_density[p1],dots_density[p2]], 'k--', linewidth=1-d, color="grey")
        if abs(dots_t[p1]-dots_t[p2]) == stepsize:
            if  min_distance < d < max_distance:
                plt.plot([dots_t[p1],dots_t[p2]], [dots_density[p1],dots_density[p2]], 'k:', linewidth=1-d, color="grey")
plt.scatter(x=dots_t, y=dots_density, s=dots_n, alpha=0.5, edgecolors='k')
plt.ylabel('Avg. Cluster Sparsity')
plt.xlabel('Processed Events')
plt.xticks(ticks, [str(j//1000)+"k" for j in ticks])
plt.show()
