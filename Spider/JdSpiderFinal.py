from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import pymongo
import pymysql
import time
import re
import traceback
from datetime import date

class jdSpider:
    driver=None
    def __init__(self,url):
        #driver配置
        firefox_options = Options()
        firefox_options.add_argument('--headless')
        firefox_options.add_argument('--disable-gpu')
        self.driver = webdriver.Firefox(firefox_options=firefox_options)
        #等待浏览器加载
        self.driver.implicitly_wait(3)
        self.driver.get(url)

    def scroll(self):
        #动态加载数据
        self.driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
        time.sleep(1)#等待数据加载
        soup=BeautifulSoup(self.driver.page_source,'html.parser')
        return soup

    def ParseItem(self,soup):
        #选择数据
        goods_info = soup.select('.gl-item')
        item = {}
        lt = []
        for info in goods_info:
            title = info.select('.p-name > a')[0].select('em')[0].text.strip()
            price = info.select('.p-price')[0].text.strip()
            comments = info.select('div.p-commit > strong')[0].select('a')[0].text.strip()
            url = info.select('.p-name')[0].select('a')[0]['href'].strip()
            #img = info.select('.p-img')[0].select('a > img')[0].attrs['src']
            tag_img = info.select('div.p-img')[0].select('a > img')[0]
            img = "https:"
            if tag_img['data-lazy-img']=='done':
                img += tag_img['src']
            else:
                img += tag_img['data-lazy-img']
            
            item = {"title":title,"price":price,"img":img,"comments":comments,"url":url} 
            #print(re.search('//img.*.jpg',aimg))
            lt.append(item)
        return lt
    def TurnToNextPage(self):
        self.driver.find_element_by_class_name('pn-next').click()
        self.driver.implicitly_wait(3)

    def Save2Mongo(self,lt):
        #持久化数据
        try:   
            client=pymongo.MongoClient('localhost',27017)
            db=client["SpiderMan"]
            col=db["jdmobile"]
            col.insert_many(lt)
        except:
            print("数据库连接错误！")
        finally:
            client.close()

    def Save2MySql(self,reslist):
        db = pymysql.connect("localhost","root","admin","django",charset='utf8' ) 
        cursor = db.cursor()
        sql = "select * from blog_category where name = \'JdMobile\'"
        try:
            cursor.execute(sql)
            results = len(cursor.fetchall())
            if results==0:
                cursor.execute('insert into blog_category(name) values(\'JdMobile\')')
            cursor.execute("select * from blog_tag where name = \'京东手机\'")
            results = len(cursor.fetchall())
            if results==0:
                cursor.execute('insert into blog_tag(name) values(\'京东手机\')')
            db.commit()
            body = ""
            for  item in reslist:
                body += '<div class="col-md-4"><div class="card mb-4 box-shadow"><img class="card-img-top" src=\"'+item['img']+'\"></img><div class="card-body"><i>'+str(item['price'])+'</i><p class="card-text" style="height:50px;overflow:hidden"><em><a href="'+item['url']+'\">'+item['title']+'</a></em></p><div class="d-flex justify-content-between align-items-center"><div class="btn-group"><button type="button" class="btn btn-sm btn-outline-secondary">View</button><button type="button" class="btn btn-sm btn-outline-secondary">Edit</button></div><small class="text-muted">'+str(item['comments'])+'条评价</small></div></div></div></div>'
            body = '<div class="container col-md-12"><div class="row" style="font-size:14px;">'+body+'</div></div>'
            time = date.today().strftime('%Y-%m-%d %H:%M:%S')            
            cursor.execute('insert into blog_post(title,body,created_time,modified_time,excerpt,author_id,category_id,views) values (\'Selenium爬取京东手机商品列表\',\'{0}\',\'{1}\',\'{2}\',\'{3}\',{4},{5},0)'.format(body,time,time,'京东手机商品列表',1,8))
            db.commit()    
        except:
            s=traceback.format_exc()
            print(s)
            db.rollback()
            print ("Error: unable to fetch data")
        finally:
            db.close()

if __name__ == "__main__":
    url = "https://search.jd.com/Search?keyword=%E6%89%8B%E6%9C%BA&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=%E6%89%8B%E6%9C%BA&cid2=653&cid3=655&page=1&s=1&click=0"
    goodsList=[]
    jd = jdSpider(url)
    goodsList += jd.ParseItem(jd.scroll())
    for i in range(0,2):
        jd.TurnToNextPage()
        goodsList += jd.ParseItem(jd.scroll())
    #jd.Save2Mongo(goodsList)
    
    
    jd.Save2MySql(goodsList)
    #关闭浏览器
    print("--end of the spider")
    jd.driver.close()