import re
import requests
from datetime import datetime   #时间
import time
from tqdm import tqdm
import threading
import json5

api_url_list={
  'hd9211':'https://raw.githubusercontent.com/hd9211/Tvbox1/refs/heads/main/zy.json',
  '2hacc':'https://raw.githubusercontent.com/2hacc/Video/refs/heads/main/zy.json',
  'shemc':'https://raw.githubusercontent.com/shemc/script/refs/heads/main/cy.txt',
  'PowerTechott1':'https://raw.githubusercontent.com/PowerTechott/baotv/refs/heads/main/bh1',
  'PowerTechott2':'https://raw.githubusercontent.com/PowerTechott/baotv/refs/heads/main/bh2',
  'PowerTechott3':'https://raw.githubusercontent.com/PowerTechott/baotv/refs/heads/main/bh3 ',
  'xyq254245':'https://raw.githubusercontent.com/xyq254245/HikerRule/refs/heads/main/ZYWCJ.txt',
  "aaabbbxu":"https://raw.githubusercontent.com/aaabbbxu/tvboxs/refs/heads/main/boxs.json",
  "aaabbbxu1":"https://raw.githubusercontent.com/aaabbbxu/tvboxs/refs/heads/main/boxs1.json",
  "aaabbbxu2":"https://raw.githubusercontent.com/aaabbbxu/tvboxs/refs/heads/main/boxs2.json",
  "月光线路":"https://raw.githubusercontent.com/guot55/yg/main/box原.json",
  "月光线路3":"https://raw.githubusercontent.com/guot55/yg/refs/heads/main/pro.json",
  "潇洒线路":"https://raw.githubusercontent.com/PizazzGY/TVBox/main/api.json",
  "南风":"https://raw.githubusercontent.com/yoursmile66/TVBox/main/XC.json ",
  "香雅情":"https://raw.githubusercontent.com/xyq254245/xyqonlinerule/main/XYQTVBox.json",
  "巧技":"http://cdn.qiaoji8.com/tvbox.json",
  "PG线路":"https://git.acwing.com/iduoduo/orange/-/raw/main/jsm.json",
  "俊于":"http://home.jundie.top:81/top98.json",
  "dxawi":"https://raw.githubusercontent.com/dxawi/0/refs/heads/main/0.json",
  "slasjh18":"https://raw.githubusercontent.com/slasjh/18/refs/heads/main/切片大全",
  "liucn":"https://raw.liucn.cc/box/m.json",
  "PG_api":"https://raw.githubusercontent.com/ls125781003/tvboxtg/refs/heads/main/PG/api.json",
  "PG_jsm":"https://raw.githubusercontent.com/ls125781003/tvboxtg/refs/heads/main/PG/jsm.json",
  'n3rddd_vod':'https://raw.githubusercontent.com/n3rddd/N3RD/master/JN/lemvod.json',
  'n3rddd_lem':'https://raw.githubusercontent.com/n3rddd/N3RD/refs/heads/master/JN/lem.json',
  '小而美':'https://raw.githubusercontent.com/xixifree/xxbox/master/0821.json',  
  "anaer":"https://raw.githubusercontent.com/anaer/Meow/refs/heads/main/meow.json",
  "qq1719248506":"https://raw.githubusercontent.com/qq1719248506/Video-interface/refs/heads/main/config.json",
  "FongMi_fish2018":"http://www.fish2018.us.kg/z/FongMi.json",
  "harry0071":"https://raw.githubusercontent.com/harry0071/keer/refs/heads/main/tv.json",
  'rx_vod':'https://rxsub.eu.org/tvbox/vod.json',
  "喵影视":"http://meowtv.top/tv",
  }

def saveZYWCJ(urllist,file_addr):#存入可用的资源网文件
    fileUrlList = []
    #添加头
    fileUrlList.append('#自用筛选')
    num = 0
    #给url 添加名字
    for key in urllist:
        num = num + 1
        key ='影视' + str(num) + ',' + key
        fileUrlList.append(key)
    #添加尾
    fileUrlList.append('#')
    saveList(fileUrlList,file_addr)
    
def saveList(configList,file_addr):#保存文件
  
    if configList:
        print('保存' + file_addr + '文件')
        file=open(file_addr,"w")
        file.write('\n'.join(configList))
        file.close()
        print('抓取时间：\t',datetime.now())

def url_ilive(url,bar,newlist,bedlist,sexlist): #检测网站是否可用可搜索
    newurl = url + '?wd=1'  #添加搜索代码
    try:
        r=requests.get(url, timeout=3.0)
        if r.status_code==200:
            r1=requests.get(newurl, timeout=3.0)
            if r != r1:
                try:
                    r1json = json5.loads(r1.text)
                    if '1' in r1json['list'][0]['vod_name']:
                    #if '{"code":1,"msg' in str(text):#如果内容包含次特征(说明可搜索)
                    #判断是否是adult网站
                        if '有码' in r1.text or '无码' in r1.text or  '传媒' in r1.text or '女优' in r1.text or '番号' in r1.text or '福利姬' in r1.text or 'JAV' in r1.text or 'Tokyo' in r1.text : 
                            sexlist.append(url)
                        else:
                            newlist.append(url)
                    else:
                        bedlist.append(url)
                except Exception as e:  
                    bedlist.append(url)
        else:
            bedlist.append(url)
    except requests.exceptions.RequestException as e:  
        pass
    bar.update(1)
    
def check_url(url_list):#检测列表网站挂了没
    goodlist = []
    bedlist = []
    sexlist = []

    #进度条添加
    url_list_len = len(url_list)
    thread_max_num = threading.Semaphore(32)
    bar = tqdm(total=url_list_len, desc='Testing url ilive：')
    thread_list = []
    
    for url in url_list:
        #为每个URL创建线程
        t = threading.Thread(target=url_ilive, args=(url,bar,goodlist,bedlist,sexlist))
        #加入线程池
        # 加入线程池并启动
        thread_list.append(t)
        t.daemon=True
        t.start()
    #等待所有线程完成，配合上面的t.daemon
    for t in thread_list:
        t.join()
    bar.close() #进度条结束
    
    #存储文件
    saveList(goodlist,"api_good.txt")
    #saveList(bedlist,"api_bad.txt")
    saveList(sexlist,"api_sex.txt")
    
    #存入可用的资源网文件
    saveZYWCJ(goodlist,'rx_ZYWCJ.txt')
    saveZYWCJ(sexlist,'cr.txt')

def list_rm(urlList):#列表去重
    begin = 0
    rm = 0
    length = len(urlList)
    print(f'\n-----去重开始-----\n')
    while begin < length:
        proxy_compared = urlList[begin]
        begin_2 = begin + 1
        while begin_2 <= (length - 1):
            if proxy_compared == urlList[begin_2]:
                urlList.pop(begin_2)
                length -= 1
                begin_2 -= 1
                rm += 1
            begin_2 += 1
        begin += 1
    print(f'重复数量 {rm}\n-----去重结束-----\n')
    return urlList

def getContent(url):#获取网站的内容，将获取的内容返回
    headers={
    "User-Agent":"okhttp/3.15",
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
    }
    try:
        r=requests.get(url,headers=headers, timeout=5.0)
        if r.status_code==200:
            r.encoding='utf-8'    #编码方式
            return r.text
    except requests.exceptions.RequestException as e:  
        #print(e)
        #print('getContent()功能中出现的错误！获取内容失败，或者打开网址错误!')
        pass

def fetchApiUrl(list):#获取列表网站的json内容，再获取的内容中的api_url
    configList=[]
    for key,value in list.items():
        config=getContent(value)
        if config:
            try:
                #https网址搜索
                # 查找所有的 api
                httpsMatchAPI = re.findall("https://(.*?)/provide/vod", config)
                """
                #好像xml后缀的都不能用，或者自己下面的去重复有问题
                #测试的话，添加带#号的3条命令，列表保存文件试试
                #apiList2 = []
                httpsMatchAPI2 = re.findall("https://(.*?)/xml", config)
                if httpsMatchAPI2:
                    #httpsMatchAPI还原网址
                    for key2 in httpsMatchAPI2:
                        key2 = 'https://' + key2 +'/xml/'
                        configList.append(key2)
                        #apiList2.append(key2)
                        #查找重复    
                        for key in httpsMatchAPI:
                            if key in key2:
                                #print('key = ' + key)
                                #print('key2 = ' + key2)
                                httpsMatchAPI.pop(key)
                #saveList(apiList2,'api2_test.txt')
                """
                if httpsMatchAPI:
                    #httpsMatchAPI还原网址
                    for key in httpsMatchAPI: 
                        key = 'https://' + key + '/provide/vod/'
                        configList.append(key)
                    
                #http网址搜索
                # 查找所有的 api
                httpMatchAPI = re.findall("http://(.*?)/provide/vod", config)
                if httpMatchAPI:
                    #httpsMatchAPI还原网址
                    for key in httpMatchAPI: 
                        key = 'http://' + key + '/provide/vod/'
                        configList.append(key)
                        
            except Exception as e: 
                #print(str(key) + str(e) + '获取内容中的API时，出现异常')
                pass            
    return configList

    
if "__name__==__main__":#主程序开始的地方
    configList = fetchApiUrl(api_url_list)
    configList = list_rm(configList)
    #saveList(configList,"api_all.txt")
    check_url(configList)
