#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
Created on 2013-3-26
Description: 改进的PageRank
@author: zhenchentl
'''
from graph.createDigraphByYear import DigraphByYear
from operator import itemgetter
from pygraph.classes.graph import graph

def PageRank(flag, graph, current_node='129972', damping_factor=0.3,\
        max_iterations=20, min_delta=0.0001):
    """
    Compute and return the PageRank in an directed graph.
    @type  graph: digraph
    @param graph: Digraph.
    @type  damping_factor: number
    @param damping_factor: PageRank dumping factor.
    @type  max_iterations: number
    @param max_iterations: Maximum number of iterations.
    @type  min_delta: number
    @param min_delta: Smallest variation required for a new iteration.
    @rtype:  Dict
    @return: Dict containing all the nodes PageRank.
    """
    nodes = graph.nodes()
    graph_size = len(nodes)
    if graph_size == 0:
        return {}
    '''if the random walk start from one node,set the rank as 1.0,while others 0'''
    pagerank = dict.fromkeys(nodes, 0)
    pagerank[current_node] = 1.0
    Svalue = {}
    min_value = (1.0-damping_factor) / graph_size
    itertimes = 0
    for i in range(max_iterations):
        diff = 0
        for node in nodes:
            rank = min_value
            for referring_page in graph.incidents(node):
                rank += damping_factor * pagerank[referring_page] * \
                         getRankTo(flag, graph, referring_page, node, Svalue)
            diff += abs(pagerank[node] - rank)
            pagerank[node] = rank
        '''重启动概率'''
        pagerank[current_node] += 1*(1-damping_factor)
        itertimes = i
        '''stop if PageRank has converged'''
        if diff < min_delta:
            break
    print '\niterition time:'+ str(itertimes)
    return sorted(pagerank.iteritems(), key=itemgetter(1), reverse=True)

def getRankTo(flag, gra, from_node, to_node, S):
    if  S.has_key(from_node+':'+to_node):
        return S[from_node+':'+to_node]
    if flag == 1:
        total_wt = 0.0
        for tmp_node in gra.neighbors(from_node):
            total_wt = total_wt + gra.edge_weight((from_node, tmp_node))
        S[from_node+':'+to_node] = var = gra.edge_weight((from_node, to_node))/total_wt
    else:
        S[from_node+':'+to_node] = var = 1.0/len(gra.neighbors(from_node))
    return  var
