#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-01-25 22:23:32
# @Author  : Claus Chen (245618722@qq.com)
# @Link    : https://github.com/clauschen121


from urllib import request, error
import re
import os
import time
import socket
import threading
import random


class Spider:

    def __init__(self, url, count):
        self.count = count
        self.url_list = []
        self.lock = threading.Lock()
        if not url:
            self.url = 'http://www.055i.com/taotu/12655.html'
        self.user_agent_list = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
            "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
        ]
        self.website = '/'.join(self.url.split('/')[0:3]) + '/'

    def header_choice(self):
        UA = random.choice(self.user_agent_list)
        headers = {'User-Agent': UA}
        return headers

    def getPage(self, url, count):
        try:
            req = request.Request(url, headers=self.header_choice())
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
            url = self.website + result.group(1).strip()
            with self.lock:
                self.url_list.append(url)
                print('新增网址：%s到列表中' % url)
            return url
        else:
            return None

    def saveImage(self, imageUrl, fileName, count):
        if os.path.exists(fileName):
            print('图片存在，跳过')
            return
        try:
            req = request.Request(imageUrl, headers=self.header_choice())
            image = request.urlopen(req, timeout=10).read()
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

    def saveAllImage(self, path):
        if len(self.url_list):
            with self.lock:
                url = self.url_list.pop()
        else:
            print('无多余的图片可以下载，退出')
            return
        n = 1
        page = self.getPage(url, 3)
        if page is None:
            print('网址%s多次连接失败，请更换网址' % url)
            return
        title = self.getTitle(page)
        title = re.sub('[*?\\\\/|"<>:]', '', title)
        pageNum = self.getPageNum(page)
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
        if len(self.url_list):
            self.saveAllImage(path)
        else:
            print('没有更多的链接了，请尝试用其他的基准链接地址获取图片')

    def run(self, path):
        url = self.url
        thread_list = []
        while self.count > 1:
            page = self.getPage(url, 3)
            url = self.getNext(page)
            if url:
                self.count -= 1
            else:
                break
        for i in range(20):
            t = threading.Thread(target=self.saveAllImage, args=(path,))
            t.start()
            thread_list.append(t)

        for t in thread_list:
            t.join()


if __name__ == '__main__':
    baseUrl = input(
        '请输入主贴链接地址，例如：http://www.055i.com/taotu/12655.html，如使用默认，则直接按回车\n')
    dlpath = input('请输入用于存储图片的文件夹地址，例如：F:/downloads/\n')
    count = input('请输入要存储的帖子数量，一个帖子可能会有几十张图，数字尽量不要超过100，已避免下载时间太长\n')
    while not os.path.exists(dlpath):
        os.makedirs(dlpath)
    while not count.isdigit():
        count = input('您输入的帖子数量有误，请重新输入:\n')

    spider = Spider(baseUrl, int(count))
    nexturl = spider.run(dlpath)
    print('下载已完成，请进入相应文件夹查看')
    input('输入任意键退出')
