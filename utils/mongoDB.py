import datetime
from pymongo import MongoClient
from pprint import pprint


# todo 重写这部分。方法命名之间太繁杂了。
class Mongo:
    def __init__(self, db, collections):
        self.client = MongoClient('localhost', 27017)

        # 这里需要检查一下给出的2个名称是否已经存在了，
        # 如果存在同名的，就删除，然后重建。是不是有点暴力啊。？？？ todo
        # 还算太危险了， 误伤的几率比较高。
        # 如果已经存在的话，那么就警告一下。这样比较好。
        self.db = self.client[db]
        self.coll = self.db[collections]

    @staticmethod
    def read_raw_data():
        good = []
        urls = [{"url": u.rstrip()} for u in good]
        return urls

    def add_to_db(self, data):
        self.coll.insert_one(data)

    def insert_temp_data(self):
        data = self.read_raw_data()
        self.coll.insert_many(data)

    def insert_bulk_data(self, list_data):
        self.coll.insert_many([{"url": u} for u in list_data])

    def get_data(self):
        return self.coll.find()

    def show_data(self):
        # for x in self.coll.find():
        #     pprint(x)
        #     if "brand" not in x.keys():
        #         self.coll.delete_one(x)

        print("all data is: ", self.coll.count_documents({}))

    # check_repeat
    # get_unique
    # 这里写的简直就是狗屎一样。
    def check_repeat(self):
        unique = set()
        shit = set()
        for x in self.coll.find():
            if x["url"] not in unique:
                unique.add(x["url"])
            else:
                shit.add(x["url"])
        print("以下内容有重复！ 个数: ", len(shit))
        return shit

    def get_unique(self, show=False):
        unique = []
        for x in self.coll.find():
            if x["url"] not in unique:
                unique.append(x["url"])

        if show:
            pprint(unique)
        print("这批数据唯一的个数是： ", len(unique))
        return unique

    def show_db(self):
        # 正确 显示数据库名称，与数据集合的名称.这里也可以逐个检测每个数据集的大小。用于筛选。
        db = self.client.list_database_names()
        print(db)
        print()

        for d in db:
            c = self.client[d].list_collection_names()
            print(d, "--->", c)

        # 删除一个  数据库
        # self.client.drop_database("db_name")


if __name__ == '__main__':
    # m = Mongo("amazon_books", "computer_book_urls")       # 6398
    # m = Mongo("amazon_books", "books_info_9")             # 2914 这里的数据差的太多了。
    m = Mongo("amazon_books", "books_info_10")

    m.show_data()




