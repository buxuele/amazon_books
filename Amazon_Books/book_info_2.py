# -*- coding: utf-8 -*-
# author: fanchuang
# DateTime:2021/2/22 0022 15:18 
# contact: fanchuangwater@gmail.com
# about: 尝试用自己的一套东西来 爬取亚马逊官网的图书信息
# 如果效果不错的话，后期可以试试看用 scrapy

import re
from utils.mongoDB import Mongo
from utils.logger import logger
from utils.get_user_agent import get_a_ua
from config import books_db, book_urls_coll, book_info_coll, proxy_db, proxy_coll
from utils.req_headers import make_headers
import requests
from bs4 import BeautifulSoup
from pprint import pprint
from retry import retry


""" 
这个文件的目的：
1. 看看单独请求一个页面是否会有问题。
2. 尝试一些小功能。
"""


class BookInfo:
    def __init__(self):
        self.food = {}          # 以一个字典的形式, 临时保存每本书的信息
        self.session = requests.Session()
        # self.proxy_pool = Mongo(proxy_db, proxy_coll).get_unique()
        self.book_urls = Mongo(books_db, book_urls_coll)
        self.book_db = Mongo(books_db, book_info_coll)

    @staticmethod
    def make_headers():
        # 这里删除 真实的UA, 删除 cookies,
        raw_text = "../data/headers2.txt"
        h = {'User-Agent': get_a_ua()}
        dic = {}
        with open(raw_text, 'r') as f:
            for a in f.readlines():
                # print(len(a.strip().split(": ")))     # 注意这里是一个 冒号加上一个空格
                x, y = a.strip().split(": ")
                dic[x] = y
        dic.update(h)
        # pprint(dic)
        return dic


    def visit(self, url):
        # p = random.choice(self.proxy_pool)
        # if p.startswith("http://"):
        #     use_proxies = {"http": p}
        # else:
        #     use_proxies = {"https": p}
        h = make_headers()
        print(h)

        try:
            # resp = self.session.get(url, headers=h, proxies=use_proxies, allow_redirects=False)
            resp = self.session.get(url, headers=h, allow_redirects=False)
            if resp.status_code == 200:
                # 这里可能会跳转到登录界面。导致后面的解析出错。
                # print(resp.text)
                # print(resp.url)     # 看看响应的url 与请求的url有什么不同。
                return resp
        except ConnectionError as e:
            logger(f"bad url: {url}")

    # 解析书籍的信息，大致分3部分。

    def parse_data(self, url):
        html = self.visit(url)
        if html:
            soup = BeautifulSoup(html.text, "lxml")
            # todo 标题 = 书名 + 副标题， 不太容易分开, 因为空格的位置不规则。
            book_name = soup.find('span', attrs={'id': 'productTitle'}).text.strip()
            self.food["book_name"] = book_name
            self.food["book_url"] = url

            price = soup.find('span', attrs={'class': 'a-size-base a-color-price a-color-price'}).text.strip()
            self.food["price"] = price

            author = soup.find('span', attrs={'class': 'author notFaded'}).find('a').text.strip()
            self.food["author"] = author

            img_box = soup.find('div', attrs={'id': 'ebooks-img-canvas'})
            book_image_url = img_box.find('img', src=re.compile(r'https://images-cn.ssl-images-amazon.cn/images/I/\w+'))
            self.food["book_image_url"] = book_image_url.get("src")

            description = soup.find('div', attrs={'id': 'bookDescription_feature_div'})  # yes
            if description:
                self._parse_description(description)
            else:
                # todo: handle error
                print("failed on this book, please handle error!!!")

            publish_info = soup.find('div', attrs={'id': 'detailBullets_feature_div'})
            if publish_info:
                self._parse_publish_info(publish_info)
            else:
                print("failed on this book, please handle error!!!")
            # self.book_db.add_to_db(self.food)


    # 紧接着处理解析书籍的描述信息
    def _parse_description(self, ele):
        # 返回的一段很长的文本。编辑推荐：/ 作者介绍：/ 内容简介,内容介绍 这3块，有些是省缺的, 那就是写 无。
        raw = ele.text.strip().split("\n")[0]
        chunk = raw.strip().split("\n")[0]
        if chunk.startswith("编辑"):
            reason, other = chunk.split("作者")                # 作者介绍，也许是不存在的。todo
            author_info, book_about = other.split("内容")      # 内容 是一定有的
        else:
            # 这是一块内容,只保留给书籍信息。
            reason = ''
            book_about = chunk.strip()
            author_info = ''
        self.food["recommend_reason"] = reason
        self.food["author_info"] = author_info
        self.food["book_about"] = book_about

    def _parse_publish_info(self, ele):
        items = ele.find_all("span", attrs={"class": "a-list-item"})
        raw = "".join(i.text for i in items)
        a = [x for x in raw.split("\n") if x and x != ":"]
        # print(a)

        for i, j in enumerate(a):
            if j == "ASIN":
                self.food["ASIN"] = a[i + 1]
            if j == "出版社":
                self.food["publisher"] = a[i + 1]
            if j == "出版日期":
                self.food["publish_time"] = a[i + 1]
            if j == "品牌":
                self.food["brand"] = a[i + 1]
            if j == "语言":
                self.food["language"] = a[i + 1]
            if j == "文件大小":
                self.food["file_size"] = a[i + 1]
            if j == "标准语音朗读":
                self.food["voice_status"] = a[i + 1]
            if j == "X-Ray":
                self.food["X-Ray"] = a[i + 1]
            if j == "纸书页数":
                self.food["pages"] = a[i + 1]
            if j == "亚马逊热销商品排名":
                self.food["selling_rank"] = a[i + 1]
            if j == "用户评分":
                self.food["stars"] = a[i + 1]
            if j == "生词提示功能":
                self.food["reading_helper"] = a[i + 1]

    def show_data(self):
        pprint(self.food)

    # def save_data(self):
    #     # 这里也是需要检查一下看看 food 里面是否有值。如果没有值的话，那么就警告一下。
    #     self.book_db.add_to_db(self.food)


if __name__ == '__main__':
    r = BookInfo()
    # u = 'https://www.amazon.cn/dp/B01HZFHE1U/ref=sr_1_127?dchild=1&qid=1613981559&s=digital-text&sr=1-127'
    u = 'https://www.amazon.cn/dp/B074TBNZLK/ref=sr_1_38?dchild=1&qid=1614070965&s=digital-text&sr=1-38'
    # u = 'https://www.amazon.cn/dp/B0719GSVJB/ref=sr_1_4?dchild=1&qid=1614414899&s=digital-text&sr=1-4'
    # r.visit(u)
    # r.make_headers()

    r.parse_data(u)
    r.show_data()











