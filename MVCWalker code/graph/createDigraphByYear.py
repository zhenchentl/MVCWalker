#!/usr/bin/env python
#coding=utf-8
'''
Created on 2013-4-4下午2:55:11

Description: 读取数据库内容，根据年份获取需要的节点和边，放入本地内存中，生成Digraph图。

@author: zhenchentl
'''

from dbhelper.RedisHelper import RedisHelper
from pygraph.classes.digraph import digraph
import string

class DigraphByYear():
    '''MinCoPapers = 4是有道理的，当一个弱节点仅发表一篇文章时，
    一般情况下，最少有三个合作者。等于4表示最少发表了两篇文章。'''
    def __init__(self, year_sta = 2000, year_end = 2010, MinCoPapers = 0):
        self.year_sta = year_sta
        self.year_end = year_end
        self.MinCoPapers = MinCoPapers
        self.mDigraph = digraph()
        self.mRedisHelper = RedisHelper()

    def getDigraph(self):
        author_list = self.mRedisHelper.getAuthorKeys()
        print "author list length:" + str(len(author_list))
        '''先向digraph中添加我们认可的强节点'''
        for author in author_list:
            coAuthors = list(self.mRedisHelper.getCoauthors(author))
            if len(coAuthors) >= self.MinCoPapers and not self.mDigraph.has_node(author):
                self.mDigraph.add_node(author)
        print "add node finished! and node count:" + str(len(self.mDigraph.nodes()))
        '''清空author_list所占内存'''
        author_list = []
        '''然后想digraph中添加所有的边'''
        rela_list = self.mRedisHelper.getCoPapersKeys()
        print "copapers keys list length:" + str(len(rela_list))
        for item in rela_list:
            author_pair = item.split(":")
            author_a = author_pair[0]
            author_b = author_pair[1]
            if self.mDigraph.has_node(author_a) and self.mDigraph.has_node(author_b):
                if  not self.mDigraph.has_edge((author_b,author_a)) and not self.mDigraph.has_edge((author_a,author_b)):
                    paper_list = list(self.mRedisHelper.getCoPapers(author_a, author_b))
                    weight = self.getWeight(paper_list)
                    if weight > 0:
                        self.mDigraph.add_edge((author_a,author_b),weight)
                        self.mDigraph.add_edge((author_b,author_a),weight)
        '''清空rela_list所占内存'''
        rela_list = []
        print "end!"
        return self.mDigraph

    def getWeight(self, paper_list):
        weight = 0
        for paper in paper_list:
            try:
                paper_attr = paper.split(":")
                attr_time = paper_attr[0]
                attr_author1 = paper_attr[1]
                attr_author2 = paper_attr[2]
                if int(attr_time) >= self.year_sta and int(attr_time) <= self.year_end:
                    weight = weight + self.getWeightByAuthorOrder(attr_author1,
                             attr_author2) * self.getWeightByPaperTime(attr_time)
#                    weight += self.getWeightByAuthorOrder(attr_author1,attr_author2)
#                    weight += self.getWeightByPaperTime(attr_time)
#                    weight += 1
            except:
                continue
        return weight

    '''根据作者顺序计算边的权重'''
    def getWeightByAuthorOrder(self, authorOrder1, authorOrder2):
#         if authorOrder1 < authorOrder2:
#             a1 = string.atof(authorOrder1)
#             a2 = string.atof(authorOrder2)
#         else:
#             a1 = string.atof(authorOrder2)
#             a2 = string.atof(authorOrder1)
#         if a1 == 1 or a1 == 2:
#             return 1/(a2-1)
#         else:
#             return 1/((a1-1)*(a2-1))
        a1 = string.atof(authorOrder1)
        a2 = string.atof(authorOrder2)
        if a1 <= 3 and a2 <= 3:
            return 1/a1 + 1/a2
        if a1 <= 3 and a2 >= 4:
            return 1/a1+2/a2
        if a1 > 3 and a2 > 3:
            return 2/a1 + 2/a2
#         
    '''根据合作时间计算边的权重'''
    def getWeightByPaperTime(self, year):
        try:
            weight = (int(year)-2000.0)/(2013.0-2000.0)
            if weight > 0:
                return weight
            else:
                return 0
        except:
            print 'papertime error'
            return 0
