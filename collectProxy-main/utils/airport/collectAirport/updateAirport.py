import re
import os
import requests
from datetime import datetime   #时间
import yaml

#文件路径
INFO_YAML = './utils/airport/collectAirport/data/sub_info.yaml'
AIRPORTFILE = './utils/airport/airportRegister/trial.cfg'
COLLECTFILE = './utils/airport/collectAirport/data/valid-domains.txt'
valid_list={
  'polarxy':'https://raw.githubusercontent.com/polarxy/aggregator/refs/heads/main/data/valid-domains.txt',
  'PangTouY00':'https://raw.githubusercontent.com/PangTouY00/aggregator/refs/heads/main/data/valid-domains.txt',
  'qjlxg':'https://raw.githubusercontent.com/qjlxg/aggregator/refs/heads/main/data/valid-domains.txt',
  }
"""
AIRPORTFILE = './trial.cfg'
COLLECTFILE = './valid-domains.txt'
valid_list={
  'polarxy':'https://ghraw.eu.org/polarxy/aggregator/refs/heads/main/data/valid-domains.txt',
  'PangTouY00':'https://ghraw.eu.org/PangTouY00/aggregator/refs/heads/main/data/valid-domains.txt',
  'rx':'https://ghraw.eu.org/rxsweet/getAirport/refs/heads/main/data/valid-domains.txt',
  }
"""

def cfg_alive(url):#测试原机场文件trial.cfg中机场是否能用
    headers={
    "User-Agent":"okhttp/3.15",
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
    }
    try:
        if 'buy  period=' in url:
            url1 = re.search(r'(.*?)  buy  period=', url).group(1)
            r=requests.get(url1,headers=headers, timeout=5.0)
        else:
            r=requests.get(url,headers=headers, timeout=5.0)
        if r.status_code==200:
            #print(url)
            return url
    except requests.exceptions.RequestException as e:  
        #print(f'获取{url}内容时出错')
        try:
            if 'https://' in url:
                url = re.sub('https://', 'http://', url)
                r=requests.get(url,headers=headers, timeout=5.0)
                if r.status_code==200:
                    #print(url)
                    return url
        except requests.exceptions.RequestException as e:  
            #print(f'获取{url}内容时出错')
            pass
    return  False
    
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
    print(f'剩余总数 {str(len(urlList))}\n')
    return urlList
    
def saveList(configList,file_addr):#保存文件
  
    if configList:
        print('保存' + file_addr + '文件')
        file=open(file_addr,"w")
        file.write('\n'.join(configList))
        file.close()
        print('抓取时间：\t',datetime.now())
        
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
        print(f'获取{url}内容时出错')
        return []
        
def fetchApiUrl(list):#获取列表网站的json内容，再获取的内容中的api_url
    domainsList=[]
    for key,value in list.items():
        domains=getContent(value)
        if domains and 'http' in domains:
            try:
                urlList = re.split(r'\n+',domains)#字符串内容转list
                domainsList.extend(urlList)
            except Exception as e: 
                #print(str(key) + str(e) + '获取内容中的API时，出现异常')
                print('抓取其他大佬更新的机场时，出现错误！')
    if domainsList:
        return domainsList
    else:
        return []
    

def url_rm(validList):
    #先列表去重
    validList = list_rm(validList)
    url_yaml = {}
    allurl = []
    for valid in validList:
        if 'buy  period=' in valid:
            url = re.search(r'(.*?)  buy  period=', valid).group(1)
            url_content = getContent(url)
        else:
            url_content = getContent(valid)
        #获取机场名字判断是否重复
        name = re.search("<title>(.*?)</title>", str(url_content))
        #如果获取到内容
        if name:
            url_yaml[valid] = name.group(1)
    temp = {}
    for key,value in url_yaml.items():
        if value not in temp:
            temp[value] = key
            #allurl.append(key)
        elif '  buy  period=' in key:
            temp[value] = key
    for k,v in temp.items():
        allurl.append(v)
    return allurl
            
        
def editUrl(validList):
    newList = []
    for valid in validList:
        if 'https' in valid:
            valid = re.sub(f'https://','',valid)
        elif 'http' in valid:
            valid = re.sub(f'http://','',valid)
        newList.append(valid)
    return newList

def updateAirport():
    aliveList = []
    #打开机场列表文件
    if os.path.exists(AIRPORTFILE) and os.path.isfile(AIRPORTFILE):
        file = open(AIRPORTFILE, 'r', encoding='utf-8')
        airportlist_content = file.read()
        file.close()
        airportlist = re.split(r'\n+',airportlist_content)

    #机场的起始行数,找到可用的，删除原始数据
    i= 20   
    lens = len(airportlist)
    alive = []
    while i < lens:
        if '##' in airportlist[i]:
            i = i + 1
            continue
        if airportlist[i]:
            #给文件中的机场添加https前缀
            airportlist[i] = 'https://'+airportlist[i]
            url = cfg_alive(airportlist[i])
            if url:
                alive.append(url)
        airportlist.pop(i)
        lens = lens -1
    
    #自己抓取的，有订阅信息的机场列表
    url_info = []
    with open(INFO_YAML,encoding="UTF-8") as f:
        dict_url = yaml.load(f, Loader=yaml.FullLoader)
    if dict_url:
        for k,v in dict_url.items():
            if 'buy_code' in v:
                url_info.append(v['url'] + v['buy_code'])
            else:
                url_info.append(v['url'])

    #抓取其他大佬更新的机场
    validList = fetchApiUrl(valid_list)
    
    if airportlist:#如果要更新的机场文件有内容
        #合并
        aliveList.extend(alive)#原机场列表
        aliveList.extend(url_info)#自己抓取的机场列表
        aliveList.extend(validList)#其他人抓取的机场列表
        
        #去重
        aliveList = url_rm(aliveList)
        #去掉http头
        aliveList = editUrl(aliveList)
        #添加到机场列表
        print(f'最终添加机场数量：{len(aliveList)}')
        airportlist.extend(aliveList)
        #保存
        saveList(airportlist,AIRPORTFILE)
if "__name__==__main__":#主程序开始的地方
    nowtime = datetime.now()
    if nowtime.weekday() == 4 and nowtime.hour > 20:#每周五更新晚20点后更新
        print("更新机场开始！")
        updateAirport()
    else:
        print("本次不更新机场！")
