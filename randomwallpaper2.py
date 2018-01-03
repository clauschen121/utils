#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-08-25 09:42:12
# @Author  : Claus Chen (245618722@qq.com)
# @Link    : https://github.com/clauschen121


from urllib import request
import random
import re
import win32gui
import win32con
import win32api
import os


class ChangeWallPaper():

    def __init__(self):
        self.dirpath = 'D:/wallpaper/'
        self.url = 'http://desk.zol.com.cn'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'}
        self.imagepath = ''
        self.imageurl = ''

    def getPage(self, url, count):
        try:
            req = request.Request(url, headers=self.headers)
            page = request.urlopen(req, timeout=20).read().decode('gbk')
            return page
        except:
            if count > 1:
                self.getPage(url, count - 1)
            else:
                print('多次连接失败')
                return None

    def getTypeUrl(self, page):
        try:
            i = random.randint(1, 19)
            pattern1 = re.compile('壁纸分类(.*?)壁纸尺寸', re.S)
            bizhi = re.search(pattern1, page).group(1)
            pattern2 = re.compile('href="(.*?)"', re.S)
            urls = re.findall(pattern2, bizhi)
            newurl = self.url + urls[i]
            return newurl
        except:
            print('图片分类不匹配，可能网站更换了结构')
            return None

    def getImageLib(self, page):
        try:
            pattern = re.compile('photo-list-padding.*?href="(.*?)"', re.S)
            urls = re.findall(pattern, page)
            n = random.randint(0, 14)
            newurl = self.url + urls[n]
            return newurl
        except:
            print('图片集合不匹配，可能网站更换了结构')
            return None

    def getImageInfo(self, page):
        try:
            pattern1 = re.compile('show1.*?src="(.*?)"', re.S)
            urls = re.findall(pattern1, page)
            m = random.randint(0, 3)
            newurl = urls[m]
            self.imagepath = self.dirpath + newurl[-20:]
            pattern2 = re.compile('t_s(.*?)c5', re.S)
            replaced = re.search(pattern2, newurl).group(1)
            self.imageurl = newurl.replace(replaced, '1920x1080')
            return True
        except:
            print('图片链接不匹配，可能网站更换了结构')
            return None

    def saveImage(self, url, count):
        try:
            req = request.Request(url, headers=self.headers)
            print('正在下载图片')
            imagedata = request.urlopen(req, timeout=30).read()
            print('正在保存图片')
            with open(self.imagepath, 'wb') as f:
                f.write(imagedata)
            print('图片已经保存到本地')
            return True
        except:
            print('图片保存失败')
            if count > 1:
                print('正在重试下载图片')
                self.saveImage(url, count - 1)
            else:
                print('多次保存失败')
                return False

    def mkdir(self):
        isExists = os.path.exists(self.dirpath)
        if not isExists:
            os.mkdir(self.dirpath)
            print('正在创建%s目录' % self.dirpath)
        else:
            print('目录%s已经创建' % self.dirpath)

    def changeWP(self):
        try:
            print('正在更换背景图片')
            reg_key = win32api.RegOpenKeyEx(
                win32con.HKEY_CURRENT_USER, 'Control Panel\\Desktop', 0, win32con.KEY_SET_VALUE)
            win32api.RegSetValueEx(
                reg_key, 'WallpaperStyle', 0, win32con.REG_SZ, '2')
            win32api.RegSetValueEx(
                reg_key, 'TileWallpaper', 0, win32con.REG_SZ, '0')
            win32gui.SystemParametersInfo(
                win32con.SPI_SETDESKWALLPAPER, self.imagepath, win32con.SPIF_SENDWININICHANGE)
            print('背景图片更换成功')
            return True
        except:
            print('更换背景图片发生错误')
            return None

    def start(self, count):
        homepage = self.getPage(self.url, 3)
        typeurl = self.getTypeUrl(homepage)
        typepage = self.getPage(typeurl, 3)
        imageliburl = self.getImageLib(typepage)
        imagepage = self.getPage(imageliburl, 3)
        imageinfo = self.getImageInfo(imagepage)
        result = self.saveImage(self.imageurl, 3)
        if not result:
            if count > 1:
                print('正在重启应用')
                self.start(count - 1)
            else:
                print('多次重启仍无法下载图片，请过一段时间重试')
                return
        else:
            result2 = self.changeWP()
            if not result2:
                if count > 1:
                    print('正在重启应用')
                    self.start(count - 1)
                else:
                    print('多次重启仍无法下载图片，请过一段时间重试')
                    return
            else:
                return


cwp = ChangeWallPaper()
cwp.mkdir()
cwp.start(3)
ct = input('重换一张按enter键，退出输入q或者直接关闭该应用\n')
while ct != 'q':
    cwp.start(3)
    ct = input('重换一张按enter键，退出输入q或者直接关闭该应用\n')
