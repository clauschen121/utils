#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-01-29 22:10:47
# @Author  : Claus Chen (245618722@qq.com)
# @Link    : https://github.com/clauschen121


import os
import sys


def file_split(filename, dirname, size):
    filename, dirname = map(os.path.abspath, [filename, dirname])
    part = 0
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
    else:
        for f in os.listdir(dirname):
            os.remove(os.path.join(dirname, f))
    if not os.path.isfile(filename):
        print('你所输入的文件不存在！')
        return
    with open(filename, 'rb') as file:
        while True:
            data = file.read(size)
            if not data:
                break
            part += 1
            newname = os.path.join(dirname, ('part%04d' % part))
            with open(newname, 'ab+') as wfile:
                wfile.write(data)
    print('分片已完成，请进入%s查看文件' % dirname)


def file_merge(filename, dirname, size):
    filename, dirname = map(os.path.abspath, [filename, dirname])
    file_list = sorted([f for f in os.listdir(dirname)])
    for file in file_list:
        with open(dirname + os.path.sep + file, 'rb') as rfile:
            while True:
                data = rfile.read(size)
                if not data:
                    break
                with open(filename, 'ab+') as wfile:
                    wfile.write(data)
    print('合并已完成，请打开%s查看文件' % filename)


def run():
    size = 1024 * 1024
    if len(sys.argv) == 2 and sys.argv[1] == '-help':
        print('Use: python file_exc.py [filename dirname flag [size]]')
        return
    else:
        if len(sys.argv) < 4:
            filename = input('请输入要分割或者合并的文件名：\n')
            dirname = input('\n请输入要分割到的目录或者合并的目录：\n')
            flag = int(input('\n请选择要执行操作的编号：\n1.分割文件 2.合并文件\n'))
        else:
            filename = sys.argv[1]
            dirname = sys.argv[2]
            flag = int(sys.argv[3])
            if len(sys.argv) > 4:
                size = int(sys.argv[4])
    if flag == 1:
        file_split(filename, dirname, size)
    elif flag == 2:
        file_merge(filename, dirname, size)
    else:
        print('非法操作，退出')
        return


if __name__ == '__main__':
    run()
