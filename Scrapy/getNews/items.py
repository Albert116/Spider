# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GetnewsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 建立name存储网页标题
    title = scrapy.Field()
    # 建立keywd存储网页关键词
    keywd = scrapy.Field()
    # 建立keywd存储网页链接
    link = scrapy.Field()
    # 建立content存储网页内容
    content = scrapy.Field()

