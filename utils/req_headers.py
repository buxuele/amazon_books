import requests
from pprint import pprint
from utils.get_user_agent import get_a_ua

"""
格式化自己的 headers.  暴力就是有用！
1. 先从Network中复制headers 的全部内容， 保存为 headers.txt
2. 运行此文件，返回dict类型的headers
"""


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


if __name__ == '__main__':
    make_headers()
