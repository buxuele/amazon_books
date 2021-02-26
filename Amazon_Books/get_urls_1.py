# -*- coding: utf-8 -*-
# author: fanchuang
# DateTime:2021/2/22 0022 19:17 
# contact: fanchuangwater@gmail.com
# about:

from utils.my_timer import timer
from utils.mongoDB import Mongo
from utils.get_user_agent import get_a_ua

import requests
from pprint import pprint
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from config import books_db, book_urls_coll

""" 
获取所有的图书链接，分一层来操作。 Mongo("amazon_books", "computer_book_urls")
"""


class RequestsClass:
    def __init__(self):
        self.mongo_db = Mongo(books_db, book_urls_coll)
        # self.mongo_db = Mongo("amazon_books", "computer_book_urls")     # 唯一的个数是：  6398
        self.session = requests.Session()

    def visit(self, url):
        # p = random.choice(self.proxy_pool)
        h = {'User-Agent': get_a_ua()}
        resp = self.session.get(url, headers=h)
        if resp.status_code == 200:
            # print(resp.text)
            return resp

    def visit2(self, url):
        # todo 后续的话，可以尝试这种思路, 目前舍弃
        # 观察网站，可以用 POST 来获取 XHR, 然后再解析每一本书的 url。
        # 给自己挖坑啊。返回的结果是一种亚马逊自定义的数据结构， 解析起来笔记费劲。

        # p = random.choice(self.proxy_pool)
        h = {'User-Agent': get_a_ua(),
             'Content-Type': 'application/json',
             'Accept-Encoding': 'gzip',
             }
        payload = {"customer-action": "pagination"}

        # 用post试试呢？？
        resp = self.session.post(url, headers=h, json=payload)
        if resp.status_code == 200:
            print(resp.text)
            return resp

    # 解析书籍的基本信息
    def parse_data(self, url):
        html = self.visit(url)
        if html:
            print("ok")
            soup = BeautifulSoup(html.text, "lxml")
            h2_text = soup.find_all("h2", attrs={'class': 'a-size-mini a-spacing-none a-color-base s-line-clamp-2'})
            # pprint(h2_text)
            if h2_text:
                base = "https://www.amazon.cn"
                book_urls = [base + a.find('a').get("href") for a in h2_text]
                self.mongo_db.insert_bulk_data(book_urls)

    def save_data(self):
        # 1. 直接保存到 MongoDB，比较简洁。 Excel, MongoDB, Json. 3种方式都写一些。 然后把三种方式汇总到一个文件。
        # 2. MongoDB 再保存到 Excel 视觉效果会更好一些
        pass

    @timer
    def show_data(self):
        self.mongo_db.get_unique(show=True)

    # 多线程。控制在5个线程左右。
    @timer
    def get_all_books(self):
        # base_url = "https://www.amazon.cn/s?i=digital-text&rh=n%3A143359071&fs=true&page=9"
        urls = [f"https://www.amazon.cn/s?i=digital-text&rh=n%3A143359071&fs=true&page={i}" for i in range(1, 401)]
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_tasks = [executor.submit(self.parse_data, g) for g in urls]
            wait(future_tasks, return_when=ALL_COMPLETED)


if __name__ == '__main__':
    r = RequestsClass()
    # u = "https://www.amazon.cn/s?i=digital-text&rh=n%3A143359071&fs=true&page=31"
    # r.parse_data(u)
    # r.get_all_books()

    r.show_data()




























