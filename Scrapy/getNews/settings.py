# -*- coding: utf-8 -*-

# Scrapy settings for getNews project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'getNews'

SPIDER_MODULES = ['getNews.spiders']
#NEWSPIDER_MODULE = 'getNews.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2 '

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 1.5
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'getNews.middlewares.GetnewsSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.orgi/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'getNews.middlewares.GetnewsDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'getNews.pipelines.GetnewsPipeline': 300,
    #支持将数据存储到redis数据库中
    'scrapy_redis.pipelines.RedisPipeline': 400,
}
# MONGODB 主机名
MONGO_HOST = "127.0.0.1"
# MONGODB 端口号
MONGO_PORT = 27017
# 数据库名称
MONGO_DBNAME = "spider"
# 存放数据的表名称
MONGO_COLL_NEWS = "news"
MONGO_COLL_RULES = "rules"

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

#CLOSESPIDER_TIMEOUT=30
#CLOSESPIDER_TIMEOUT = 86400   # 24小时*3600秒 = 86400
DOWNLOADER_MIDDLEWARES = {
    'getNews.middlewares.getNewsUserAgentMiddleware' :400
}

#SPIDER_MIDDLEWARES = {
#'scrapy.spidermiddlewares.offsite.OffsiteMiddleware': None,
#}


from datetime import datetime
today = datetime.now()
# log_file_path = "{}-{}-{} {}:{}:{}.log".format(today.year, today.month, today.day,today.hour,today.minute,today.second)
log_file_path="news.log"
LOG_LEVEL="DEBUG"
LOG_ENABLED="True"
LOG_FILE =log_file_path

#Redis组件(去重和调度器组件)
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
#持久化数据
SCHEDULER_PERSIST = True
#REDIS_URL = 'reds://127.0.0.1:6379'
#REDIS_HOST="远程ip"
#REDIS_PORT=6379
REDIS_HOST = '127.0.0.1'  # redis设置
REDIS_PORT = 6379

REDIS_PARAMS = {'db': 0}
#默认的队列形式
#SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderPriorityQueue"
#SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderQueue"
#SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderStack"


'''
#IP代理池
IPPOOL = [
{"ipaddr": "119.101.116.6:9999"},
{"ipaddr": "119.101.117.76:9999"},
{"ipaddr": "119.101.116.127:9999"},
{"ipaddr": "119.101.115.87:9999"},
]

'''