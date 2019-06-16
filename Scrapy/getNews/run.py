import sys
import os
import redis
import logging
import pymongo
BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from getNews.spiders.news import NewsSpider
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings


if __name__ == '__main__':
    #连接数据库
    settings = get_project_settings()
    try:
        client = pymongo.MongoClient(host=settings['MONGO_HOST'], port=settings['MONGO_PORT'])
        # 数据库登录需要帐号密码的话
        # self.client.admin.authenticate(settings['MINGO_USER'], settings['MONGO_PSW'])
        db = client[settings['MONGO_DBNAME']]  # 获得数据库的句柄
        coll = db[settings['MONGO_COLL_RULES']]  # 获得collection的句柄
    except:
        print("数据库链接错误！退出程序！")
        exit(0)

    rules=coll.find({"enable":1});
    runner = CrawlerRunner(settings)
    client.close()
    temp=1
    for rule in rules:
        # stop reactor when spider closes
        # runner.signals.connect(spider_closing, signal=signals.spider_closed)
        #typeof(rule)dict
        runner.crawl(NewsSpider, rule=rule)


        # 连接上master的redis
        r = redis.StrictRedis(host='127.0.0.1', port=6379)
        # r.delete('NewsSpider:start_urls')
        # 循环添加
        # result为lpush添加的结果，返回0或1。0为不成功，1为成功
        # for url in rule['start_urls']:
        result = r.lpush('NewsSpider:start_urls', rule['start_urls'])
        # print(r.smembers('NewsSpider:start_urls'))
        if result is temp:
            print('{0:}加入成功'.format(rule['start_urls']))
            temp += 1
    d = runner.join()
    d.addBoth(lambda _: reactor.stop())

    # blocks process so always keep as the last statement
    reactor.run()



    logging.info('all finished.')