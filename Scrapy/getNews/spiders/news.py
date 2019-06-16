# -*- coding: utf-8 -*-

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
from scrapy_redis.spiders import RedisCrawlSpider
from getNews.items import GetnewsItem
from scrapy.utils.log import configure_logging

class NewsSpider(RedisCrawlSpider):
    #name = "news"
    def __init__(self,rule):
        self.name=rule["name"]
        self.rule=rule
        self.allowed_domains = [rule["allowed_domains"]]
        #self.start_urls = [rule["start_urls"]]
        self.redis_key = "NewsSpider:start_urls"

        rule_list = []
        rule_list.append(Rule(LinkExtractor(allow=rule["rule"]),
             callback='parse_item', follow=True,))
        self.rules = tuple(rule_list)
        super(NewsSpider, self).__init__()
        configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})


    def parse_item(self, response):
        i = GetnewsItem()
        i['title'] = self.getTitle(response)
        i['keywd'] = self.getKeywd(response)
        i["link"] = response.url
        i['content'] =self.getContent(response)
        if i['content'] is not None:
            yield i
        else:
            pass

        #return i

    def getTitle(self,response):
        title = response.xpath(self.rule["title"]).extract()
        if len(title):
            title=title[0]
        else:
            title = ""
        return title.strip()

    def getKeywd(self, response):
        keytemp = response.xpath(self.rule["keywd"]).extract()
        if len(keytemp):
            keytemp=keytemp[0]
        else:
            keytemp = ""
        keytemp = keytemp.replace(',腾讯新闻', '')
        keytemp = keytemp.replace(',腾讯网','')
        return  keytemp.strip()

    def getContent(self, response):
        content_list = response.xpath(self.rule["content"])
        # 合并p的文本内容,xpath-->string(.)获取子节点文本内容
        content_list = content_list.xpath("string()").extract()
        if len(content_list)>0:
            for index in range(len(content_list)):
                content_list[index] = content_list[index].strip()
            content_list_str = "\n".join(content_list)
            return content_list_str
        else:
            pass

