# -*- coding: utf-8 -*-
# author: fanchuang
# DateTime:2021/2/23 0023 15:32 
# contact: fanchuangwater@gmail.com
# about:

import re
import time
import random

from utils.mongoDB import Mongo
from utils.my_timer import timer
from utils.logger import logger
from utils.get_user_agent import get_a_ua
# from utils.req_headers import make_headers
from config import books_db, book_urls_coll, book_info_coll, proxy_db, proxy_coll

import requests
from bs4 import BeautifulSoup
from pprint import pprint
from retry import retry
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

""" 改写 book_info_2.py 爬取全部的图书信息。"""


# todo 修改自己的代理之后再来跑一下, 现在先搁置了。
class AllBookInfo:
    def __init__(self):
        self.session = requests.Session()
        self.proxy_pool = Mongo(proxy_db, proxy_coll).get_unique()
        self.book_urls = Mongo(books_db, book_urls_coll)
        self.book_db = Mongo(books_db, book_info_coll)
        self.status = 0         # 用做监控的变量

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
        h = self.make_headers()

        p = random.choice(self.proxy_pool)
        if p.startswith("http://"):
            use_proxies = {"http": p}
        else:
            use_proxies = {"https": p}

        try:
            resp = self.session.get(url, headers=h, proxies=use_proxies, allow_redirects=False)
            # resp = self.session.get(url, headers=h, allow_redirects=False)      # 不使用代理。
            if resp.status_code == 200:
                # print(f"working on: {url}")
                # 这里可能会跳转到登录界面。导致后面的解析出错。
                # print(resp.text)
                # print(resp.url)     # 看看响应的url 与请求的url有什么不同。
                return resp
        except ConnectionError as e:
            logger(f"bad url: {url}")
            logger(e)

    # 解析书籍的信息，大致分3部分。
    @retry(ConnectionError, tries=2, delay=10)  # 如果有问题，就停歇 10s
    def parse_data(self, url):
        # 以一个字典的形式, 临时保存每本书的信息
        food = {'ASIN': '', 'X-Ray': '', 'author': '', 'author_info': '', 'book_about': '', 'book_image_url': '', 'book_name': '', 'book_url': '', 'brand': '', 'file_size': '', 'language': '', 'pages': '', 'price': '', 'publish_time': '', 'publisher': '', 'reading_helper': '', 'recommend_reason': '', 'voice_status': ''}
        html = self.visit(url)
        if html:


            soup = BeautifulSoup(html.text, "lxml")
            # todo 标题 = 书名 + 副标题， 不太容易分开, 因为空格的位置不规则。
            book_name = soup.find('span', attrs={'id': 'productTitle'}).text.strip()
            food["book_name"] = book_name
            food["book_url"] = url

            price = soup.find('span', attrs={'class': 'a-size-base a-color-price a-color-price'}).text.strip()
            food["price"] = price

            author = soup.find('span', attrs={'class': 'author notFaded'}).find('a').text.strip()
            food["author"] = author

            img_box = soup.find('div', attrs={'id': 'ebooks-img-canvas'})
            book_image_url = img_box.find('img', src=re.compile(r'https://images-cn.ssl-images-amazon.cn/images/I/\w+'))
            food["book_image_url"] = book_image_url.get("src")

            # 紧接着处理解析书籍的描述信息
            description = soup.find('div', attrs={'id': 'bookDescription_feature_div'})  # yes
            if description:
                # self._parse_description(description)
                raw = description.text.strip().split("\n")[0]
                chunk = raw.strip().split("\n")[0]
                if chunk.startswith("编辑"):
                    reason, other = chunk.split("作者")  # 作者介绍，也许是不存在的。todo
                    author_info, book_about = other.split("内容")  # 内容 是一定有的
                else:
                    # 这是一块内容,只保留给书籍信息。
                    reason = ''
                    book_about = chunk.strip()
                    author_info = ''
                food["recommend_reason"] = reason
                food["author_info"] = author_info
                food["book_about"] = book_about
            else:
                logger("failed on this book, please handle error!!!")

            publish_info = soup.find('div', attrs={'id': 'detailBullets_feature_div'})
            if publish_info:
                # self._parse_publish_info(publish_info)
                items = publish_info.find_all("span", attrs={"class": "a-list-item"})
                raw = "".join(i.text for i in items)
                a = [x for x in raw.split("\n") if x and x != ":"]

                for i, j in enumerate(a):
                    if j == "ASIN":
                        food["ASIN"] = a[i + 1]
                    if j == "出版社":
                        food["publisher"] = a[i + 1]
                    if j == "出版日期":
                        food["publish_time"] = a[i + 1]
                    if j == "品牌":
                        food["brand"] = a[i + 1]
                    if j == "语言":
                        food["language"] = a[i + 1]
                    if j == "文件大小":
                        food["file_size"] = a[i + 1]
                    if j == "标准语音朗读":
                        food["voice_status"] = a[i + 1]
                    if j == "X-Ray":
                        food["X-Ray"] = a[i + 1]
                    if j == "纸书页数":
                        food["pages"] = a[i + 1]
                    if j == "亚马逊热销商品排名":
                        food["selling_rank"] = a[i + 1]
                    if j == "用户评分":
                        food["stars"] = a[i + 1]
                    if j == "生词提示功能":
                        food["reading_helper"] = a[i + 1]
            else:
                logger("failed on this book, please handle error!!!")

        if len([j for j in food.values() if j]) < 10:   # 总共18项内容，如果少于10项，那么就重试
            print("数据不完整，正在重试中...")
            # todo retrying
        else:
            self.status += 1
            print(f"{self.status}working on: {url}")
            self.book_db.coll.insert_one(food)
        # time.sleep(random.random() * 4)

    def get_book_urls(self):
        urls = [x["url"] for x in self.book_urls.coll.find()]
        # print(urls)
        return urls

    @timer
    def run(self):
        urls = self.get_book_urls()
        # 线程数 2，不能给的太多了。
        with ThreadPoolExecutor(max_workers=30) as executor:
            future_tasks = [executor.submit(self.parse_data, u) for u in urls]
            # future_tasks = [executor.submit(self.visit, u) for u in urls]
            wait(future_tasks, return_when=ALL_COMPLETED)


if __name__ == '__main__':
    r = AllBookInfo()
    # u = 'https://www.amazon.cn/dp/B01HZFHE1U/ref=sr_1_127?dchild=1&qid=1613981559&s=digital-text&sr=1-127'
    # u = 'https://www.amazon.cn/dp/B074TBNZLK/ref=sr_1_38?dchild=1&qid=1614070965&s=digital-text&sr=1-38'

    # r.parse_data(u)
    # r.get_book_urls()
    r.run()


