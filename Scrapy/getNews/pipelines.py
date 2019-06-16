# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
'''
import codecs

class GetnewsPipeline(object):

    def __init__(self):
        self.file = codecs.open("C:/Users/Albert/getNews/sinanews.txt", "wb", encoding="utf-8")

    def process_item(self, item, spider):
        # 拼接字符组成  标题:**** 链接:****
        line = "标题:%s 链接:%s\n" % (item["name"][0], item["link"])
        self.file.write(line)

    def close_spider(self):
        self.file.close()


import pymysql

class GetnewsPipeline(object):
    def __init__(self):
        # 连接数据库
        # spider数据库中 只有一个表为mydb，表中有两个字段title和keywd和link
        self.conn = pymysql.connect(host="127.0.0.1", user="root", passwd="123", db="spider",use_unicode=True, charset="utf8")

    def process_item(self, item, spider):
        # 将获取到的title和keywd分别赋给变量title和变量keywd
        title = item["title"][0]
        #print(title+"\n")
        link = item["link"][0]
        # 可能存在没有关键词的情况 如果直接填入item["keywd"][0]可能会出现数组溢出的情况
        if item["keywd"]:
            keywd = item["keywd"][0]
        else:
            keywd = ""
        #print(keywd)
        # 构造对应的sql语句
        sql = "insert into mydb(title, keywd,link) values('" + title + "','" + keywd + "','" + link + "')"

        # 通过query实现执行对应的sql语句
        try:
            self.conn.query(sql)
            # 提交
            self.conn.commit()


        except Exception as error:
            # 出现错误时打印错误日志
            print(error)
        return item
    def close_spider(self):
        # 关闭数据库连接
        self.conn.close()
'''
import pymongo
from scrapy.utils.project import get_project_settings

class GetnewsPipeline(object):
    def __init__(self):
        # 链接数据库
        settings = get_project_settings()
        try:
            self.client = pymongo.MongoClient(host=settings['MONGO_HOST'], port=settings['MONGO_PORT'])
            # 数据库登录需要帐号密码的话
            # self.client.admin.authenticate(settings['MINGO_USER'], settings['MONGO_PSW'])
            self.db = self.client[settings['MONGO_DBNAME']]  # 获得数据库的句柄
            self.coll = self.db[settings['MONGO_COLL_NEWS']]  # 获得collection的句柄
        except:
            print("数据库链接错误！")

    def process_item(self, item, spider):
        postItem = dict(item)  # 把item转化成字典形式
        self.coll.insert(postItem)  # 向数据库插入一条记录
        self.client.close()
        #return item  # 会在控制台输出原item数据，可以选择不写