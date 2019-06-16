#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#coding=utf-8
import configparser
import datetime
import re
import time
from urllib import parse

import requests
import urllib3
import json
from random import randint

from login_api import check_captcha
from query_train import queryTrain
import traceback

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


"""
 12306登录接口，获取到了验证码标题的内容。
"""
headers = {
    "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://kyfw.12306.cn",
    }


# cookies信息
cookies = ""
# 登陆返回的第一个uuid
login_id = ""
# auth_uamtk根据login_Id得到的新tk_id
newapptk_id = ""
# check_uamauthclient 检查客户端登陆返回i
apptk_id = ""

# 加载现有配置文件
conf = configparser.ConfigParser()
conf.read("./conf/conf.ini", encoding="utf-8-sig")
# 登陆信息
username = conf.getint('user_info', 'username')
password = conf.get('user_info', 'password')

# 乘客信息
passengerTicketStr = conf.get('passenger_info', 'passengerTicketStr')
oldPassengerStr = conf.get('passenger_info', 'oldPassengerStr')

# 开启循环购票，一直查询余票，有票就购买
isAutoBuy = conf.get('buy_trcket_info', 'isAutoBuy')

# 车票信息
from_station = conf.get('ticket_info', 'from_station')
to_station = conf.get('ticket_info', 'to_station')
date = conf.get('ticket_info', 'date')



req = ""


def login(point):
    """
    12306登陆接口
    :return:
    """
    headers1 = { 
        "Referer": "https://kyfw.12306.cn/otn/resources/login.html",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }   

    headers2 = {**headers,**headers1}
    loginUrl = "https://kyfw.12306.cn/passport/web/login"
    data = {
        'username': username,
        'password': password,
        'appid': 'otn',
        "answer": ",".join(point),
    }
    result = req.post(url=loginUrl, data=data, headers=headers2,verify=False)
    print("登录返回结果:")
    try:
        res = result.json()
    except Exception:
        print("网络繁忙")
        return False
    #cookies = result.headers['set-cookie']
    te = res["result_message"]
    if te == "登录成功":
        login_id = res["uamtk"]
        print("登录成功！")
        return True
    else:
        return False
    

def auth_uamtk():
    """
    根据登录返回的umatk,得到newapptk
    :return:
    """
    print("验证是否登录，得到newapptk")
    data = {
        "appid": "otn"
    }
    url = "https://kyfw.12306.cn/passport/web/auth/uamtk"
    response = req.post(url, data=data, headers=headers, cookies=cookies,timeout=25)
    print(response.text)
    newapptk_id = response.json()['newapptk']
    return newapptk_id

def check_uamauthclient(tk):
    """
    检查客户端是否登录
    :param tk:
    :return:
    """
    print("检查unamuth客户端")
    url = "https://kyfw.12306.cn/otn/uamauthclient"
    data = {
        "tk": tk,
        "_json_att": ""
    }
    resp = req.post(url, data=data, headers=headers)
    # 反回一个验证通过信息
    if resp.status_code == requests.codes.ok:
        # 成功,返回这种类型数据
        # {
        # apptk:"1eB7-ZqCXawUvOSEwc3xshNWaDF7R_mWtOrh1gBrcusoz1210"
        # result_code:0
        # result_message:"验证通过"
        # username:""
        # }
        print(resp.text)
        """
            会存在失败的情况，网络原因，转json将会失败
        """
        te = resp.json()
        if te["result_message"] == "验证通过":
            print("用户名：", te['username'])
            apptk_id = te['apptk']


def get_user_info():
    print("获取用户信息")
    """
    获取用户信息
    :return:
    """
    url_info = "https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs"
    data = {
        "_json_att": "",
        "REPEAT_SUBMIT_TOKEN": newapptk_id
    }
    response = req.post(url_info, data=data, headers=headers, cookies=cookies)
    # print(response.text)


def initDc():
    """
    在进行点击了预定，初始化订票页面
    :return:
    """
    print("初始化订单数据")
    url = "https://kyfw.12306.cn/otn/confirmPassenger/initDc"
    data = {
        "_json_att": ""
    }
    resp = req.post(url, data=data, headers={**headers,**{
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        # "Cache-Control": "max-age=0",
        "Referer": "https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc",
        "Upgrade-Insecure-Requests": "1",
        "Content-Type": "application/x-www-form-urlencoded",

    }},timeout=9)
    # print(resp.text)
    # 返回一个验证通过信息
    if resp.status_code == requests.codes.ok:
        a1 = re.search(r'globalRepeatSubmitToken.+', resp.text).group()
        globalRepeatSubmitToken = re.sub(r'(globalRepeatSubmitToken)|(=)|(\s)|(;)|(\')', '', a1)

        b1 = re.search(r'key_check_isChange.+', resp.text).group().split(',')[0]
        key_check_isChange = re.sub(r'(key_check_isChange)|(\')|(:)', '', b1)
        print(key_check_isChange)
        return (globalRepeatSubmitToken, key_check_isChange)


def check_user():
    """
    检查用户是否登陆
    :return:
    """
    print("检查用户")
    url = "https://kyfw.12306.cn/otn/login/checkUser"
    data = {
        "_json_att": ""
    }
    resp = req.post(url, data=data, headers=headers, cookies=cookies)
    # 返回一个验证通过信息
    if resp.status_code == requests.codes.ok:
        print("check_user -->"+resp.text)

def submit_order_request(trick_data):
    """
    进行订单检查
    :return:
    """
    print("开始进行订单检查...")
    url = "https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest"

    """
        分析代码的js为：
        https://kyfw.12306.cn/otn/resources/merged/queryLeftTicket_end_js.js?scriptVersion=1.9058 
        在该js中，checkG1234方法就有详细的说明
        格式化之后在7606行
            
        点击预订参数说明：
            p1:车次组第一个元素
            p2:出发时间
            p3:车次数组第三个元素
            p4: 出发地代码
            p5: 结束地代码
            是用来拼接成以下数据的
    """

    """
    
    "secretStr" 车次,需要进行解码
    "train_date": 出发日期
    "back_train_date"  返回日期
    "tour_flag": "dc"  单程/ 往返(wc)
    "purpose_codes":  "ADULT"  普通/学生(0X00)
    "query_from_stati":  出发车站 ，可以在查询车次接口中得到
    "query_to_station":  返回车站，  可以在查询车次接口中得到
    "undefined": ""  应该是跟返回数据相关
    """

    data = {
        "secretStr": parse.unquote(trick_data[len(trick_data) - 1][0]),
        "train_date": date,
        "back_train_date": datetime.datetime.now().strftime('%Y-%m-%d'),
        "tour_flag": "dc",
        "purpose_codes": "ADULT",
        "query_from_station_name": from_station.encode(encoding='UTF-8'),
        "query_to_station_name": to_station,
        "undefined": "",
    }
    
    data_str = ("secretStr=%s&train_date=%s&back_train_date=%s&tour_flag=dc&purpose_codes=ADULT&query_from_station_name=%s&query_to_station_name=%s&undefined" % (trick_data[len(trick_data) - 2][0],date,datetime.datetime.now().strftime('%Y-%m-%d'),from_station,to_station)).encode("UTF-8")
    
    resp = req.post(url, data=data_str, headers={**headers,**{
        "Referer":"https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc",
        "X-Requested-With": "XMLHttpRequest",
    }})
    # 返回一个验证通过信息    
    # print(resp.text)
    if resp.status_code == requests.codes.ok:
        # {"validateMessagesShowId":"_validatorMessage","status":true,"httpstatus":200,"分析js文件":"N","messages":[],"validateMessages":{}}
        # print(resp.text)
        if resp.json()['status'] == True:
            return True
        else:
            print("异常结果：", resp.json()['messages'][0])
            # 强制退出程序，去处理未完成的订单
            exit(0)
            return False
    else:
        print("预提交订单失败")

def init_buy_page():
    print("初始化购票页面")
    url = "https://kyfw.12306.cn/otn/leftTicket/init"
    resp = req.get(url, headers=headers)
    if resp.status_code == requests.codes.ok:
        print("购票页面初始化成功!")


def check_order_info(REPEAT_SUBMIT_TOKEN):
    """
    再次检查订单
    :return:
    """
    """
    js信息：https://kyfw.12306.cn/otn/resources/merged/passengerInfo_js.js?scriptVersion=1.9058
    参数信息
    cancel_flag:2  默认
    bed_level_order_num:000000000000000000000000000000  默认
    passengerTicketStr:3,0,1,黎安永,1,522121197001016817,,N  用户信息
    oldPassengerStr:黎安永,1,522121197001016817,1_
    tour_flag:dc 
    randCode: 需要重新获取验证码，为空
    whatsSelect:1  是否是常用联系人中选择的需要购买车票的人
    _json_att:
    REPEAT_SUBMIT_TOKEN:89089246526d93566b2266de1791af87
    """
    print("检查订单信息")
    data = {
        "cancel_flag": "2",
        "bed_level_order_num": "000000000000000000000000000000",
        "passengerTicketStr": passengerTicketStr,
        "oldPassengerStr": oldPassengerStr,
        "tour_flag": "dc",
        "randCode": "",
        "whatsSelect": "1",
        "_json_att": "",
        "REPEAT_SUBMIT_TOKEN": REPEAT_SUBMIT_TOKEN
    }
    url = "https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo"
    resp = req.post(url, data=data, headers=headers)
    if resp.status_code == requests.codes.ok:
        # print(resp.text)
        if '"submitStatus":true' in resp.text:
            return True
    return False


def confirm_single(REPEAT_SUBMIT_TOKEN, key_check_isChange, trick_data):
    """
    真正的提交订单
    最后一次确认订单
    :return: 返回购票结果
    """
    """
    passengerTicketStr:3,0,1,黎安永,1,522121197001016817,,N
    oldPassengerStr:黎安永,1,522121197001016817,1_
    tour_flag:dc
    randCode:
    purpose_codes:00
    key_check_isChange:1C84C0EA5533D3D73F88A0C7A6BE1E73D65BF9C00C38B3ABF8D09A12
    train_location:QZ
    choose_seats:
    seatDetailType:000
    whatsSelect:1
    roomType:00
    dwAll:N
    _json_att:
    REPEAT_SUBMIT_TOKEN:89089246526d93566b2266de1791af87
    """
    print("最后一次确认订单")
    url = "https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue"
    data = {
        "passengerTicketStr": passengerTicketStr,
        "oldPassengerStr": oldPassengerStr,
        "randCode": "",
        "purpose_codes": "00",
        "key_check_isChange": key_check_isChange,
        "leftTicketStr": trick_data[len(trick_data) - 1][12],
        "train_location": trick_data[len(trick_data) - 1][15],
        "choose_seats": "",
        "seatDetailType": "000",
        "whatsSelect": "1",
        "roomType": "00",
        "dwAll": "N",
        "_json_att": "",
        "REPEAT_SUBMIT_TOKEN": REPEAT_SUBMIT_TOKEN
    }
   
    data_str = ('passengerTicketStr=%s&oldPassengerStr=%s&randCode=&purpose_codes=00&key_check_isChange=%s&leftTicketStr=%s&train_location=%s&choose_seats=&seatDetailType=000&whatsSelect=1&roomType=00&dwAll=N&_json_att=&REPEAT_SUBMIT_TOKEN=%s'%(parse.quote(passengerTicketStr),parse.quote(oldPassengerStr),key_check_isChange,parse.quote(trick_data[len(trick_data) - 2][12]),trick_data[len(trick_data) - 2][15],REPEAT_SUBMIT_TOKEN))
    # url_str = parse.urlencode(data_str)
    # print(data)
    resp = req.post(url, data=data_str, headers={**headers,**{
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json, text/javascript, */*; q=0.01"
    }})
    if resp.status_code == requests.codes.ok:
        print(resp.text)
        # 返回购票结果
        return resp.json()['status']


def get_passenger(REPEAT_SUBMIT_TOKEN):
    """
    获取到用户的乘车人信息
    :param REPEAT_SUBMIT_TOKEN:  uuid
    :return:
    """
    print("获取乘车人信息.......")
    url = "https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs"
    data = {
        "_json_att": "",
        "REPEAT_SUBMIT_TOKEN": REPEAT_SUBMIT_TOKEN
    }
    resp = req.post(url, data=data, headers=headers)
    if resp.status_code == requests.codes.ok:
        pass

def getQueueCount(trick_data, REPEAT_SUBMIT_TOKEN, query_date):
    """
        判断是都有余票
    :param REPEAT_SUBMIT_TOKEN:
    :return:
    """
    print("检查余票...")
    url = "https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount"
    # 将字符串转化为需要的时间
    train_data = tranceDate(query_date)
    data = {
        # 时间
        "train_date": train_data,
        # 车次编号
        "train_no": trick_data[len(trick_data) - 2][2],
        # 火车代码
        "stationTrainCode": trick_data[len(trick_data) - 2][3],
        # 座位类型 1：硬卧 3：硬座
        "seatType": "O",
        # 出发点，终止地址
        "fromStationTelecode": trick_data[len(trick_data) - 2][6],
        "toStationTelecode": trick_data[len(trick_data) - 2][7],
        "leftTicket": trick_data[len(trick_data) - 2][12],
        "purpose_codes": "00",
        "train_location": trick_data[len(trick_data) - 2][15],
        "_json_att": "",
        "REPEAT_SUBMIT_TOKEN": REPEAT_SUBMIT_TOKEN
    }
    data_str = "train_date=%s&train_no=%s&stationTrainCode=%s&seatType=O&fromStationTelecode=%s&toStationTelecode=%s&leftTicket=%s&purpose_codes=00&train_location=%s&_json_att=&REPEAT_SUBMIT_TOKEN=%s" %(parse.quote(train_data),trick_data[len(trick_data) - 2][2],trick_data[len(trick_data) - 2][3],trick_data[len(trick_data) - 2][6],trick_data[len(trick_data) - 2][7],trick_data[len(trick_data) - 2][12],trick_data[len(trick_data) - 2][15],REPEAT_SUBMIT_TOKEN)
    # print(data)
    resp = req.post(url, data=data_str, headers={**headers,**{
        "Referer": "https://kyfw.12306.cn/otn/confirmPassenger/initDc",
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }})
    if resp.status_code == requests.codes.ok:
        # 有余票，返回值将会是True
        print(resp.text)


def tranceDate(param):
    """
    将传递的字符串转化为时间
    :param param: 时间： 2017-12-29
    :return: Fri Dec 29 2017 00:00:00 GMT+0800 (中国标准时间)
    """
    ts = time.mktime(time.strptime(param, "%Y-%m-%d"))
    s = time.ctime(ts)
    t1 = s[0:11] + s[20:] + " 00:00:00 GMT+0800 (中国标准时间)"
    return t1

def getOrder(REPEAT_SUBMIT_TOKEN):
    flag = True
    while(flag):
        url='https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime?random={}&tourFlag=dc&_json_att=&REPEAT_SUBMIT_TOKEN={}'.format('%10d' % (time.time() * 1000),REPEAT_SUBMIT_TOKEN)
        res = req.get(url,headers={
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Referer": "https://kyfw.12306.cn/otn/confirmPassenger/initDc",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "User-agent": "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0",
            "DNT": "1",
        },verify=False)
        try:
            json_response = res.json()
        except:
            print("获取订单号出现错误")
            exit()
        print(json_response)
        wait_time = json_response['data']['waitTime']
        order_id = json_response['data']['orderId']
        # if wait_time == -100:
        #     return 
        if order_id:
            flag = False
        elif json_response['data'].get('errorcode'):
            print(json_response['data'].get('msg'))
            # exit()
            return
        time.sleep(randint(4,7))
    print("获得订单号:%s" %order_id)
    return order_id

def resultOrderForDcQueue(orderId,REPEAT_SUBMIT_TOKEN):
    if orderId == None:
        return False
    url = "https://kyfw.12306.cn/otn/confirmPassenger/resultOrderForDcQueue"
    data_str = "orderSequence_no=%s&_json_att=&REPEAT_SUBMIT_TOKEN=%s" %(orderId,REPEAT_SUBMIT_TOKEN)
    res = req.get(url,data=data_str,headers={**headers,**{
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer": "https://kyfw.12306.cn/otn/confirmPassenger/initDc",
    }})
    print(res.text)
    try:
        json_response = res.json()
    except:
        return True 
    print(json_response)
    if json['data'].get('submitStatus'):
        return True
    else:
        return False
def LogOut():
    req.post("https://kyfw.12306.cn/otn/login/loginOut",headers=headers)

def login_12306(point):
    # 进行登录
    login_rs = login(point)
    if login_rs is True:
        print("登录成功")
        #  阶段一，验证是否登录
        # 验证 登录 获取tk
        # resp = req.get(url=r'https://kyfw.12306.cn/otn/passport?redirect=/otn/login/userLogin')
        # print(resp.text)
        check_uamauthclient(auth_uamtk())

        # 阶段二 进行车票确认
        # 初始化买票页面
        init_buy_page()
        print("查询车票数据: 出发地:{},目的地:{},出发日期:{}".format(from_station, to_station, date))
        # 开启自动查询购票
        # 查询票
        qt = queryTrain(req, headers)
        query_ticket_data = qt.query_trict(from_station, to_station, date)
        # print("输出车次数据")
        print(query_ticket_data[len(query_ticket_data) - 2])
        # 检查用户登陆状态
        check_user()

        isAutoBuy = True
        while (isAutoBuy):
            try:
                # 初始化订单
                order_check_result = submit_order_request(query_ticket_data)
                # 说明订单成功，需要确认订单即可
                if order_check_result == True:
                    # 初始化订单数据,获取到REPEAT_SUBMIT_TOKEN,key_check_isChange,leftTicketStr
                    REPEAT_SUBMIT_TOKEN, key_check_isChange = initDc()
                    # 检查订单信息
                    print("得到校验uuid:", REPEAT_SUBMIT_TOKEN)
                    # 获取该用户下的乘车人信息
                    get_passenger(REPEAT_SUBMIT_TOKEN)
                    # 进行订单确认
                    check_order_result = check_order_info(REPEAT_SUBMIT_TOKEN)
                    if check_order_result == True:
                        print("订单检查成功，确认订单")
                        # 查询订单队列余票
                        getQueueCount(query_ticket_data, REPEAT_SUBMIT_TOKEN, date)
                        # 最后一次确认订单
                        ok = confirm_single(REPEAT_SUBMIT_TOKEN, key_check_isChange, query_ticket_data)
                        if ok == True:
                            if resultOrderForDcQueue(getOrder(REPEAT_SUBMIT_TOKEN),REPEAT_SUBMIT_TOKEN):
                                print("购票成功,请前往官网支付!")
                                LogOut()
                                exit(0)
                            else:
                                time.sleep(10)
                        else:
                            # 休眠5秒钟，防止被防刷票封ip
                            time.sleep(10)

            except Exception:
                traceback.print_exc()
                print("发生异常")
    else:
        return False

if __name__ == "__main__":
    url = "https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand&0.6523880813900003"
    parent_file_url = "./images"
    mck = check_captcha(parent_file_url, url)
    # 进行验证码识别
    rs = list()
    yanSol = ['35,35', '105,35', '175,35', '245,35', '35,105', '105,105', '175,105', '245,105']

    flag = 1
    while(flag < 3):
        print("第%d尝试自动识别验证码" %flag)
        point = mck.get_key()
        if  len(point) == 0:
            flag += 1
            continue
        else:
            for x in point:
                rs.append(yanSol[int(x)-1])
            check_result, req = mck.check(rs)
            if check_result == True:
                login_12306(rs)
                break
            else:
                flag += 1
                continue
    if flag == 3:
        print("验证码自动识别出现多次错误，采用手动识别")
        rs = mck.getPointManually()
        check_result, req = mck.check(rs)
        if check_result == True:
            login_12306(rs)    
    
