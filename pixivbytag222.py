# -*- coding:utf-8 -*-
import json

import requests
import re
import os

import time

import threadpool
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
        self.password = 'xxx'
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
            print self.rootPath
            os.makedirs(os.path.join(self.rootPath, "1-50"))
            os.makedirs(os.path.join(self.rootPath, "51-300"))
            os.makedirs(os.path.join(self.rootPath, "301-1000"))
            os.makedirs(os.path.join(self.rootPath, "1000+"))
            print u'在' + folderName + u'文件夹下建立了 1-50 51-300 301-1000 1000+ 4个文件夹'
            return True
        else:
            print u'名字叫做' + folderName + u'的文件夹已经存在了！'
            os.chdir(path + '/' + self.tag)  # 切换到目录
            self.rootPath = os.getcwd()

            # 下载指定url的图片

    def getBigImg(self, sourceUrl, wholePageUrl, name):
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

            ppp = name
            print ppp

            img = s.get(sourceUrl, headers=header)
            f = open(ppp, 'wb')  # 写入多媒体文件要b这个参数
            f.write(img.content)  # 多媒体文件要是用conctent！
            f.close()

    def getImg(self, url):
        wholePageUrl = 'http://www.pixiv.net' + str(url)
        pageHtml = self.getPageWithUrl(wholePageUrl)

        soup = BeautifulSoup(pageHtml, 'lxml')
        # wrapper > div._illust_modal.ui-modal-close-box > div > img
        origins = soup.select('div._illust_modal.ui-modal-close-box > div > img')
        img_origin = None
        for origin in origins:
            img_origin = str(origin.get('data-src'))
        if img_origin:
            print u'这个地址含有1张图片，地址：' + wholePageUrl
            print u'正在获取第1张图片.....'
            print u'源地址：' + img_origin
            self.getBigImg(img_origin, wholePageUrl, '')
            print 'Done!'
            print '--------------------------------------------------------------------------------------------------------'
        else:
            wholePageUrl = str(wholePageUrl).replace("medium", "manga")
            pageHtml = self.getPageWithUrl(wholePageUrl)

            soup = BeautifulSoup(pageHtml, 'lxml')
            # main > section > div:nth-child(2) > img
            origins = soup.select('section > div > img')

            print u'这个地址含有' + str(len(origins)) + u'张图片，地址：' + wholePageUrl
            for index, origin in enumerate(origins):
                img_origin = str(origin.get('data-src'))
                print u'正在获取第' + str(index + 1) + u'张图片.....'
                print u'源地址：' + img_origin
                self.getBigImg(img_origin, wholePageUrl, '')
                print 'Done!'
                print '--------------------------------------------------------------------------------------------------------'


    def start(self):
        # self.tag = raw_input('Please input the tag: ').decode('utf-8')
        # self.page = int(raw_input('Please input the page you want to start from: '))
        # self.resolution = int(raw_input('Please input the resolution, from 1 to 3, 1 is highest resolution: '))
        self.tag = u'2b'
        p = '1'
        self.page = int(p)

        path = "Pixiv/tag"
        self.mkdir(path, self.tag)  # 调用mkdir函数创建文件夹

        self.getPostKeyAndCookie()  # 获得此次会话的post_key和cookie

        for pageNum in range(self.page, 2):
            url = "http://www.pixiv.net/search.php?word=%s&s_mode=s_tag_full&order=date_d&type=illust&p=%d" % (
                self.tag, pageNum)
            pageHtml = self.getPageWithUrl(url)  # 获取该页html
            pageSoup = BeautifulSoup(pageHtml, 'lxml')
            # wrapper > div.layout-body > div:nth-child(1) > section.column-search-result > ul > li:nth-child(1) > a.work._work
            imgs = pageSoup.select('div.layout-body > div > section.column-search-result > ul > li > a.work._work')
            # wrapper > div.layout-body > div:nth-child(1) > section.column-search-result > ul > li:nth-child(1) > ul > li > a
            stars = pageSoup.select('div.layout-body > div > section.column-search-result > ul > li > ul > li > a')
            for img, star in zip(imgs, stars):
                img_url = img.get('href')
                try:
                    star_count = int(star.get_text())
                except:
                    star_count = 0

                if star_count <= 50:
                    os.chdir(self.rootPath + '/1-50')  # 切换到对应目录
                    self.getImg(img_url)
                elif star_count <= 300:
                    os.chdir(self.rootPath + '/51-300')
                    self.getImg(img_url)
                elif star_count <= 1000:
                    os.chdir(self.rootPath + '/301-1000')
                    self.getImg(img_url)
                else:
                    os.chdir(self.rootPath + '/1000+')
                    self.getImg(img_url)

    def get_next_url(self,url,pool):
        html = s.get(url)
        data = json.loads(html.content)
        body = data.get('body')
        content = body.get('html')
        pageSoup = BeautifulSoup(content, 'lxml')
        items = pageSoup.select('div.thumbnail-container > a')

        urls = []
        for item in items:
            urls.append(item.get('href'))
        requests = threadpool.makeRequests(self.getImg,urls)
        [pool.putRequest(req) for req in requests]
        pool.wait()
        return body.get('next_url')

    def start2(self):
        self.tag = raw_input('Please input the tag: ').decode('utf-8')
        path = "Pixiv/contest"
        self.mkdir(path, self.tag)  # 调用mkdir函数创建文件夹
        self.getPostKeyAndCookie()  # 获得此次会话的post_key和cookie

        # urll = 'https://www.pixiv.net/rpc/whitecube/index.php?q=FGO%E3%82%A4%E3%83%A9%E3%82%B3%E3%83%B3&type=all&s_mode=s_tag_full&adult_mode=exclude&deny_user_ids_string=1482890&mode=contest_entries&p=1&tt=a5f453ea6ef33a7851423284826579b6'
        urll = 'https://www.pixiv.net/rpc/whitecube/index.php?q=%s&type=all&s_mode=s_tag_full&adult_mode=exclude' \
               '&deny_user_ids_string=1482890&mode=contest_entries&p=1&tt=a5f453ea6ef33a7851423284826579b6' % self.tag
        pool = threadpool.ThreadPool(50)
        while True:
            next_url = self.get_next_url(urll,pool)
            if next_url:
                urll = 'https://www.pixiv.net' + next_url
                print urll
            else:
                break

p = Pixiv()
# p.start()
p.start2()
