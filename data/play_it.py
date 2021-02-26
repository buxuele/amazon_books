# -*- coding: utf-8 -*-
# author: fanchuang
# DateTime:2021/2/23 0023 19:46 
# contact: fanchuangwater@gmail.com
# about:

import time
import random
from utils.get_user_agent import get_a_ua
from utils.mongoDB import Mongo
from utils.logger import logger
from utils.my_timer import timer

import requests
from bs4 import BeautifulSoup
from pprint import pprint


"""
理由:   
1. 爬取全部书籍的url，还没有问题，今天爬没本书的详情，被跳转。
2. 这里进行各种大胆的尝试，看看如何能请求到数据。并且把过程记录下来；

尝试:
1. 同时 使用新的代理 + 重新构造请求头 + 重新构造url, 成功了！！！
2. 经过多番测试，问题还是在于 [请求头] 这里。与其他部分无关。
3. 尝试逐步修改 headers,看看能忍我到什么程度。
   如果删掉 cookies呢 也行的。
   如果修改 User-Agent 呢 也是可行的。
"""


class BookInfo:
    def __init__(self):
        self.food = {}
        self.session = requests.Session()

    @staticmethod
    def make_headers():
        # 这里删除 真实的UA, 删除 cookies,
        raw_text = "headers2.txt"
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
        # h = {'User-Agent': get_a_ua()}
        # p = random.choice(self.proxy_pool)
        # if p.startswith("http://"):
        #     use_proxies = {"http": p}
        # else:
        #     use_proxies = {"https": p}

        h = self.make_headers()
        use_proxies = {"http": 'http://178.63.126.8:1080'}  # 等下更换这个。
        try:
            resp = self.session.get(url, headers=h, allow_redirects=False)
            if resp.status_code == 200:
                # 这里可能会跳转到登录界面。导致后面的解析出错。
                print(resp.text)
                print(resp.url)     # 看看响应的url 与请求的url有什么不同。
                return resp
        except ConnectionError as e:
            logger(f"bad url: {url}")


if __name__ == '__main__':
    r = BookInfo()
    tm = str(time.time()).split(".")[0]
    u = 'https://www.amazon.cn/dp/B01HZFHE1U/ref=sr_1_127?dchild=1&qid=1613981559&s=digital-text&sr=1-127'
    # u = f'https://www.amazon.cn/dp/B074TBNZLK/ref=sr_1_38?dchild=1&qid={tm}&s=digital-text&sr=1-38'
    r.visit(u)
    # r.parse_data(u)
    # r.show_data()




