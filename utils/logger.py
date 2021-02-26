import os
import logging
import time
import sys


""" 调用:
from utils.logger import logger
logger(stuff)
"""


def chinese_time():
    # print(datetime.now())       # 2020-12-31 19:40:58.431721
    pretty_time = time.strftime("%Y-%m-%d--%H-%M-%S")
    print(pretty_time)            # 2020-12-31 19:40:58
    return pretty_time


def logger(msg):
    # os.chdir(os.getcwd())   # 在文件运行的直接路径下新建一个 .log 文件。
    t = chinese_time()
    # fn = os.path.basename(__file__).replace(".", "_") + '_' + t + ".log"

    # 从别处调用的话，那么 log 文件的名称就是调用者的名字。
    # https://blog.csdn.net/iamcodingmylife/article/details/79866600
    fn = str(sys.argv[0]).replace(".", "_") + '_' + t + ".log"
    logging.basicConfig(filename=fn,
                        level=logging.DEBUG,
                        format=f'%(levelname)s:%(message)s')
    logging.info(f"start logging on: {chinese_time()} ")
    logging.warning(msg)


if __name__ == '__main__':
    logger("hahhah")



