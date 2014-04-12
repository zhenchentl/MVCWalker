#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
Created on 2013-3-26

Description: 对本地的DBLP.xml文档进行解析。并放在Redis数据库中

@author: zhenchentl
'''
import sys
sys.path.append("./dbhelper")

from xml.sax import handler, make_parser
from dbhelper.RedisHelper import RedisHelper
import time

DBLP_XML_PATH = '/home/zhenchentl/dblp/dblp.xml'

paperTag = ('article','inproceedings','proceedings','book',
        'incollection','phdthesis','mastersthesis','www')

ISOTIMEFORMAT = '%Y-%m-%d %X'

class CoauthorHandler(handler.ContentHandler):

    def __init__(self):
        self.count = 0
        self.year = ''
        self.conf = ''
        self.isPaperTag = 0
        self.isAuthorTag = 0
        self.isYearTag = 0
        self.CoauthorList = []
        self.parserHelper = parserHelper()
        self.ConfList = self.parserHelper.getConfList()
        print self.ConfList

    def startDocument(self):
        print 'Document Start'

    def endDocument(self):
        print 'Document End'

    def startElement(self, name, attrs):
        if name in paperTag:
            confname = attrs.get('key').split('/')[1]
            if confname in self.ConfList:
                self.isPaperTag = 1
                self.conf = confname
        if name == 'author':
            self.isAuthorTag = 1
        if name == 'year':
            self.isYearTag = 1

    def endElement(self, name):
        if name in paperTag:
            if self.isPaperTag == 1:
                self.isPaperTag = 0
                self.parserHelper.addcoAuthorByList(self.CoauthorList, self.year, self.conf)
                self.con = ''
                self.CoauthorList = []
                self.year = ''
                self.count+=1
                if self.count%10000 == 0:
                    print self.count
    def characters(self, content):
        if self.isYearTag == 1:
            self.isYearTag = 0
            self.year = content
        if self.isAuthorTag == 1 and self.isPaperTag == 1:
            self.isAuthorTag = 0
            self.CoauthorList.append(content)


class parserHelper:
    '''作者合作关系解析帮助类'''
    def __init__(self):
        self.RedisHelper = RedisHelper()

    def addcoAuthorByList(self, coauthorList, year, conf):
#        print str(coauthorList) + '----' + conf
        if len(coauthorList)>1:
            for au in coauthorList:
                for coau in coauthorList:
                    if au != coau:
                        auth1 = coauthorList.index(au)
                        auth2 = coauthorList.index(coau)
                        self.RedisHelper.addCoauthor(au, coau, year, auth1, auth2,conf)
    def getConfList(self):
        ConfList = []
        tmplist = []
        with open('/home/zhenchentl/in.txt') as file_input:
            tmplist.append(file_input.readline().strip().split(','))
            ConfList.extend(tmplist[0])
        return ConfList

def parserDblpXml():
    print 'parser start! Time:'+time.strftime(ISOTIMEFORMAT,time.localtime())

    handler = CoauthorHandler()
    parser = make_parser()
    parser.setContentHandler(handler)
    f = open(DBLP_XML_PATH,'r')
    parser.parse(f)

    f.close()
    print 'parser end! Time:'+time.strftime(ISOTIMEFORMAT,time.localtime())

if __name__ == '__main__':
    parserDblpXml()
