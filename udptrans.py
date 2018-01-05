#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-01-02 09:03:02
# @Author  : Claus Chen (245618722@qq.com)
# @Link    : https://github.com/clauschen121


import socketserver
import threading
import re

L = []
lock = threading.Lock()


class ThreadedUDPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        data, socket = self.request[0].strip().decode('ascii'), self.request[1]
        print('recieve data from {}:{}'.format(
            self.client_address[0], self.client_address[1]))
        print(data)
        result = parse_id(data)
        if result:
            d = {
                'id': result.group(1),
                'type': result.group(2),
                'address': self.client_address[0],
                'port': self.client_address[1]
            }
            add_dict(d)
        else:
            if find_sendto(self.client_address[0], self.client_address[1]):
                address, port = find_sendto(
                    self.client_address[0], self.client_address[1])
                print("{}:{} wrote to {}:{} :".format(
                    self.client_address[0],
                    self.client_address[1],
                    address,
                    port)
                )
                print(data)
                socket.sendto(data.encode('ascii'), (address, port))


class ThreadedUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass


def find_list(list1, list2):
    if list1 in list2:
        return list2.index(list1)
    else:
        return -1


def parse_id(data):
    pattern = r'^(\d{11})([a|b])$'
    result = re.search(pattern, data)
    return result


def add_dict(d):
    flag = find_list([d['id'], d['type']], list(
        [i['id'], i['type']] for i in L))
    if flag != -1:
        if L[flag]['type'] == d['type']:
            lock.acquire()
            try:
                L[flag]['address'] = d['address']
                L[flag]['port'] = d['port']
            finally:
                lock.release()
    else:
        lock.acquire()
        try:
            L.append(d)
            print(L)
        finally:
            lock.release()


def find_sendto(address, port):
    flag = find_list([address, port], list(
        [i['address'], i['port']] for i in L))
    if flag != -1:
        id, type = L[flag]['id'], L[flag]['type']
        for i in L:
            if i['id'] == id and i['type'] != type:
                return i['address'], i['port']
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
    server = ThreadedUDPServer((HOST, PORT), ThreadedUDPHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()
    print('udp is listening on %s:%s' % (HOST, PORT))


if __name__ == "__main__":
    start()
