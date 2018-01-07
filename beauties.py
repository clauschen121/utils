#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-08-20 22:17:35
# @Author  : Claus Chen (245618722@qq.com)
# @Link    : https://github.com/clauschen121


from urllib import request, error
import re
import os
import time
import socket


class Spider:

    def __init__(self, url='http://www.055i.com/taotu/12655.html'):
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36'
        }
        self.website = '/'.join(self.url.split('/')[0:3]) + '/'

    def getPage(self, url, count):
        try:
            req = request.Request(url, headers=self.headers)
            data = request.urlopen(req, timeout=10).read().decode('utf-8')
            return data
        except error.URLError as e:
            if hasattr(e, 'reason'):
                print('连接网站失败，错误原因：', e.reason)
            if count > 1:
                time.sleep(1)
                print('正在重试连接网站')
                self.getPage(url, count - 1)
            else:
                return None
        except socket.timeout as e:
            if count > 1:
                print('连接超时，正在重试')
                self.getPage(url, count - 1)
            else:
                return None
        except:
            print('未知失败原因')
            return None

    def getTitle(self, page):
        pattern = re.compile('<h1 class="title">(.*?)</h1>', re.S)
        result = re.search(pattern, page)
        if result:
            return result.group(1).strip()
        else:
            return None

    def getImageUrl(self, page):
        urls = []
        pattern = re.compile('<p>.*?img.*?src="(.*?)".*?</p>', re.S)
        result = re.findall(pattern, page)
        if result:
            for item in result:
                urls.append(item)
            return urls
        else:
            return None

    def getPageNum(self, page):
        pattern = re.compile('id="max-page">(.*?)</span>', re.S)
        result = re.search(pattern, page)
        if result:
            return result.group(1).strip()
        else:
            return None

    def getNext(self, page):
        pattern = re.compile('next-post.*?href="(.*?)"', re.S)
        result = re.search(pattern, page)
        if result:
            return self.website + result.group(1).strip()
        else:
            return None

    def saveImage(self, imageUrl, fileName, count):
        if os.path.exists(fileName):
            print('图片存在，跳过')
            return
        try:
            image = request.urlopen(imageUrl, timeout=10).read()
            with open(fileName, 'wb') as f:
                f.write(image)
        except error.URLError as e:
            if hasattr(e, 'reason'):
                print('图片下载失败，错误原因：', e.reason)
            if count > 1:
                time.sleep(1)
                print('正在重试下载图片')
                self.saveImage(imageUrl, fileName, count - 1)
            else:
                print('多次下载失败，跳过')
                return
        except socket.timeout as e:
            if count > 1:
                print('连接超时，正在重试')
                self.saveImage(imageUrl, fileName, count - 1)
            else:
                print('多次超时，跳过')
                return
        except:
            print('未知失败原因，跳过')
            return

    def mkdir(self, path):
        path = path.strip()
        isExists = os.path.exists(path)
        if not isExists:
            os.mkdir(path)
            print('正在创建%s目录' % path)
        else:
            print('目录%s已经创建' % path)

    def saveAllImage(self, url, path, count):
        if url == '':
            url = self.url
        n = 1
        page = self.getPage(url, 3)
        if page is None:
            print('网址%s多次连接失败，请更换网址' % url)
            return
        title = self.getTitle(page)
        title = re.sub('[*?\\\\/|"<>:]', '', title)
        pageNum = self.getPageNum(page)
        nexturl = self.getNext(page)
        imageurls = self.getImageUrl(page)
        newpath = path + title
        self.mkdir(newpath)
        for imageurl in imageurls:
            self.saveImage(imageurl, newpath + '/' + str(n) + '.jpg', 3)
            print('正在保存第%s张图片' % str(n))
            n += 1
        if pageNum:
            for i in range(2, int(pageNum)):
                newurl = url[0:-5] + '_' + str(i) + '.html'
                newpage = self.getPage(newurl, 3)
                if not newpage:
                    print('网页失效，跳过')
                    continue
                newimageurls = self.getImageUrl(newpage)
                if newimageurls:
                    for newimageurl in newimageurls:
                        print('正在保存第%s张图片' % str(n))
                        self.saveImage(newimageurl, newpath +
                                       '/' + str(n) + '.jpg', 3)
                        n += 1
                else:
                    print('网页失效，跳过')
                    continue
        if count > 1:
            if nexturl:
                self.saveAllImage(nexturl, path, count - 1)
            else:
                print('没有更多的链接了，请尝试用其他的基准链接地址获取图片')


baseUrl = input(
    '请输入主贴链接地址，例如：http://www.055i.com/taotu/12655.html，如使用默认，则直接按回车\n')
dlpath = input('请输入用于存储图片的文件夹地址，例如：F:/downloads/，注意：只能使用已经存在的文件夹\n')
count = input('请输入要存储的帖子数量，一个帖子可能会有几十张图，数字尽量不要超过100，已避免下载时间太长\n')
while not os.path.exists(dlpath):
    dlpath = input('您输入的文件夹不存在，请重新输入:\n')
while not count.isdigit():
    count = input('您输入的帖子数量有误，请重新输入:\n')

spider = Spider()
nexturl = spider.saveAllImage(baseUrl, dlpath, int(count))
print('下载已完成，请进入相应文件夹查看')
input('输入任意键退出')
