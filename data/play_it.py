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



dic = {'ASIN': 'B01HZFHE1U',
 'X-Ray': '未启用',
 'author': 'W. Richard Stevens',
 'author_info': '',
 'book_about': '内容简介本书是被誉为UNIX编程“圣经”的Advanced Programming in the UNIX '
               'Environment一书的第3版。在本书第2版出版后的8年中，UNIX行业发生了巨大的变化，特别是影响UNIX编程接口的有关标准变化很大。本书在保持前一版风格的基础上，根据最新的标准对内容进行了修订和增补，反映了最新的技术发展。书中除了介绍UNIX文件和目录、标准I/O库、系统数据文件和信息、进程环境、进程控制、进程关系、信号、线程、线程控制、守护进程、各种I/O、进程间通信、网络IPC、伪终端等方面的内容，还在此基础上介绍了众多应用实例，包括如何创建数据库函数库以及如何与网络打印机通信等。此外，还在附录中给出了函数原型和部分习题的答案。本书内容权威，概念清晰，阐述精辟，对于所有层次UNIX/Linux程序员都是一本不可或缺的参考书。编辑推荐20多年来，严谨的C程序员都是依靠一本书来深入了解驱动UNIX和Linux内核的编程接口的实用知识的，这本书就是W. '
               'Richard Stevens所著的《UNIX高级环境编程》。现在，Stevens的同事Steve '
               'Rago彻底更新了这本经典著作。新的第3版支持当今领先的系统平台，反映了新技术进展和实践，并且符合最新的Single '
               'UNIX Specification第4版（SUSv4）。 '
               'Rago保留了使本书前版成为经典之作的精髓和方法。他在Stevens原著的基础上，从基础的文件、目录和进程讲起，并给诸如信号处理和终端I/O之类的先进技术保留较大的篇幅。他还深入讨论了线程和多线程编程、使用套接字接口驱动进程间通信（IPC）等方面的内容。 '
               '这一版涵盖了70多个最新版POSIX.1标准的新增接口，包括POSIX异步I/O、旋转锁、屏障（barrier）和POSIX信号量。此外，这一版删除了许多过时的接口，保留了一些广泛使用的接口。书中几乎所有实例都已经在目前最主流的4个平台上测试过，包括Solaris '
               '10、Mac OS X 10.6.8（Darwin 10.8.0）、FressBSD 8.0、Ubuntu '
               '12.04（基于Linux 3.2内核）。 与前两版一样，读者仍可以通过实例学习，这些实例包括了1万多行可下载的ISO '
               'C源代码，书中通过简明但完整的程序阐述了400多个系统调用和函数，清楚地说明它们的用法、参数和返回值。为了使读者能融会贯通，书中还提供了几个贯穿整章的案例，每个案例都根据现在的技术环境进行了全面更新。 '
               '本书帮助了几代程序员写出强大、高性能、可靠的代码。第3版根据当今主流系统进行更新，更具实用价值。名人推荐“本书第1版连同Stevens所著的系列网络技术书籍，被公认为优秀的、匠心独具的名著，成为极其畅销的作品……总之，这是一本弥足珍贵的经典著作的更新版。” '
               '——Dennis Ritchie，图灵奖得主，UNIX操作系统和C语言之父 '
               '“对任何一个严谨的、专业的UNIX系统程序员而言，本书都是不可或缺的权威参考书。Rago更新和扩展了Stevens的经典著作，并保持了原书的风貌。书中利用清晰的实例演示了API的使用过程，还提到了许多在不同UNIX系统实现上编程时需要注意的陷阱，并指出如何使用相关的标准（如POSIX '
               '1003.1 2004版和Single UNIX Specification第3版）来避免这些错误。” ——Andrew '
               'Josey， The Open Group标准部门主管，POSIX 1003.1标准工作组主席 '
               '“绝对的UNIX编程经典之一。” ——Eric S. Raymond，《UNIX编程艺术》作者 “Stephen '
               'Rago的更新版本对于使用众多UNIX及相关操作系统环境的广大专业用户来说是一个迟来的喜讯。这一版不仅删除了过时的接口，吸纳了较新的开发接口，还根据UNIX及类UNIX操作系统环境的几种主流实现发布的新版本全面更新了所有主题、实例和应用的背景。难能可贵的是，这一版本还保持了经典的第1版的风格和品位。” '
               '——Mukesh Kacker，Pronto Networks公司联合创始人和前任CTO '
               '“本书对于任何在UNIX系统上编写程序的开发人员来说都是非常重要的参考书。当我想要了解或者重新回顾各种系统接口时，这本书是首选的求助工具。Stephen '
               'Rago成功地修订了本书，使其与新的操作系统（如GNU/Linux和苹果的OS '
               'X）相容，并保持了第1版易读和实用的特质。它将永远摆放在我桌上随手可及的位置。” ——Benjamin '
               'Kuperman博士，斯沃斯莫尔学院媒体推荐“这是每一位严谨的UNIX '
               'C程序员必备的书籍。它深入、全面、清晰的解释是无可匹敌的。” ——UniForum Monthly “从W. Richard '
               'Stevens的这本书中可以找到更多易于理解的、详尽的UNIX系统内部细节。这本书包含了大量实际的例子，对系统编程工作非常有益。” '
               '——RS/Magazine作者简介作者介绍 W. Richard Stevens '
               '国际知名的UNIX和网络专家，备受赞誉的技术作家。生前著有多部经典的传世之作，包括《UNIX网络编程》（两卷本）、《TCP/IP详解》（三卷本）和本书第1版。 '
               'Stephen A. Rago '
               '资深UNIX程序员，目前任NEC美国实验室存储系统集团研究员。之前是贝尔实验室的UNIX系统V版本4的开发人员之一。著有《UNIX系统V网络编程》，并曾担任本书第1版的技术审校和第2版的共同作者。 '
               '译者介绍 戚正伟 '
               '博士，上海交通大学软件学院副教授，微软亚洲研究院（2008）和美国CMU大学（2011-2012）访问学者。研究方向为系统软件和程序分析，著有《New '
               'Blue Pill深入理解硬件虚拟机》和《嵌入式GIS开发及应用》等书。 张亚英 '
               '博士，同济大学电子与信息工程学院计算机系副教授，研究方向为分布与移动计算、嵌入式系统以及系统软件等。\u2003 尤晋元 '
               '上海交通大学计算机科学及工程系教授、博士生导师。在科研方面，主要从事操作系统和分布对象计算技术方面的研究。在教学方面，长期承担操作系统及分布计算等课程的教学工作。主编和翻译了多本操作系统教材和参考书，包括《UNIX操作系统教程》、《UNIX高级编程技术》、《UNIX环境高级编程》和《操作系统：设计与实现》等。',
 'book_image_url': 'https://images-cn.ssl-images-amazon.cn/images/I/51aGhOzwiGL._SY346_.jpg',
 'book_name': 'UNIX环境高级编程（第3版）（异步图书）',
 'book_url': 'https://www.amazon.cn/dp/B01HZFHE1U/ref=sr_1_127?dchild=1&qid=1613981559&s=digital-text&sr=1-127',
 'brand': '异步社区',
 'file_size': '75012 KB',
 'language': '简体中文',
 'pages': '812页',
 'price': '￥40.99',
 'publish_time': '2014年6月1日',
 'publisher': '人民邮电出版社; 第2版 (2016年7月5日)',
 'reading_helper': '未启用',
 'recommend_reason': '',
 'voice_status': '未启用'}


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




