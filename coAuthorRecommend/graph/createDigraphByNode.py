#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
Created on 2013-4-4下午2:55:11
Description: 读取数据库内容，根据中心节点和条数获取需要的节点和边，放入本地内存中，生成Digraph图
@author: zhenchentl
'''
from dbhelper.RedisHelper import RedisHelper
from pygraph.classes.digraph import digraph
import string

class DigraphByNode():
    def __init__(self):
        self.mRedisHelper = RedisHelper()
        self.mDigraph = digraph()
        self.mQueue = []
    def getDigraph(self, name = '129972', MaxLeapCount = 3):
    #     edge_count = 0
        self.mQueue.append([name,0])
        self.mDigraph.add_node(name)
        while len(self.mQueue)>0:
            author = list(self.mQueue.pop(0))
            authorName = author[0]
            authorleapCount = author[1]
            if authorleapCount < MaxLeapCount:
                coAuthorList = list(self.mRedisHelper.getCoauthors(authorName))
                while len(coAuthorList)>0:
                    coAuthor = coAuthorList.pop(0)
                    if not self.mDigraph.has_node(coAuthor):
                        self.mDigraph.add_node(coAuthor)
                        self.mQueue.append([coAuthor,authorleapCount+1])
                    if not self.mDigraph.has_edge((authorName, coAuthor)) and \
                            not self.mDigraph.has_edge((coAuthor, authorName)):
                        coPaperList = list(self.mRedisHelper.getCoPapers(authorName, coAuthor))
                        if len(coPaperList) <2:
                            continue
                        weight = self.getWeightOfEdge(coPaperList)
                        self.mDigraph.add_edge((authorName, coAuthor),weight)
                        self.mDigraph.add_edge((coAuthor, authorName),weight)
            else:
                """后面都是叶子节点，不再计算其合作者"""
                break
        return self.mDigraph
    def getWeightOfEdge(self, coPaperList):
        """生成合作者之间的关系权重，考虑到时间和作者顺序关系"""
    #     print coPaperList
        weight = 0
        for coPaper in coPaperList:
            attrList = coPaper.split(':')
            orderFac = self.getWeightByAuthorOrder(attrList[1], attrList[2])
            timeFac = self.getWeightByPaperTime(attrList[0])
    #         print 'order:',orderFac, ' time:', timeFac
            weight = weight + orderFac * timeFac
        return weight
    def getWeightByAuthorOrder(self, authorOrder1, authorOrder2):
        if authorOrder1 < authorOrder2:
            a1 = string.atof(authorOrder1)
            a2 = string.atof(authorOrder2)
        else:
            a1 = string.atof(authorOrder2)
            a2 = string.atof(authorOrder1)
        if a1 == 1 or 2:
            return 1/a2
        else:
            return 1/(a1*a2)
    def getWeightByPaperTime(self, year):
        try:
            return (string.atof(year)-1980.0)/(2013.0-1980.0)
        except:
            return 1
if __name__ == '__main__':
    mD = DigraphByNode()
    mD.getDigraph()
