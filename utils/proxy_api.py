import time
import requests
from utils.my_timer import timer
from utils.get_user_agent import get_a_ua
from utils.mongoDB import Mongo
import config                               # 根目录 数据库名称。
from pprint import pprint
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED


class SmallProxy:
    def __init__(self, china=True):
        self.country = china
        self.m = Mongo(config.proxy_db, config.proxy_coll)
        self.url = "https://ip.jiangxianli.com/api/proxy_ips"
        self.headers = {'User-Agent': get_a_ua()}
        self.real_ip = self.find_myself()

    @staticmethod
    def find_myself():
        target = 'http://httpbin.org/ip'
        resp = requests.get(target)
        return resp.json()["origin"]

    # 获取更多的代理。这一部分写的很漂亮啊。自己写的就是很得意。
    def make_payloads(self):
        nations = ["俄罗斯", "美国", "加拿大", "日本", "德国", "香港", "印度尼西亚", "法国"]
        if self.country:
            pay = [{"page": c, "country": "中国", "order_by": "speed"} for c in range(1, 5)]
        else:
            pay = [{"page": 1, "country": b, "order_by": "speed"} for b in nations]
        return pay

    def greet(self, pay):
        resp = requests.get(self.url, params=pay, headers=self.headers)
        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"Sorry! 这个代理网站有问题!")
            return None

    @timer
    def get_all_proxy(self):
        temp = []
        for k in self.make_payloads():
            d = self.greet(k)    # d  <dict>
            if d:
                all_data = d["data"]["data"]
                for t in all_data:
                    # if t["anonymity"] == 2:       # 按匿名度来排除。
                    a = t["protocol"] + "://" + t["ip"] + ":" + t["port"]
                    temp.append(a)
        print(temp)
        print(len(temp))
        return temp

    def speed_status(self, proxy=None):
        url = "http://httpbin.org/ip"
        resp = requests.get(url, proxies={"http": proxy}, timeout=1)
        # 只有当前使用的代理与自己真实的ip 不相等的时候，才说明这个代理是有效的。
        if resp.status_code == 200 and resp.json()["origin"] != self.real_ip:
            print("test ip", proxy)
            print("real ip : ", resp.json()["origin"])
            self.m.add_to_db({"url": proxy})

    @timer
    def run(self):
        fake_proxy = self.get_all_proxy()
        # 这里设置为20就很合适了，太多反而不利。
        with ThreadPoolExecutor(max_workers=16) as executor:
            future_tasks = [executor.submit(self.speed_status, p) for p in fake_proxy]
            wait(future_tasks, return_when=ALL_COMPLETED)

    def show_product(self):
        self.m.get_unique(show=True)


if __name__ == '__main__':
    p = SmallProxy(china=True)
    # p.main()
    p.run()
    time.sleep(.1)
    p.show_product()








