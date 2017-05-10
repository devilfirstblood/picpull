# -*- coding:utf-8 -*-

import requests
import re
import os

import sys

import time
from bs4 import BeautifulSoup

s = requests.Session()


class Pixiv:
    def __init__(self):
        self.baseUrl = "https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index"
        self.LoginUrl = "https://accounts.pixiv.net/api/login?lang=zh"
        self.loginHeader = {
            'Host': "accounts.pixiv.net",
            'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36",
            'Referer': "https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index",
            'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8",
            'Connection': "keep-alive"
        }
        self.return_to = "http://www.pixiv.net/"
        self.pixiv_id = 'xxx',
        self.password = 'xx'
        self.postKey = []
        self.savedUrlList = []  # 存放存储过的图片的url

    # 获取此次session的post_key
    def getPostKeyAndCookie(self):
        loginHtml = s.get(self.baseUrl)
        pattern = re.compile('<input type="hidden".*?value="(.*?)">', re.S)
        result = re.search(pattern, loginHtml.text)
        self.postKey = result.group(1)
        print self.postKey
        loginData = {"pixiv_id": self.pixiv_id, "password": self.password, 'post_key': self.postKey,
                     'return_to': self.return_to}
        s.post(self.LoginUrl, data=loginData, headers=self.loginHeader)

        # 获取页面

    def getPageWithUrl(self, url):
        count = 0
        while count < 5:
            try:
                print '=======count:%d=========url:%s' % (count, url)
                text = s.get(url).text
                count = 5
                return text
            except:
                time.sleep(30)
                count = count + 1

        # 输入文件夹名，创建文件夹

    def mkdir(self, path, folderName):
        folderName = folderName.strip()
        isExists = os.path.exists(os.path.join(path, folderName))
        if not isExists:
            os.makedirs(os.path.join(path, folderName))
            print u'建了一个名字叫做' + folderName + u'的文件夹！'
            os.chdir(path + '/' + self.tag)  # 切换到目录
            self.rootPath = os.getcwd()
            return True
        else:
            print u'名字叫做' + folderName + u'的文件夹已经存在了！'
            os.chdir(path+'/'+self.tag)  # 切换到目录
            self.rootPath = os.getcwd()

            # 下载指定url的图片

    def getBigImg(self, sourceUrl, wholePageUrl,nnnnn):
        header = {
            'Referer': wholePageUrl,
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36'
        }
        if sourceUrl in self.savedUrlList:
            print '该图片已经存在，不用再次保存，跳过！'
        else:
            self.savedUrlList.append(sourceUrl)
            a = sourceUrl.split('/')
            name = a[a.__len__() - 1]

            ppp = os.getcwd() + '/' + name
            imgExist = os.path.exists(ppp)  # 如果存在重名的，则给name加1重新命名
            print ppp
            if (imgExist):
                name = 're' + name
                print u'存在重名图片，重新命名为: ' + name

            count = 0
            while count < 5:
                try:
                    print '=======count:%d=========url:%s' % (count, sourceUrl)
                    img = s.get(sourceUrl, headers=header)
                    f = open(name, 'wb')  # 写入多媒体文件要b这个参数
                    f.write(img.content)  # 多媒体文件要是用conctent！
                    f.close()

                    f = open('saved_url.txt', 'a')
                    f.write(sourceUrl + '\n')
                    f.close()
                    count = 5
                    break
                except:
                    time.sleep(10)
                    count = count + 1

    def getImg(self, url):

        # 查找本页面内最大分辨率的图片的url的正则表达式
        singleImgePattern = re.compile('<div class="_illust_modal.*?<img alt="(.*?)".*?data-src="(.*?)".*?</div>', re.S)
        wholePageUrl = 'http://www.pixiv.net' + str(url)
        pageHtml = self.getPageWithUrl(wholePageUrl)

        singleImgResult = re.search(singleImgePattern, pageHtml)  # 如果这个页面只有一张图片，那就返回那张图片的url和名字，如果是多张图片 那就找不到返回none
        # 单图的获取方法
        if (singleImgResult):
            imgName = singleImgResult.group(1)
            imgSourceUrl = singleImgResult.group(2)
            print u'这个地址含有1张图片，地址：' + wholePageUrl
            print u'正在获取第1张图片.....'
            print u'名字: ' + singleImgResult.group(1)
            print u'源地址：' + singleImgResult.group(2)
            self.getBigImg(imgSourceUrl, wholePageUrl, imgName)
            print 'Done!'
            print '--------------------------------------------------------------------------------------------------------'
            # 多图的获取方法
        else:
            wholePageUrl = str(wholePageUrl).replace("medium", "manga")
            pageHtml = self.getPageWithUrl(wholePageUrl)
            totalNumPattern = re.compile('<span class="total">(\d*)</span></div>', re.S)  # 找到这一页共有几张图
            totalNum = re.search(totalNumPattern, pageHtml)
            if (totalNum):  # 如果是动图get不到这个num,返回的是none
                print u'这个地址含有' + totalNum.group(1) + u'张图片，地址：' + str(wholePageUrl)
                urlPattern = re.compile('<div class="item-container.*?<img src=".*?".*?data-src="(.*?)".*?</div>', re.S)
                namePattern = re.compile('<section class="thumbnail-container.*?<a href="/member_illust.*?>(.*?)</a>',
                                         re.S)
                urlResult = re.findall(urlPattern, pageHtml)
                nameResult = re.search(namePattern, pageHtml)
                for index, item in enumerate(urlResult):
                    # item = item.replace('img-master', 'img-original').replace('_master1200.jpg', '.png')
                    print u'正在获取第' + str(index + 1) + u'张图片......'
                    print u'名字: ' + nameResult.group(1) + str(index + 1)
                    print u'源地址：' + item
                    self.getBigImg(item, wholePageUrl, nameResult.group(1) + str(index + 1))
                    print 'Done!'
                    print '--------------------------------------------------------------------------------------------------------'
            else:
                print '这个网址是一个gif，跳过!'
                print 'Done!'
                print '--------------------------------------------------------------------------------------------------------'

    def start(self):
        self.tag = raw_input('Please input the tag: ').decode('utf-8')
        # self.page = int(raw_input('Please input the page you want to start from: '))
        # self.resolution = int(raw_input('Please input the resolution, from 1 to 3, 1 is highest resolution: '))
        # self.tag = '4338012'
        self.page = 1

        path = "Pixiv/id"
        self.mkdir(path, self.tag)  # 调用mkdir函数创建文件夹
        if os.path.exists(self.tag + '/saved_url.txt'):
            f = open(self.tag + '/saved_url.txt')
            for line in f:
                self.savedUrlList.append(line.strip('\n') )
            f.close()


        self.getPostKeyAndCookie()  # 获得此次会话的post_key和cookie

        for pageNum in range(self.page, 100):
            url = "https://www.pixiv.net/member_illust.php?id=%s&type=all&p=%d" % (self.tag, pageNum)
            pageHtml = self.getPageWithUrl(url)  # 获取该页html
            pageSoup = BeautifulSoup(pageHtml, 'lxml')
            imgItemsResult = pageSoup.find_all("ul",class_="_image-items")  # 找到20张图片所在的标签，返回的list长度为1
            imgItemsSoup = BeautifulSoup(str(imgItemsResult), 'lxml')
            imgItemResult = imgItemsSoup.find_all("li", class_="image-item")  # 找到每张图片所在的标签，返回list长度应为20
            imgUrlPattern = re.compile('<a href="(.*?)"><h1.*?</h1>', re.S)  # 在该图片所在image-item标签里找到url和收藏数
            imgStarsPattern = re.compile('<ul class="count-list.*?data-tooltip="(\d*).*?".*?</ul>', re.S)
            for imgItem in imgItemResult:
                imgUrl = re.search(imgUrlPattern, str(imgItem))
                os.chdir(self.rootPath)  # 切换到对应目录
                self.getImg(imgUrl.group(1))

p = Pixiv()
p.start()  