#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
Created on 2013-3-27
Description:对数据库操作。增删改查操作
@author: zhenchentl
'''
import redis
DB_COAUTHOR_SET = 0
DB_PAPER_ATTR = 1
DB_KEY_AUTHOR_MAP = 2
DB_AUTHOR_KEY_MAP = 3
class RedisHelper:
    def __init__(self):
        try:
            '''Key-->set:存储合作者集合。author-->coAuthor'''
            self.coSetDB = redis.StrictRedis('192.168.2.200', port = 6379,db = DB_COAUTHOR_SET)
            '''key-->set:存储论文合作关系及论文时间、作者顺序，会议／期刊名称。
            author1:author2-->1991:1:2(论文时间：author1作者顺序：author2作者顺序：期刊／会议名称)'''
            self.paperAttrDB = redis.StrictRedis('192.168.2.200', port = 6379,db = DB_PAPER_ATTR)
            '''Key-->value：存储作者名与代码键值对。codenum-->author'''
            self.keyAuthorMapDB = redis.StrictRedis('192.168.2.200', port = 6379,db = DB_KEY_AUTHOR_MAP)
            '''Key-->value：与上面相反，中间过程。author-->codenum'''
            self.authorKeyMapDB = redis.StrictRedis('192.168.2.200', port = 6379,db = DB_AUTHOR_KEY_MAP)
        except:
            print "can not open Redis database"
    def addCoauthor(self, author, coauthor, year, auth1, auth2,conf):
        '''增加一条合作关系，以及合作论文时间属性，作者顺序'''
        try:
            '''增加一个作者名-代码键值对，已经存在则忽略（值为自增长）'''
            authorCode = self.authorKeyMapDB.dbsize()
            if self.authorKeyMapDB.setnx(author, authorCode) ==0:
                authorCode = self.authorKeyMapDB.get(author)
            else:
                self.keyAuthorMapDB.setnx(authorCode, author)
            coAuthorCode = self.authorKeyMapDB.dbsize()
            if self.authorKeyMapDB.setnx(coauthor, coAuthorCode) ==0:
                coAuthorCode = self.authorKeyMapDB.get(coauthor)
            else:
                self.keyAuthorMapDB.setnx(coAuthorCode, coauthor)
            '''增加一条作者合作关系'''
            self.coSetDB.sadd(authorCode, coAuthorCode)
            #print authorCode, ':', coAuthorCode
            '''增加一片论文的信息，即作者合作关系的属性'''
            attr = year + ':' + str(auth1) + ':' + str(auth2) + ':' + str(conf)
            key = str(authorCode) + ':' + str(coAuthorCode)
            self.paperAttrDB.sadd(key, attr)
            #print 'haha4'
        except:
            print "can not add value to Redis database"
    def getCoauthors(self, author):
        return self.coSetDB.smembers(author)
    def getCoPapers(self, author, coAuthor):
        key = str(author)+':'+str(coAuthor)
        return self.paperAttrDB.smembers(key)
    def getAuthornameByCode(self, code):
        return self.keyAuthorMapDB.get(code)
    def getCoPapersKeys(self):
        return self.paperAttrDB.keys()
    def getAuthorKeys(self):
        return self.coSetDB.keys()
    def ifexists(self, node):
        return self.authorKeyMapDB.exists(node)
    def getAllauthornames(self):
        return self.authorKeyMapDB.keys()
