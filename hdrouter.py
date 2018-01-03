#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-08-27 09:18:08
# @Author  : Claus Chen (245618722@qq.com)
# @Link    : https://github.com/clauschen121


import telnetlib
import time
import socket
import re


class Hdrouter():

    def __init__(self):
        self.finish = b'~#'
        self.password = ''

    def connect(self, host, port):
        # 使用try语句，在异常后能够捕获到异常原因
        try:
            # telnetlib.Telnet的目的是建立一个到对端连接的管道，
            # 需要输入host和port，最后一个参数是超时时间
            tn = telnetlib.Telnet(host, port, 10)
            # 等待对端输出login，由于在通讯中均为二进制传输
            # 所以写入和读取都要用b''
            tn.read_until(b'login:')
            # 在对端输出login：提示符后，本地输入用户名root到对端
            tn.write(b'root\n')
            tn.read_until(b'Password:')
            # 路由器的密码，请用实际密码代替*
            tn.write(b'********\n')
            # 读取到self.finish提示符后，说明已经登录到了路由器的系统
            tn.read_until(self.finish)
            return tn
        except socket.timeout as e:
            print('连接失败：', e)
            return None

    def getModemInfo(self):
        print('正在获取模块名称。。。')
        #输入cat /tmp/modem.dev获取文件信息
        self.tn.write(b'cat /tmp/modem.dev\n')
        # 必须要等待一段时间对端把所有文件信息发送到缓冲区
        # 使用read_very_eager()方法可以获取到所有缓冲区的内容
        time.sleep(1)
        result = self.tn.read_very_eager().decode('ascii')
        # 通过正则匹配获取到文件中需要读取的内容，加入re.S可以跨行匹配
        pattern = re.compile('name:(.*?)\r\n', re.S)
        modem = re.search(pattern, result).group(1)
        print('模块名称：%s' % modem)

    def getModemStatus(self):
        print('正在获取模块状态。。。')
        self.tn.write(b'cat /tmp/modem.info\n')
        time.sleep(1)
        result = self.tn.read_very_eager().decode('ascii')
        pattern = re.compile('.*?\r\n(.*)\r\n', re.S)
        modem = re.search(pattern, result).group(1)
        modem = modem.replace('\r\n', '\n')
        print('模块状态：%s' % modem)

    def getAllLog(self):
        print('正在获取日志信息。。。')
        self.tn.write(b'cat /var/log/messages\n')
        time.sleep(2)
        result = self.tn.read_very_eager().decode('ascii')
        pattern = re.compile('.*?\r\n(.*)\r\n', re.S)
        log = re.search(pattern, result).group(1)
        print('日志信息如下：\n%s' % log)

    def getNewLog(self):
        print('正在获取日志信息。。。')
        self.tn.write(b'tail -10 /var/log/messages\n')
        time.sleep(1)
        result = self.tn.read_very_eager().decode('ascii')
        pattern = re.compile('.*?\r\n(.*)\r\n', re.S)
        log = re.search(pattern, result).group(1)
        print('最近10条日志信息如下：\n%s' % log)

    def getVersion(self):
        print('正在获取路由器版本信息。。。')
        self.tn.write(b'cat /etc/version\n')
        time.sleep(1)
        result = self.tn.read_very_eager()
        result = result.decode('ascii')
        pattern = re.compile('.*?\r\n(.*)\r\n', re.S)
        version = re.search(pattern, result).group(1)
        print('路由器版本信息如下：\n%s' % version)

    def getNvramInfo(self):
        # 获取初始化文件里的信息并返回
        self.tn.write(b'cat /etc/defconfig/system.info\n')
        time.sleep(1)
        result = self.tn.read_very_eager().decode('ascii')
        pattern = re.compile('.*?\r\n(.*)\r\n', re.S)
        nvram = re.search(pattern, result).group(1)
        return nvram

    def setModel(self, command, rpcommand, nvram, count):
        # 首先判断是否查找到文件
        pattern2 = re.compile('.*No such file or directory.*', re.S)
        fnexist = re.match(pattern2, nvram)
        if not fnexist:
                # 如果没有找到文件，则手动写入文件
                # 如果找到文件，则从原文件中获取相应的配置进行更改
            pattern0 = re.compile('.*' + command + '.*', re.S)
            pattern1 = re.compile(command)
            if re.match(pattern0, nvram):
                nvramset = re.sub(pattern1, rpcommand, nvram)
            else:
                nvramset = nvram + rpcommand + '\n'
        else:
            nvramset = rpcommand + '\n'

        nvramset = 'echo -e \"' + nvramset + '\">/etc/defconfig/system.info\n'
        nvramset = nvramset.replace('\r\n', '\n').encode('ascii')
        print('正在初始化参数')
        time.sleep(1)
        self.tn.write(nvramset)
        time.sleep(1)
        print('正在验证参数是否正确')
        time.sleep(1)
        result = self.tn.read_very_eager().decode('ascii')
        pattern = re.compile('.*' + rpcommand, re.S)
        validate = re.match(pattern, result)
        if validate:
            print('参数配置成功，需要重启路由器后生效')
            return True
        else:
            if count > 1:
                print('参数配置失败，正在重新尝试')
                time.sleep(1)
                self.setModel(command, rpcommand, nvram, count - 1)
            else:
                print('多次失败，停止尝试')
                return None

    # 具体的初始化配置信息，需要与输入对应
    def setNvramInfo(self, command, nvram):
        if(command == '10'):
            self.setModel('vpn_lice = \d', 'vpn_lice = 0', nvram, 5)
        elif(command == '11'):
            self.setModel('vpn_lice = \d', 'vpn_lice = 1', nvram, 5)
        elif(command == '20'):
            self.setModel('wan_lice = \d', 'wan_lice = 0', nvram, 5)
        elif(command == '21'):
            self.setModel('wan_lice = \d', 'wan_lice = 1', nvram, 5)
        elif(command == '30'):
            self.setModel('wlan_lice = \d', 'wlan_lice = 0', nvram, 5)
        elif(command == '31'):
            self.setModel('wlan_lice = \d', 'wlan_lice = 1', nvram, 5)
        elif(command == '32'):
            self.setModel('wlan_lice = \d', 'wlan_lice = 3', nvram, 5)
        elif(command == '40'):
            self.setModel('cfe_console_lice = \d',
                          'cfe_console_lice = 0', nvram, 5)
        elif(command == '41'):
            self.setModel('cfe_console_lice = \d',
                          'cfe_console_lice = 1', nvram, 5)
        elif(command == '50'):
            self.setModel('hd_soft_release = r-en',
                          'hd_soft_release = r-cn', nvram, 5)
        elif(command == '51'):
            self.setModel('hd_soft_release = r-cn',
                          'hd_soft_release = r-en', nvram, 5)
        elif(command == '60'):
            self.setModel('-oem', '-std', nvram, 5)
        elif(command == '61'):
            self.setModel('-std', '-oem', nvram, 5)
        else:
            print('未知输入，不修改')

    # 交互第一步，连接到路由器
    def step0(self):
        flag = ''
        pattern_ip = re.compile('\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}')
        while not flag:
            ipaddr = input('\n请输入路由器的ip地址（例如：192.168.8.1），同时保证电脑能够访问路由器：\n\n')
            flag = re.match(pattern_ip, ipaddr)
        self.tn = self.connect(ipaddr, '5188')

    # 交互第二步，输入需要的操作
    def step1(self):
        self.option1 = ''
        while (self.option1 != '1' and self.option1 != '2'):
            self.option1 = input(
                '\n请输入需要进行的操作代号（例如：1）：\n\n1.查看状态或日志 \n\n2.初始化路由器\n\n')

    # 第二步选1后的交互
    def step2(self):

        self.option2 = ''
        while (self.option2 != '1' and self.option2 != '2' and self.option2 != '3' and self.option2 != '4' and self.option2 != '5' and self.option2 != '6'):
            self.option2 = input(
                '\n请输入需要进行的操作代号（例如：1）：\n\n1.查看modem型号 \n\n2.查看modem状态 \n\n3.查看路由器版本号 \n\n4.查看所有日志 \n\n5.查看最近10条日志 \n\n6.退回上一级菜单\n\n')

    # 第二步选2后的交互
    def step3(self):
        self.option3 = ''
        while (self.option3 != '1' and self.option3 != '2' and self.option3 != '3' and self.option3 != '4' and self.option3 != '5' and self.option3 != '6' and self.option3 != '7'):
            self.option3 = input(
                '\n请输入需要进行的操作代号（例如：1）：\n\n1.初始化vpn功能 \n\n2.初始化wan口功能 \n\n3.初始化wifi功能 \n\n4.初始化DTU功能 \n\n5.初始化中英文版本 \n\n6.初始化OEM版本 \n\n7.退回到上一级菜单\n\n')

    # 定义整个交互的方法
    def start(self, count):
        self.step0()
        if self.tn:
            while True:
                self.step1()
                while self.option1 == '1':
                    self.step2()
                    if self.option2 == '1':
                        self.getModemInfo()
                    elif self.option2 == '2':
                        self.getModemStatus()
                    elif self.option2 == '3':
                        self.getVersion()
                    elif self.option2 == '4':
                        self.getAllLog()
                    elif self.option2 == '5':
                        self.getNewLog()
                    elif self.option2 == '6':
                        self.option1 = ''
                        break
                    time.sleep(2)
                while self.option1 == '2':
                    if self.password != 'hongdian':
                        self.password = input('请输入初始化验证密码，如不清楚可咨询售后工程师：\n\n')
                        if self.password != 'hongdian':
                            break
                    self.step3()
                    command = ''
                    if self.option3 == '7':
                        self.option1 = ''
                        break
                    else:
                        if self.option3 == '1':
                            while (command != '10' and command != '11'):
                                command = input(
                                    '请输入需要进行的操作代号（例如：1）：\n\n0.关闭VPN功能 \n\n1.开启VPN功能 \n\n')
                                command = self.option3 + command
                        elif self.option3 == '2':
                            while (command != '20' and command != '21'):
                                command = input(
                                    '请输入需要进行的操作代号（例如：1）：\n\n0.关闭wan口 \n\n1.开启wan口 \n\n')
                                command = self.option3 + command
                        elif self.option3 == '3':
                            while (command != '30' and command != '31' and command != '32'):
                                command = input(
                                    '请输入需要进行的操作代号（例如：1）：\n\n0.关闭wifi功能 \n\n1.开启wifi ap模式 \n\n2.开启wifi所有模式 \n\n')
                                command = self.option3 + command
                        elif self.option3 == '4':
                            while (command != '40' and command != '41'):
                                command = input(
                                    '请输入需要进行的操作代号（例如：1）：\n\n0.开启DTU功能 \n\n1.关闭DTU功能 \n\n')
                                command = self.option3 + command
                        elif self.option3 == '5':
                            while (command != '50' and command != '51'):
                                command = input(
                                    '请输入需要进行的操作代号（例如：1）：\n\n0.中文版本 \n\n1.英文版本 \n\n')
                                command = self.option3 + command
                        elif self.option3 == '6':
                            while (command != '60' and command != '61'):
                                command = input(
                                    '请输入需要进行的操作代号（例如：1）：\n\n0.标准版本 \n\n1.OEM版本 \n\n')
                                command = self.option3 + command
                        nvram = self.getNvramInfo()
                        self.setNvramInfo(command, nvram)
                    time.sleep(2)
        else:
            if count > 1:
                print('路由器连接失败，确认连接无误后点回车继续')
                self.start(count - 1)
            else:
                print('多次连接失败，请检查连接')


if __name__ == '__main__':
    conn = Hdrouter()
    conn.start(3)
