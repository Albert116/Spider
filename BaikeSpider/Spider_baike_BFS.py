import re
import lxml
import time
import random
import requests
import traceback
import pymysql
from urllib import parse
from bs4 import BeautifulSoup

headers = {
    "User-agent": "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0",
}

class BaiKe:
    def __init__(self,start_url):
        self.base_url = start_url
        self.current_deepth = 1
        self.linkQueue = LinkQueue()
        self.linkQueue.addUnvisitedUrl(start_url)

    def getHtml(self,url):
        response = requests.post(url=url,headers=headers,timeout=60)
        if not response ==None:
            response.encoding = 'utf-8'
            return response.text
    
    def getHyperLinks(self,html):
        links = []
        soup = BeautifulSoup(html,features='lxml')
        href_list = soup.find_all("a", {"target": "_blank", "href": re.compile("/item/(%.{2})+/\d+$")})
        for i in href_list:
            links.append("https://baike.baidu.com"+i.get('href'))
        return links

    def parseItem(self,html):
        soup = BeautifulSoup(html,features='lxml')
        summary = soup.select('div.lemma-summary > div.para')
        if len(summary) == 0:
            return ""
        else:
            return summary[0].text.replace('\n','').replace('\'','\"')
    
    def Pipeline(self,key,summary,lemmaid):
        db = pymysql.connect("localhost","root","admin","baike",charset='utf8' ) 
        cursor = db.cursor()
        try:
            sql = "insert into DFS(`key`,`lemmaid`,`summary`) values('%s','%s','%s')"%(key,lemmaid,summary)
            cursor.execute(sql)
            db.commit()    
        except:
            print(traceback.format_exc())
        finally:
            db.close()

    def crawl(self,carwl_deepth):
        while(self.current_deepth <= carwl_deepth):
            print("当前爬取深度%d"%self.current_deepth)
            tempQueue = []
            while not self.linkQueue.UnvisitedUrlsEmpty():
                url_to_visit = self.linkQueue.UnvisitedUrlDeQueue()
                key = parse.unquote(url_to_visit[url_to_visit.find('item/')+5:url_to_visit.rfind('/')])
                lemmaid = url_to_visit[url_to_visit.rfind('/')+1:]
                html =  self.getHtml(url_to_visit)
                summary = self.parseItem(html)
                self.Pipeline(key,summary,lemmaid)
                html =  self.getHtml(url_to_visit)
                self.parseItem(html)
                for i in self.getHyperLinks(html):
                    tempQueue.append(i)
                self.linkQueue.addVisitedUrl(url_to_visit)
            self.linkQueue.Unvisited += tempQueue
            self.current_deepth += 1
                       
class LinkQueue:
    def __init__(self):
        self.visited = []
        self.Unvisited = []

    def getVisitedUrl(self):
        return self.visited

    def getUnvisitedUrl(self):
        return self.Unvisited

    def addVisitedUrl(self,url):
        self.visited.append(url)

    def addUnvisitedUrl(self,url):
       if url!="" and url not in self.visited \
                and url not in self.Unvisited:
            self.Unvisited.append(url)

    def removeVisitedUrl(self,url):
        self.visited.append(url)

    def UnvisitedUrlDeQueue(self):
        try:
            return self.Unvisited.pop(0)
        except:
            return None

    def getVisitedUrlCount(self):
        return len(self.visited)

    def getUnvisitedUrlCount(self):
        return len(self.Unvisited)

    def UnvisitedUrlsEmpty(self):
        return len(self.Unvisited)==0

if __name__ == "__main__":
    start_url = "https://baike.baidu.com/item/%E7%BD%91%E7%BB%9C%E7%88%AC%E8%99%AB/5162711"
    baike = BaiKe(start_url)
    baike.crawl(3)
    