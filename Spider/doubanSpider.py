import requests
import pymongo
from lxml import html
import sqlite3
from datetime import date
import traceback
import pymysql

#https://zhuanlan.zhihu.com/p/26304106


class SpiderMan:
    def __init__(self, version):
        self.version = version
        self.result = []

    def get_page(self, start_num):
        url = 'https://movie.douban.com/top250?start=%s&filter=' % start_num
        res = requests.get(url).content
        text = html.fromstring(res)
        return text


    def parseItem(self,content):
        item = {}
        lt=[]
        for i in content.xpath('//div[@class="info"]'):
            title = i.xpath('div[@class="hd"]/a/span[@class="title"]/text()')[0]
            info = i.xpath('div[@class="bd"]/p[1]/text()')
            date = info[1].replace(" ", "").replace("\n", "").split("/")[0].strip()
            country = info[1].replace("\n", "").split("/")[1].strip()
            geners = info[1].replace("\n", "").split("/")[2].strip() 
            rate = i.xpath('//span[@class="rating_num"]/text()')[0].strip()  
            item = {"title":title,"date":date,"country":country,"geners":geners,"rate":rate}
            lt.append(item)
        return lt
            
    def Output2Text(self,res):
        f=open("E:\\rs.txt",'w+',encoding='utf-8')
        for i in res:
            f.write(i+'\n')
        f.close()


    def Con2Mongo(self,reslist):
        try:   
            client=pymongo.MongoClient('localhost',27017)
            db=client["SpiderMan"]
            col=db["douban"]

            col.insert_many(reslist)
            client.close()
        except:
            print("数据库连接错误！")

    def Con2Sqlite3(self,reslist):
        try:
            conn = sqlite3.connect('db.sqlite3')
            cur = conn.execute('select * from blog_category where name = \'doubanTop250\'')
            len_Rs = len(cur.fetchall())
            if(len_Rs==0):
                cur = conn.cursor()
                cur.execute('insert into blog_category(name) values(\'doubanTop250\')')
            cur = conn.execute('select * from blog_tag where name = \'电影\'')
            len_Rs = len(cur.fetchall())
            if(len_Rs==0):
                conn.execute('insert into blog_tag(name) values(\'电影\')')
            body = ""
            for  item in reslist:
                body += item['title']+'\n'+item['date']+'/'+item['country']+'/'+item['geners']+'\n'+item['rate']+'\n'
                #print(body)


            time = date.today().strftime('%Y-%m-%d %H:%M:%S')
            #print('insert into blog_post(title,body,create_time,modified_time,excerpt,author_id,category_id,views) values (\'豆瓣电影 Top 250\',\'{0}\',{1},{2},\'{3}\',{4},{5},0)'.format(body,datetime.datetime.now(),datetime.datetime.now(),'豆瓣电影排行榜',2,5))
            conn.execute('insert into blog_post(title,body,created_time,modified_time,excerpt,author_id,category_id,views) values (\'豆瓣电影 Top 250\',\'{0}\',\'{1}\',\'{2}\',\'{3}\',{4},{5},0)'.format(body,time,time,'豆瓣电影排行榜',2,5))    
            conn.commit()
        except:
            s=traceback.format_exc()
            #print("连接sqlite3数据库错误")
        finally:
            conn.close()
        
    def Con2MySql(self,reslist):
        db = pymysql.connect("localhost","root","admin","django",charset='utf8' ) 
        cursor = db.cursor()
        sql = "select * from blog_category where name = \'doubanTop250\'"
        try:
            cursor.execute(sql)
            results = len(cursor.fetchall())
            if results==0:
                cursor.execute('insert into blog_category(name) values(\'doubanTop250\')')
            cursor.execute("select * from blog_tag where name = \'电影\'")
            results = len(cursor.fetchall())
            if results==0:
                cursor.execute('insert into blog_tag(name) values(\'电影\')')
            body = ""
            count = 0
            for  item in reslist:
                count += 1
                body += '<blockquote><p>TOP'+str(count)+': '+item['title']+'</p><p>'+item['date']+'/'+item['country']+'/'+item['geners']+'</p><p>'+item['rate']+'</p></blockquote>'
            time = date.today().strftime('%Y-%m-%d %H:%M:%S')            
            cursor.execute('insert into blog_post(title,body,created_time,modified_time,excerpt,author_id,category_id,views) values (\'豆瓣电影 Top 250\',\'{0}\',\'{1}\',\'{2}\',\'{3}\',{4},{5},0)'.format(body,time,time,'豆瓣电影排行榜',1,4))
            db.commit()    
        except:
            
            s=traceback.format_exc()
            print(s)
            db.rollback()
            print ("Error: unable to fetch data")
        finally:
            db.close()

if __name__ == "__main__":
    print('crawling douban Top250'+'\n')
    my_spider = SpiderMan('1.0')
    top250 = []
    for i in range(0, 10):        
        text = my_spider.get_page(i*25)
        top250 += my_spider.parseItem(text)
        print("正在爬取第%d页"%(i))
    #my_spider.Con2Mongo(top250)
    my_spider.Con2MySql(top250)
    print('--end of the spider--')