import os
import requests
import urllib3
from PIL import Image
from requests_toolbelt import MultipartEncoder
import random
import time
import string
from bs4 import BeautifulSoup


from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

from utils.data_loader import LocalSimpleCache
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Upgrade-Insecure-Requests": "1",
    }

req = requests.session()
cookies = []



class check_captcha(object):

    def get_fingerprint(self,driver):
        return driver.current_url == "https://kyfw.12306.cn/otn/resources/login.html"

    def set_cookie5(self):
        dict_temp = {}
        #("由于12306采取用设备指纹来校验访问, 现使用selenium获取完整cookie")
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        options.add_argument("--incognito")
        options.add_argument("--disable-databases")
        options.add_argument("--disable-gpu-compositing")
        options.add_argument("--disable-application-cache")
        driver = webdriver.Firefox(options=options)
        driver.implicitly_wait(15)
        # first clear selenium cache
        driver.get("https://kyfw.12306.cn")
        wait = WebDriverWait(driver, 10)
        wait.until(self.get_fingerprint)
        cookies = driver.get_cookies()
        if "RAIL_DEVICEID" not in [v["name"] for v in cookies] \
                or "RAIL_EXPIRATION" not in [v["name"] for v in cookies]:
            print("设备指纹未获取到,正在重试")
            self.set_cookie5()
            return
        driver.quit()
        for v in cookies:
            if v['name'] == "RAIL_DEVICEID":
                deviceId = v["value"]
            if v['name'] == "RAIL_EXPIRATION":
                exp = v["value"]
        req.cookies.update({
            "RAIL_DEVICEID":deviceId,
            "RAIL_EXPIRATION":exp,
            "hibext_instdsigdipv2":"1",
        })

    def set_cookie4(self):
        req.cookies.update({
            # "RAIL_EXPIRATION":"1560271645947",
            "RAIL_EXPIRATION":str(round(time.time()*1000)),
            #"RAIL_DEVICEID":"SLcY_VSGi3CWsaygNUfhuCeWRmQImct6RXs0oID_CImzitqn5oxGAPUXl94VOnkfTfTYBPsI_bwaTkz_X4ADMlJ-aZmA0gOJfDlLXrUxBrXQoFAsFIoDg9Sb4TvudgAXpl_hgLfX8lIOae9vXSb5WYQcqORfe4a8",
            # "hibext_instdsigdipv2":"1",
            "RAIL_DEVICEID":"mGMQh8uPUxCgbaRKxVyEj3AXt4qHu_RupqnHT-4cldNaHfZz2gPFrimLe7Wc2eD-03atsDleAfzU8ZCJBqu0ZJ0Rms7oeTRK8OmOWvYE7jv4zwtromREbWzo9i74x3CIxIcLARcAjuNldLI_M0VTn-hhPQ4OIXmy",
            "_jc_save_fromStation":"%u6E29%u5DDE%u5357%2CVRH",
            "_jc_save_toStation":"%u676D%u5DDE%u4E1C%2CHGH",
            "_jc_save_wfdc_flag":"dc",
        })
        
    def set_cookie3(self):
        req.cookies.update({
            "JSESSIONID":"CD26079B57A893FA5B0140DECA104329",
            "tk":"WRKYXZ17ab5LuHjYD7zFsP8UX7ZS7CcZHub8HZ1FyUAnx1110",
            "_jc_save_fromStation":"%u6E29%u5DDE%u5357%2CVRH",
            "_jc_save_toStation":"%u676D%u5DDE%u4E1C%2CHGH",
            "_jc_save_wfdc_flag":"dc",
            "RAIL_EXPIRATION":"1560271645947",
            "RAIL_DEVICEID":"SLcY_VSGi3CWsaygNUfhuCeWRmQImct6RXs0oID_CImzitqn5oxGAPUXl94VOnkfTfTYBPsI_bwaTkz_X4ADMlJ-aZmA0gOJfDlLXrUxBrXQoFAsFIoDg9Sb4TvudgAXpl_hgLfX8lIOae9vXSb5WYQcqORfe4a8",
            "_jc_save_fromDate":"2019-06-10",
            "BIGipServerpool_passport":"334299658.50215.0000",
            "route":"c5c62a339e7744272a54643b3be5bf64",
            "BIGipServerpassport":"988283146.50215.0000",
            "BIGipServerotn":"2162688266.64545.0000",
            "searchHistory":"%5B%7B%22innerText%22%3A%22%u6E29%u5DDE%22%7D%5D",
        })
        
    def set_cookie2(self):
        s = LocalSimpleCache([], "device_pickle.pickle", expire_time=24)
        load = s.get_final_data()
        dict_temp = {}
        # print(load.raw_data)
        if not load.raw_data:
            #("由于12306采取用设备指纹来校验访问, 现使用selenium获取完整cookie")
            options = webdriver.FirefoxOptions()
            options.add_argument('--headless')
            options.add_argument("--incognito")
            options.add_argument("--disable-databases")
            options.add_argument("--disable-gpu-compositing")
            options.add_argument("--disable-application-cache")
            driver = webdriver.Firefox(options=options)
            driver.implicitly_wait(15)
            # first clear selenium cache
            driver.get("https://kyfw.12306.cn")
            wait = WebDriverWait(driver, 10)
            wait.until(self.get_fingerprint)
            cookies = driver.get_cookies()
            if "RAIL_DEVICEID" not in [v["name"] for v in cookies] \
                    or "RAIL_EXPIRATION" not in [v["name"] for v in cookies]:
                print("设备指纹未获取到,正在重试")
                self.set_cookie2()
            driver.quit()
            # print(cookies)
            s.raw_data = [v for v in cookies]
            s.export_pickle()
        else:
            print("使用缓存过的cookie")
            cookies = load.raw_data
            print(cookies)
        for v in cookies:
            v.pop('httpOnly', None)
            v.pop('expiry', None)
            dic = {v['name']:v['value']}
            dict_temp={**dic,**dict_temp}
        req.cookies.update(dict_temp)

    def set_cookie(self):
        #("由于12306采取用设备指纹来校验访问, 现使用selenium获取完整cookie")
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        options.add_argument("--incognito")
        options.add_argument("--disable-databases")
        options.add_argument("--disable-gpu-compositing")
        options.add_argument("--disable-application-cache")
        driver = webdriver.Firefox(options=options)
        driver.implicitly_wait(15)
        # first clear selenium cache
        driver.get("https://kyfw.12306.cn")
        wait = WebDriverWait(driver, 10)
        wait.until(self.get_fingerprint)
        wait = WebDriverWait(driver, 10)
        cookies = driver.get_cookies()
        dict_temp = {}
        if "RAIL_DEVICEID" not in [v["name"] for v in cookies] \
                or "RAIL_EXPIRATION" not in [v["name"] for v in cookies]:
            print("设备指纹未获取到")
            return
        for v in cookies:
            dic = {v['name']:v['value']}
            dict_temp={**dic,**dict_temp}
        req.cookies.update(dict_temp)
        driver.quit()
        s.raw_data = [v for v in cookies]

    def __init__(self, parent_file_url, http_url):
        self.image_code = parent_file_url + "/code.png"
        # 删除文件
        self.__del_file__(parent_file_url)
        # 下载图片
        self.__get_picture__(http_url, self.image_code)
        self.set_cookie4()

    def __get_picture__(self, get_pic_url, img_code):
        """
        下载图片放入指定位置
        :param get_pic_url:
        :param img_code:
        :return:
        """
        response = req.get(get_pic_url, headers=headers, verify=False)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            with open(img_code, "wb") as f:
                f.write(response.content)
                print("验证码图片下载成功")
                return True
        else:
            print("图片下载失败，正在重试....")
            self.__get_picture__(get_pic_url, img_code)

    def __del_file__(self, path):
        for i in os.listdir(path):
            # 取文件绝对路径
            path_file = os.path.join(path, i)
            if os.path.isfile(path_file):
                os.remove(path_file)
            else:
                self.__del_file__(path_file)

    def check(self,point):
        # 验证码地址
        check_url = "https://kyfw.12306.cn/passport/captcha/captcha-check"
        data = {
            "answer": ",".join(point),
            "login_site": "E",
            "rand": "sjrand"
        }
        # print(分析js文件)
        response = req.post(check_url, data=data,
                            headers=headers, verify=False)
        # print(response.text)
        if response.status_code != 200:
            return (False, req)
        code = response.json()['result_code']
        # 取出验证结果，4：成功  5：验证失败  7：过期
        if str(code) == '4':
            print('验证码校验成功')
            return (True, req)
        else:
            print('验证码校验失败')
            return (False, req)

    def get_key(self):
        headers2 = {"Content-type" : "multipart/form-data",'Content-Type': 'image/jpeg','Referer': 'http://littlebigluo.qicp.net:47720/','Content-Type': 'multipart/form-data;boundary=----WebKitFormBoundary9MMCBHAWppoMw6p8','Pragma': 'no-cache','Cache-Control': 'no-cache','Upgrade-Insecure-Requests': '1','Accept': ': text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3','DNT': '1'}
        headersNew = {**headers, **headers2}
        url = "http://littlebigluo.qicp.net:47720/"
        m = MultipartEncoder(
            fields={'pic_xxfile':('code.png',open('./images/code.png','rb'),'image/png')},
            boundary='----'+'WebKitFormBoundary9MMCBHAWppoMw6p8'
        )
        key_list = ()
        res = requests.post(url, headers=headersNew, data=m)
        #print(res.text)
        soup = BeautifulSoup(res.text,'lxml')
        tag = soup.b
        if tag == None:
            print("抱歉!验证码系统访问过于频繁，请稍后再试！！")
            return key_list
        key_list = tag.string.split(" ")
        if len(key_list[0]) > 1:
            print("不好意思，您这图片好难，木有认出来...")
            return key_list
        print("验证码答案为",end=':')
        for i in key_list:
           print(i,end=',')
        return key_list

    def auth_uamtk(self):
        """
        根据登录返回的umatk,得到newapptk
        :return:
        """
        print("验证是否登录，得到newapptk")
        data = {
            "appid": "otn"
        }
        url = "https://kyfw.12306.cn/passport/web/auth/uamtk"
        response = req.post(url, data=data, headers=headers)
        print(response.text)
        newapptk_id = response.json()['newapptk']
        return newapptk_id

    def getPointManually(self):
        img = Image.open(self.image_code)
        img.show()
        # 坐标点
        yanSol = ['35,35', '105,35', '175,35', '245,35', '35,105', '105,105', '175,105', '245,105']
        # 输入坐标点获取到最表0-7,逗号分隔
        te = input("请输入坐标序号,逗号分隔(1-8)\n")
        index = te.split(",")
        point = list()
        for x in index:
            point.append(yanSol[int(x)-1])
        return point
        