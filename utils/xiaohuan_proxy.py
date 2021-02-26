import config
import requests
from utils.mongoDB import Mongo
from utils.my_timer import timer
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED


"""
其他项目每次想使用 proxy 的时候，都必须先运行一下此文件。

1. 手动复制代理到 .txt 文件。
2. 更改 代理池数据库的名称。
3. 执行此文件。

看了一圈，下面这种写法是最好的。
1. 把 pool 放在 main 外面。
2. 使用 imap

"""


class Proxy:
    def __init__(self, china=True):
        self.china = china
        self.m = self.m = Mongo(config.proxy_db_name, config.proxy_coll_name)             # 这个保存有效代理是的名称
        self.real_ip = self.find_myself()

    @staticmethod
    def find_myself():
        target = 'http://httpbin.org/ip'
        resp = requests.get(target)
        return resp.json()["origin"]

    def check_proxy(self, url):
        target = 'http://httpbin.org/ip'
        try:
            resp = requests.get(target,  proxies={"http": url}, timeout=1)
            if resp.status_code == 200 and resp.json()["origin"] != self.real_ip:
                print("test ip", url)
                print("real ip : ", resp.json()["origin"])
                self.m.add_to_db({"url": url})
        except ConnectionError as e:
            pass

    @timer
    def run(self):
        if self.china:
            data = open("china.txt").readlines()
        else:
            data = open("other.txt").readlines()
        urls = ["http://" + d.strip() for d in data]
        # 这里必须是100个，不然的话太慢了。
        with ThreadPoolExecutor(max_workers=100) as executor:
            future_tasks = [executor.submit(self.check_proxy, u) for u in urls]
            wait(future_tasks, return_when=ALL_COMPLETED)


if __name__ == '__main__':
    p = Proxy(china=True)
    p.run()





