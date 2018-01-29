#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-01-28 11:17:54
# @Author  : Claus Chen (245618722@qq.com)
# @Link    : https://github.com/clauschen121


import os
from sys import argv

dirname = os.curdir
filename = '.py'
flag = 0
if len(argv) > 1:
    dirname = argv[1]
if len(argv) > 2:
    filename = argv[2]
if len(argv) > 3:
    flag = int(argv[3])
find_list = []
print(dirname, filename, flag)


def search_file():
    for (thisDir, subsDir, filesHere) in os.walk(dirname):
        thisDir = os.path.abspath(thisDir)
        print('正在搜索目录：', thisDir)
        for file in filesHere:
            if flag == 0:
                if file.endswith(filename):
                    find_list.append(thisDir + file)
            if flag == 1:
                if file.startswith(filename):
                    find_list.append(thisDir + file)
            if flag == 2:
                if file.find(filename) != -1:
                    find_list.append(thisDir + file)


search_file()

if len(find_list):
    print('\n\n共找到%s个匹配文件，如下：' % len(find_list))
    for i in find_list:
        print(i)
else:
    print('未找到匹配文件')
