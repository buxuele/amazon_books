# -*- coding: utf-8 -*-
# date: 2021/2/17 0017 
# author: fanchuang
# contact: fanchuangwater@gmail.com
# about:


import os
import time
import shutil
import zipfile
import json
import requests
from pprint import pprint

from utils.my_timer import timer
from utils.get_user_agent import get_a_ua
from utils.mongoDB import Mongo
from config import proxy_db, proxy_coll                               # 根目录 数据库名称。

from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED


""" 
1. 下载 github 上这个代理，https://github.com/fate0/proxylist
2. 每15分钟更新一次的。数量也很多。
3. 当前这个文件是独立的。下载 + 校验 + 好用。当前是够用了，日后再考虑合并。
"""


# todo 日后考虑定时执行，每15分钟一次，保持最新的状态。
class SecondProxy:
    def __init__(self, china=True):
        self.country = china
        self.m = Mongo(proxy_db, proxy_coll)
        self.headers = {'User-Agent': get_a_ua()}
        self.real_ip = self.find_myself()

    @staticmethod
    def find_myself():
        target = 'http://httpbin.org/ip'
        resp = requests.get(target)
        return resp.json()["origin"]

    # 完成任务后，删除用过的临时文件，防止下次出错。
    @staticmethod
    def clear_space():
        temp_zip = "temp_file.zip"
        if temp_zip in os.listdir():
            os.remove(temp_zip)
        if 'proxylist-master' in os.listdir():
            shutil.rmtree(os.path.normpath('proxylist-master'))

    @staticmethod
    def clone_zip():
        temp_zip = "temp_file.zip"
        food = []

        # 1. 下载
        url = "https://github.com/fate0/proxylist/archive/master.zip"
        ret = requests.get(url)
        if ret.status_code == 200:
            with open(temp_zip, "wb") as f:
                f.write(ret.content)
        else:
            print("Internet broken!")
        print("Download github proxy finished!")

        # 2. 解压，分析。
        if temp_zip in os.listdir():
            with zipfile.ZipFile(temp_zip, 'r') as zzz:
                zzz.extractall()  # 解压全部文件，并保存到当前文件目录

        # 3. 读取，解析这批代理文件
        os.chdir('proxylist-master')
        with open('proxy.list', 'r') as g:
            for d in g.readlines():
                proxy = json.loads(d)
                # print(proxy)
                c = f'{proxy["type"]}://{proxy["host"]}:{proxy["port"]}'
                print(c)
                food.append(c)
        return food

    def speed_status(self, proxy=None):
        url = "http://httpbin.org/ip"
        if proxy.startswith("http://"):
            checking_proxies = {"http": proxy}
        else:
            checking_proxies = {"https": proxy}
        resp = requests.get(url, proxies=checking_proxies, timeout=1)
        # 只有当前使用的代理与自己真实的ip 不相等的时候，才说明这个代理是有效的。
        if resp.status_code == 200 and resp.json()["origin"] != self.real_ip:
            print("test ip", proxy)
            print("real ip : ", resp.json()["origin"])
            self.m.add_to_db({"url": proxy})

    @timer
    def run(self):
        fake_proxy = self.clone_zip()
        # 这里的数量有点多，所以给50个线程。
        with ThreadPoolExecutor(max_workers=50) as executor:
            future_tasks = [executor.submit(self.speed_status, p) for p in fake_proxy]
            wait(future_tasks, return_when=ALL_COMPLETED)

    def show_product(self):
        self.m.get_unique(show=True)


if __name__ == '__main__':
    s = SecondProxy()
    s.clear_space()  # 注意打扫卫生啊。
    # s.run()
    # s.show_product()










