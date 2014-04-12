#!/usr/bin/env python
#coding=utf-8

'''
输出数据
格式：01:02 -> 1991:2:3
'''

import redis
import xlwt
import string

#file1 = xlwt.Workbook()
#table = file1.add_sheet('authorRela')
file_o = open('test.txt','w')
#try:
r = redis.StrictRedis('192.168.2.200',port = 6379, db =1)
count = r.dbsize()
k = r.keys()
i = 0
index = 0
#k = ['1990:1:2']
for item in k:
    item_list12 = item.split(':')
    value_list = list(r.smembers(item))
#    print item_list12
#    print value_list
    for value in value_list:
        col_list345 = value.split(':')
        #table.write(i,0,item_list12[0])
        #table.write(i,1,item_list12[1])

        #table.write(i,2,col_list345[0])
        #table.write(i,3,col_list345[1])
        #table.write(i,4,col_list345[2])

        file_o.write(item_list12[0] + ' ' + item_list12[1] + ' ' + col_list345[0] + ' ' + col_list345[1] + ' ' + col_list345[2] + '\n')
        i += 1
    index += 1
    if index/10000 == 0:
        print index/float(count)
file_o.close()
#file1.save('test.xls')
#except:
print 'rela size:' + count
print 'co rela count:' + i
print 'start'
#print r.dbsize()
