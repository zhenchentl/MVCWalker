#!/usr/bin/env python
#coding=utf-8

import sys
sys.path.append("./dbhelper")
sys.path.append("./graph")
sys.path.append("./randomwalk")

from graph.createDigraphByYear import DigraphByYear
from graph.createDigraphByNode import DigraphByNode
from pygraph.classes.digraph import digraph
from randomwalk.pagerank import PageRank
from dbhelper.RedisHelper import RedisHelper
from collections import Counter
from operator import itemgetter
import random
import time

def recommender( recom_count = 25, test_times = 100, hotNode_degree = 60, year_sta = 2011):
    '''
    进行推荐实验，计算结果存储在txt文件中
    @edge_del       随机删掉的边数
    @recom_count    推荐列表大小
    @test_times     实验次数
    @hotNode_degree 定义热点最小邻居数
    '''
    file_input = open('/home/zhenchentl/out.txt','w+')
    file_input_re = open('/home/zhenchentl/out_re.txt','w+')
    file_input.write('recom_count:' + str(recom_count) + '\n')
    file_input.write('test_times:' + str(test_times) + '\n')
    file_input.write('hotNode_degree:' + str(hotNode_degree) + '\n')

    file_input.write('befor get graph time:' + time.strftime('%Y-%m-%d-%H-%M-%S', \
            time.localtime(time.time())) + '\n')
    print 'befor get graph time:' + time.strftime('%Y-%m-%d-%H-%M-%S', \
            time.localtime(time.time()))
    '''get the graph based on the coauhtor relationship'''
    mD = DigraphByYear()
    mDigraph = mD.getDigraph()
    getGraphAttr(mDigraph, file_input)
    file_input.write('after get graph time:' + time.strftime('%Y-%m-%d-%H-%M-%S', \
            time.localtime(time.time())) + '\n')
    print 'after get graph time:' + time.strftime('%Y-%m-%d-%H-%M-%S', \
            time.localtime(time.time()))
    recom_count = 5
    while(recom_count <= 100):
        exp_recom(mDigraph, file_input,file_input_re,recom_count)
        recom_count += 5
    file_input.close()
    file_input_re.close()

def exp_recom(mDigraph, file_input,file_input_re,recom_count = 25, year_sta = 2011, \
        damping_factor=0.25, max_iterations = 25, test_times = 100, hotNode_degree = 60):
    precision_MVC = recall_MVC = avrpathMVC = 0.0
    precision_base = recall_base = avrpath_base = 0.0
#    precision_CN = recall_CN = avrpath_CN = 0.0
    targetNodeList = gettargetNodeList()
    for index in range(test_times):
        file_input.write('this is the experiments of number:' + str(index+1) + '\n')
        print 'this is the experiments of number:' + str(index+1)
        targetNode, newCoAuthorList = getTNodeCauthorList(mDigraph, year_sta, targetNodeList)
        pB, rB, aB = recomByBasewalker(mDigraph, targetNode, newCoAuthorList, recom_count, \
                file_input, file_input_re, max_iterations,damping_factor)
        pM, rM, aM = recomByMVCwalker(mDigraph, targetNode, newCoAuthorList, recom_count, \
                file_input, file_input_re, max_iterations,damping_factor)
        precision_MVC += pM
        recall_MVC += rM
        avrpathMVC += aM
        precision_base += pB
        recall_base += rB
        avrpath_base += aB
    print '\nrecom_count:' + str(recom_count) + '\n'
    file_input_re.write('*************************\nrecom_count' + str(recom_count))
    file_input_re.write('\nprecision _MVC:' + str((1.0*precision_MVC)/test_times))
    file_input_re.write('\nprecision _base:' + str((1.0*precision_base)/test_times))
    file_input_re.write('\n\nrecall _MVC:' + str((1.0*recall_MVC)/test_times))
    file_input_re.write('\nrecall _base:' + str((1.0*recall_base)/test_times))
    file_input_re.write('\n\navrpath _MVC:' + str((1.0*avrpathMVC)/test_times))
    file_input_re.write('\navrpath _base:' + str((1.0*avrpath_base)/test_times))
    file_input_re.write(str(targetNodeList))

def recomByMVCwalker(graph, targetNode, newCoAuthorList, recom_count, \
        file_input, file_input_re, max_iterations, damping_factor):
    recom_list = []
    file_input.write('befor MVCWalker time:' + time.strftime('%Y-%m-%d-%H-%M-%S', \
            time.localtime(time.time())) + '\n')
    pagerank = PageRank(1, graph, targetNode, damping_factor, max_iterations)
    file_input.write('after MVCWalker time:' + time.strftime('%Y-%m-%d-%H-%M-%S', \
            time.localtime(time.time())) + '\n')
    index = 0
    for k, v in pagerank:
#        if not graph.has_edge((targetNode, k)):
        recom_list.append(k)
        file_input.write('recom:' + '(' + targetNode + ':' + k + ')' + str(v) + '\n')
        index += 1
        if index >= recom_count - 1:
            break
    pagerank = []
    node_count_right = len(list(set(newCoAuthorList) & set(recom_list)))
    path_dis = find_shortest_path(graph, targetNode, recom_list)
    file_input_re.write('1'+str(len(newCoAuthorList)) + ' ' + str(node_count_right) + \
            ' ' + str(recom_count) + ' ' + str((1.0*path_dis)/recom_count) + '\n')
    recom_list = []
    '''return the percision,recall and average of shortest path leghth'''
    return (1.0*node_count_right)/recom_count, (1.0*node_count_right)/len(newCoAuthorList), (1.0*path_dis)/recom_count

def recomByBasewalker(graph, targetNode, newCoAuthorList, recom_count, \
        file_input, file_input_re, max_iterations, damping_factor):
    recom_list = []
    file_input.write('befor BaseWalker time:' + time.strftime('%Y-%m-%d-%H-%M-%S', \
            time.localtime(time.time())) + '\n')
    pagerank = PageRank(0, graph, targetNode, damping_factor, max_iterations)
    file_input.write('after BaseWalker time:' + time.strftime('%Y-%m-%d-%H-%M-%S', \
            time.localtime(time.time())) + '\n')
    index = 0
    for k, v in pagerank:
#        if not graph.has_edge((targetNode, k)):
        recom_list.append(k)
        file_input.write('recom:' + '(' + targetNode + ':' + k + ')' + str(v) + '\n')
        index += 1
        if index >= recom_count - 1:
            break
    pagerank = []
    file_input.write(str(newCoAuthorList) + '\n')
    node_count_right = len(list(set(newCoAuthorList) & set(recom_list)))
    path_dis = find_shortest_path(graph, targetNode, recom_list)
    file_input_re.write('2'+str(len(newCoAuthorList)) + ' ' + str(node_count_right) + \
            ' ' + str(recom_count) + ' ' + str((1.0*path_dis)/recom_count) + '\n')
    recom_list = []
    '''return the percision,recall and average of shortest path leghth'''
    return (1.0*node_count_right)/recom_count, (1.0*node_count_right)/len(newCoAuthorList), (1.0*path_dis)/recom_count

def getTNodeCauthorList(mDigraph, year_sta, targetNodeList):
    targetNode = targetNodeList.pop(0)
    newCoauthors = getNewCoAUhtorList(targetNode, year_sta)
    return targetNode, newCoauthors


def getNewCoAUhtorList(targetNode, year_sta = 2011):
    newCoAuthors = []
    mRedisHelper = RedisHelper()
    coauthors = mRedisHelper.getCoauthors(targetNode)
    for coau in coauthors:
        coPapers = mRedisHelper.getCoPapers(targetNode, coau)
        for copa in coPapers:
            try:
                time = copa.split(':')[0]
                if int(time) >= year_sta:
                    newCoAuthors.append(coau)
                    break
            except:
                return []
    return newCoAuthors

def find_shortest_path(graph, start, recom_list):
    dis = 0
    tmplist = []
    rightList = []
    queue = []
    queue.append([start,0])
    tmplist.append(start)
    while len(queue) > 0:
        item = list(queue.pop(0))
        name = item[0]
        loop = item[1]
        if name in recom_list:
            dis += loop
            rightList.append(name)
        if loop < 3:
            for nb in graph.neighbors(name):
                if nb not in tmplist:
                    queue.append([nb,loop+1])
                    tmplist.append(nb)
    dis = dis + 3*(len(recom_list)- len(rightList))
    tmplist = []
    return dis

def getGraphAttr(graph, file_input):
    nodes = graph.nodes()
    edges = graph.edges()
    degree_distr = []
    degree = 0
    for node in nodes:
        d = graph.neighbors(node)
        degree_distr.append(int(len(d)/10*10))
        degree += len(d)
    c = Counter(degree_distr)
    de_di = dict(c.most_common())
    de_di = sorted(de_di.iteritems(), key=itemgetter(0), reverse=True)
    average_degree = (1.0*degree)/len(nodes)
    file_input.write("nodes count:" + str(len(nodes)))
    file_input.write("edges count:" + str(len(edges)))
    file_input.write("average degree:" + str(average_degree))
    file_input.write("degree distribution:" + str(de_di))

    print "nodes count:" + str(len(nodes))
    print "edges count:" + str(len(edges))
    print "average degree:" + str(average_degree)
    print "degree distribution:" + str(de_di)

def gettargetNodeList():
        ConfList = []
        tmplist = []
        with open('in.txt') as file_input:
            tmplist.append(file_input.readline().strip().split(','))
            ConfList.extend(tmplist[0])
        return ConfList

if __name__ == '__main__':
    recommender()
#     print gettargetNodeList()
#     with open('in.txt','w') as file1:
#         mRedisHelper = RedisHelper()
#         authors = mRedisHelper.getAuthorKeys()
#         for inter in range(100):
#             print inter
#             while 1:
#                 targetNode = random.choice(authors)
#                 if len(list(mRedisHelper.getCoauthors(targetNode))) > 30 and len(getNewCoAUhtorList(targetNode))>3:
#                     file1.write(targetNode+',')
#                     break