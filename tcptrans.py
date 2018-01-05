#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-01-03 019:03:02
# @Author  : Claus Chen (245618722@qq.com)
# @Link    : https://github.com/clauschen121

import socket
import threading
import re

L = []
lock = threading.Lock()


def tcplink(sock, addr):
    try:
        decode_type = 'utf-8'
        print('Accept new connection from %s:%s' % addr)
        while True:
            data = sock.recv(1024)
            try:
                data = data.decode(decode_type)
            except UnicodeDecodeError:
                try:
                    decode_type = 'gbk'
                    data = data.decode(decode_type)
                except UnicodeDecodeError:
                    print('utf-8与gbk均不能对你的数据解码，请检查数据编码方式')
                    break
            if not data:
                break
            result = parse_id(data)
            if result:
                d = {
                    'id': result.group(1),
                    'type': result.group(2),
                    'sock': sock
                }
                add_dict(d)
            else:
                if find_sendto(sock):
                    sid, did, dsock = find_sendto(sock)
                    print("{} wrote to {}:".format(
                        sid,
                        did)
                    )
                    dsock.sendall(data.encode(decode_type))
                    print('%s(编码方式：%s)' % (data, decode_type))
        sock.close()
        print('id号为%s的设备断开了连接' % sid)
        delete_dict(sock)
    except ConnectionResetError:
        sock.close()
        print('远程设备异常断开连接：%s' % sid)
        delete_dict(sock)


def find_list(list1, list2):
    if list1 in list2:
        return list2.index(list1)
    else:
        return -1


def parse_id(data):
    pattern = r'^(\d{11})([a|b])'
    result = re.search(pattern, data)
    return result


def add_dict(d):
    flag = find_list([d['id'], d['type']], list(
        [i['id'], i['type']] for i in L))
    if flag != -1:
        if L[flag]['type'] == d['type']:
            lock.acquire()
            try:
                L[flag]['sock'] = d['sock']
                print('在配对列表中更新了id号为%s的设备' %
                      (d['id'] + d['type']))
            finally:
                lock.release()
    else:
        lock.acquire()
        try:
            L.append(d)
            print('在配对列表中增加了id号为%s的设备' % (d['id'] + d['type']))
        finally:
            lock.release()


def delete_dict(sock):
    flag = find_list(sock, list(i['sock'] for i in L))
    if flag != -1:
        pid, ptype = L[flag]['id'], L[flag]['type']
        lock.acquire()
        try:
            L.pop(flag)
            print('从配对列表中删除了id号为%s的设备' % (pid + ptype))
        finally:
            lock.release()


def find_sendto(sock):
    flag = find_list(sock, list(
        i['sock'] for i in L))
    if flag != -1:
        id, type = L[flag]['id'], L[flag]['type']
        for i in L:
            if i['id'] == id and i['type'] != type:
                return id + type, i['id'] + i['type'], i['sock']
    return None


def start():
    flag_host = ''
    flag_port = ''
    while not flag_host:
        HOST = input('\n请输入要侦听的本机ip，确保该ip能被外网访问：\n\n')
        pattern_host = re.compile('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
        flag_host = re.match(pattern_host, HOST)
        if not flag_host:
            print('ip地址格式有误')
    while not flag_port:
        PORT = input('\n请输入需要监听的端口，确保能从外网访问该端口：\n\n')
        pattern_port = re.compile('^\d{1,5}$')
        flag_port = re.match(pattern_port, PORT)
        if not flag_port:
            print('端口号需要在0-65535之间')
    PORT = int(PORT)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(5)
    print('tcp is listening on %s:%s' % (HOST, PORT))
    while True:
        sock, addr = s.accept()
        t = threading.Thread(target=tcplink, args=(sock, addr))
        t.start()


if __name__ == "__main__":
    start()
