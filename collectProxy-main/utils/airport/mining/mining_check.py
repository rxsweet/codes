import re
import time
import requests
import threading
from tqdm import tqdm
from retry import retry
from datetime import datetime
import math
import yaml
import urllib.parse

"""
# 获取当天日期，格式为 YYYYMMDD
#today = datetime.today().strftime('%Y%m%d')
# 动态生成 URL，替换日期部分
#url = f'https://clashgithub.com/wp-content/uploads/rss/{today}.txt'
nowtime = datetime.now()
year = nowtime.year
month = nowtime.month
today = datetime.today().strftime('%Y%m%d')
s = str(year) + '/' + str(month) + '/' + str(today)
urlList = [
'https://ghraw.eu.org/abshare/abshare.github.io/refs/heads/main/README.md',
'https://ghraw.eu.org/abshare3/abshare3.github.io/refs/heads/main/README.md',
'https://ghraw.eu.org/tolinkshare2/tolinkshare2.github.io/refs/heads/main/README.md',
'https://ghraw.eu.org/toshare5/toshare5.github.io/refs/heads/main/README.md',
'https://ghraw.eu.org/mkshare3/mkshare3.github.io/refs/heads/main/README.md',
'https://ghraw.eu.org/mksshare/mksshare.github.io/refs/heads/main/README.md'
]
"""

urlList = [
'https://raw.githubusercontent.com/abshare/abshare.github.io/refs/heads/main/README.md',
'https://raw.githubusercontent.com/abshare3/abshare3.github.io/refs/heads/main/README.md',
'https://raw.githubusercontent.com/tolinkshare2/tolinkshare2.github.io/refs/heads/main/README.md',
'https://raw.githubusercontent.com/toshare5/toshare5.github.io/refs/heads/main/README.md',
'https://raw.githubusercontent.com/mkshare3/mkshare3.github.io/refs/heads/main/README.md',
'https://raw.githubusercontent.com/mksshare/mksshare.github.io/refs/heads/main/README.md'
]


# 流量byte转字符串str大小
def pybyte(size, dot=2):
    size = float(size)
    # 位 比特 bit
    if 0 <= size < 1:
        human_size = str(round(size / 0.125, dot)) + 'b'
    # 字节 字节 Byte
    elif 1 <= size < 1024:
        human_size = str(round(size, dot)) + 'B'
    # 千字节 千字节 Kilo Byte
    elif math.pow(1024, 1) <= size < math.pow(1024, 2):
        human_size = str(round(size / math.pow(1024, 1), dot)) + 'KB'
    # 兆字节 兆 Mega Byte
    elif math.pow(1024, 2) <= size < math.pow(1024, 3):
        human_size = str(round(size / math.pow(1024, 2), dot)) + 'MB'
    # 吉字节 吉 Giga Byte
    elif math.pow(1024, 3) <= size < math.pow(1024, 4):
        human_size = str(round(size / math.pow(1024, 3), dot)) + 'GB'
    # 太字节 太 Tera Byte
    elif math.pow(1024, 4) <= size < math.pow(1024, 5):
        human_size = str(round(size / math.pow(1024, 4), dot)) + 'TB'
    # 拍字节 拍 Peta Byte
    elif math.pow(1024, 5) <= size < math.pow(1024, 6):
        human_size = str(round(size / math.pow(1024, 5), dot)) + 'PB'
    # 艾字节 艾 Exa Byte
    elif math.pow(1024, 6) <= size < math.pow(1024, 7):
        human_size = str(round(size / math.pow(1024, 6), dot)) + 'EB'
    # 泽它字节 泽 Zetta Byte
    elif math.pow(1024, 7) <= size < math.pow(1024, 8):
        human_size = str(round(size / math.pow(1024, 7), dot)) + 'ZB'
    # 尧它字节 尧 Yotta Byte
    elif math.pow(1024, 8) <= size < math.pow(1024, 9):
        human_size = str(round(size / math.pow(1024, 8), dot)) + 'YB'
    # 千亿亿亿字节 Bront Byte
    elif math.pow(1024, 9) <= size < math.pow(1024, 10):
        human_size = str(round(size / math.pow(1024, 9), dot)) + 'BB'
    # 百万亿亿亿字节 Dogga Byte
    elif math.pow(1024, 10) <= size < math.pow(1024, 11):
        human_size = str(round(size / math.pow(1024, 10), dot)) + 'NB'
    # 十亿亿亿亿字节 Dogga Byte
    elif math.pow(1024, 11) <= size < math.pow(1024, 12):
        human_size = str(round(size / math.pow(1024, 11), dot)) + 'DB'
    # 万亿亿亿亿字节 Corydon Byte
    elif math.pow(1024, 12) <= size:
        human_size = str(round(size / math.pow(1024, 12), dot)) + 'CB'
    # 负数
    else:
        raise ValueError('{}() takes number than or equal to 0, but less than 0 given.'.format(pybyte.__name__))
    return human_size


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
    
def sub_check(url,alive_yaml,bar):
    headers = {'User-Agent': 'ClashforWindows/0.18.1'}
    with thread_max_num:
        @retry(tries=3)
        def start_check(url):
            res=requests.get(url,headers=headers,timeout=5)#设置5秒超时防止卡死
            if res.status_code == 200:
                res.encoding='utf-8' 
                try: #有流量信息
                    info = res.headers['subscription-userinfo']
                    #print(str(res.headers))
                    info_num = re.findall('\d+',info)
                    #info_num[3] - 到期时间 
                    #info_num[2]- 总流量
                    #info_num[1]-使用的下载流量
                    #info_num[0] - 使用的上传流量
                    time_now=int(time.time())
                    # 剩余流量大于10MB
                    if int(info_num[2])-int(info_num[1])-int(info_num[0])>10485760:
                        if len(info_num) == 4: # 有时间信息
                            if time_now <= int(info_num[3]): # 没有过期
                                usetime = int(info_num[3])
                                date_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(usetime))
                                #date_str = time.strftime('%Y-%m-%d', time.localtime(usetime))
                                liuliang_str = pybyte(int(info_num[2])-int(info_num[1])-int(info_num[0]))
                                #查看有节点再添加
                                if res.text:
                                    try:
                                        proxyconfig = yaml.load(res.text, Loader=yaml.FullLoader)
                                        #print('len = '+ str(len(proxyconfig['proxies'])))
                                        node_num = len(proxyconfig['proxies'])
                                        if node_num > 0:
                                            #
                                            url_yaml = {}
                                            url_yaml['api'] = url
                                            url_yaml['time'] = date_str
                                            url_yaml['free'] = liuliang_str
                                            url_yaml['nodes'] = str(node_num)
                                            url_yaml['url'] = res.headers['profile-web-page-url']
                                            #url_yaml['content-disposition'] = res.headers['content-disposition']
                                            name = re.search(f"UTF-8''(.*)", res.headers['content-disposition'])
                                            #如果获取到内容
                                            if name:
                                                url_yaml['name'] = urllib.parse.unquote(name.group(1))
                                                #print("url_yaml['content-disposition'] = " + url_yaml['content-disposition'] )
                                            alive_yaml.append(url_yaml)
                                    except Exception as e: 
                                        print('获取机场信息失败')
                                        print(e)
                                
                                #print(url+' 到期时间：' + date_str +' -- 剩余流量：' + liuliang_str)
                            else: # 已经过期
                                old_list.append(url)
                        else: # 没有时间信息
                            liuliang_str = pybyte(int(info_num[2])-int(info_num[1])-int(info_num[0]))
                            #查看有节点再添加
                            if res.text:
                                try:
                                    proxyconfig = yaml.load(res.text, Loader=yaml.FullLoader)
                                    #print('len = '+ str(len(proxyconfig['proxies'])))
                                    node_num = len(proxyconfig['proxies'])
                                    if node_num > 0:
                                        #
                                        url_yaml = {}
                                        url_yaml['api'] = url
                                        url_yaml['time'] = '永久有效'
                                        url_yaml['free'] = liuliang_str
                                        url_yaml['nodes'] = str(node_num)
                                        url_yaml['url'] = res.headers['profile-web-page-url']
                                        #url_yaml['content-disposition'] = res.headers['content-disposition']
                                        name = re.search(f"UTF-8''(.*)", res.headers['content-disposition'])
                                        #如果获取到内容
                                        if name:
                                           url_yaml['name'] = urllib.parse.unquote(name.group(1))
                                        alive_yaml.append(url_yaml)
                                except Exception as e: 
                                    print('获取机场信息失败')
                                    print(e)
                            #print(url+' 到期时间：无 -- 剩余流量：'+ liuliang_str)
                    else: # 流量小于10MB
                        #old_list.append(url)
                        pass
                except:
                    #old_list.append(url)  
                    pass
                # output_text='无流量信息捏'
            else:
                #old_list.append(url)
                pass
        try:
            start_check(url)
        except:
            #old_list.append(url)
            pass
        bar.update(1)

def subs_check(subs,alive_yaml):

    thread_max_num =threading.Semaphore(32) #32线程
    bar = tqdm(total=len(subs), desc='订阅筛选：')
    thread_list = []
    for url in subs:
        #为每个新URL创建线程
        t = threading.Thread(target=sub_check, args=(url,alive_yaml,bar))
        #加入线程池并启动
        thread_list.append(t)
        t.daemon=True
        t.start()
    for t in thread_list:
        t.join()
    bar.close()
    return alive_yaml

def yaml_rm(alive_yaml):#列表去重
    begin = 0
    rm = 0
    length = len(alive_yaml)
    print(f'\n-----去重开始-----\n')
    while begin < length:
        proxy_compared = alive_yaml[begin]
        begin_2 = begin + 1
        while begin_2 <= (length - 1):
            try:
                if proxy_compared['name'] == alive_yaml[begin_2]['name']:
                    if proxy_compared['time'] == '永久有效' or alive_yaml[begin_2]['time'] == '永久有效':
                        alive_yaml.pop(begin_2)
                    else:
                        date_obj = datetime.strptime(proxy_compared['time'], "%Y-%m-%d %H:%M:%S")
                        date_obj1 = datetime.strptime(alive_yaml[begin_2]['time'], "%Y-%m-%d %H:%M:%S")
                        if date_obj < date_obj1:
                            alive_yaml[begin]['api'] = alive_yaml[begin_2]['api']
                            alive_yaml[begin]['time'] = alive_yaml[begin_2]['time']
                        alive_yaml.pop(begin_2)
                    length -= 1
                    begin_2 -= 1
                    rm += 1
            except:
                pass
            begin_2 += 1
        begin += 1
    print(f'重复数量 {rm}\n-----去重结束-----\n')
    print(f'剩余总数 {str(len(alive_yaml))}\n')
    return alive_yaml

def xfxssr(url):
    try:
        r=requests.get(url, timeout=5.0)
        if r.status_code==200:
            r.encoding='utf-8'    #编码方式
            #matches = re.findall(r'https://www.xfxssr.me/nav/(.*?).html', r.text)
            #node_url = re.search(r"(https://www.mibei77.com/[^<\s]*.html)", r.text).group(0)#匹配第一个相同的网址
            matches = re.findall(r'https://www.xfxssr.me/nav/\d{4}.html', r.text)
            if matches:
                u = matches[0]
                #print(u)
                r1=requests.get(u, timeout=5.0)
                if r1.status_code==200:
                    r1.encoding='utf-8'    #编码方式
                    pattern = r'http://subssr\.xfxvpn\.me[^<\s"]*'
                    matches1 = re.findall(pattern, r1.text, flags=re.S)
                    if matches1:
                        #print('\n'.join(matches1))
                        return matches1
            else:
                print("订阅链接未捕获：", matches)
        return []
    except requests.exceptions.RequestException as e:  
        print(f'订阅链接未捕获:{url}')
        return []
        

def getsub(url):
    subs = []
    try:
        r=requests.get(url, timeout=5.0)
        if r.status_code==200:
            r.encoding='utf-8'    #编码方式
            #matches = re.findall(r'https://www.xfxssr.me/nav/(.*?).html', r.text)
            #node_url = re.search(r"(https://www.mibei77.com/[^<\s]*.html)", r.text).group(0)#匹配第一个相同的网址
            #matches = re.findall('(http.*)', r.text)
            #matches = re.findall(r"(http.*?)\r\n", r.text)
            #print(matches)
            res = re.search(
                r".*?Clash订阅.*?(?P<clash>http.*?)\r\n",
                r.text,
                re.DOTALL
                )
            #返回的是dict格式,,clash:https://Gjre6H.absslk.xyz/719235ba9270100542db0a0a5b835f77
            links = res.groupdict()
            if links:
                for key,value in links.items():
                    subs.append(value)
                return subs
        return []
    except requests.exceptions.RequestException as e:  
        print(f'订阅链接未捕获:{url}')
        return []
def getSubs(urlList):
    subs = []
    for url in urlList:
        sub = getsub(url)
        subs.extend(sub)
    #print('\n'.join(subs))
    return subs

def wzdnzd_aggregator():
    repolist  = [
    'https://raw.githubusercontent.com/PangTouY00/aggregator/refs/heads/main/data/subscribes.txt',
    'https://raw.githubusercontent.com/qjlxg/aggregator/refs/heads/main/data/subscribes.txt',
    'https://raw.githubusercontent.com/polarxy/aggregator/refs/heads/main/data/subscribes.txt'
    ]
    subs = []
    for url in repolist:
        try:
            r=requests.get(url, timeout=5.0)
            if r.status_code==200:
                r.encoding='utf-8'    #编码方式
                if r.text:
                    api_list = re.split(r'\n+',r.text)
                    if api_list:
                        subs.extend(api_list)
        except requests.exceptions.RequestException as e:  
            print(f'订阅链接未捕获:{url}')
            pass
    return subs
if "__name__==__main__":#主程序开始的地方

    #INFO_YAML = './2.yaml'
    #CONFIG_YAML = './_1.yaml'
    #TG_SOURCE_PATH = './TG.yaml'
    INFO_YAML = './utils/airport/mining/sub_info.yaml'
    INFO_YAML_WEB = './sub/sources/sub_info.txt'
    CONFIG_YAML = './utils/airport/mining/mining_config.yaml'
    TG_SOURCE_PATH = './utils/collectTGsub/TGsources.yaml'

    subs = []
    
    #读取txt文件里的subs
    #file = open('1.txt', 'r', encoding='utf-8')
    #subs_content = file.read()
    #file.close()
    #subs = re.split(r'\n+',subs_content)
    
    #读取api.yaml文件里的url订阅地址
    with open(INFO_YAML,encoding="UTF-8") as f:
        dict_url = yaml.load(f, Loader=yaml.FullLoader)
    if dict_url:
        for url in dict_url:
            subs.append(url['api'])
    #读取抓取的TG源
    with open(TG_SOURCE_PATH,encoding="UTF-8") as f:
        yamldata = yaml.load(f, Loader=yaml.FullLoader)
    if yamldata:
        for url in yamldata['机场订阅']:
            subs.append(url) 
        
    #收集xfxssr网站的airport
    subs.extend(xfxssr("https://www.xfxssr.me/nav/blog"))
    #收集urllist里网站的airport
    subs.extend(getSubs(urlList))
    subs.extend(wzdnzd_aggregator())
    #去重 
    subs = list_rm(subs)
    
    #将可用的机场存到alive_yaml列表
    alive_yaml = []
    #alive_yaml = subs_check(subs,alive_yaml)
    thread_max_num =threading.Semaphore(32) #32线程
    bar = tqdm(total=len(subs), desc='订阅筛选：')
    thread_list = []
    for url in subs:
        #为每个新URL创建线程
        t = threading.Thread(target=sub_check, args=(url,alive_yaml,bar))
        #加入线程池并启动
        thread_list.append(t)
        t.daemon=True
        t.start()
    for t in thread_list:
        t.join()
    bar.close()
    # 去重
    alive_yaml = yaml_rm(alive_yaml)
    
    #save yaml
    with open(INFO_YAML, 'w',encoding="utf-8") as f:
        data = yaml.dump(alive_yaml, f,allow_unicode=True)
    #save to sub, web read
    with open(INFO_YAML_WEB, 'w',encoding="utf-8") as f:
        data = yaml.dump(alive_yaml, f,allow_unicode=True)
    #收集alive
    alive = []
    for url in alive_yaml:
        alive.append(url['api'])

    #打开读取 config.yaml    
    with open(CONFIG_YAML,encoding="UTF-8") as f:
        dict_url = yaml.load(f, Loader=yaml.FullLoader)
    for url in dict_url['sources']:
        if url['name'] == 'subs':
            url['options']['urls'] = alive
    #save  config.yaml
    with open(CONFIG_YAML, 'w',encoding="utf-8") as f:
        data = yaml.dump(dict_url, f,allow_unicode=True)

"""

    #收集alive
    alive = []
    if alive_yaml:
        print('alive_yaml----')
        for url in alive_yaml:
            alive.append(url['api'])
        if alive:
            print('alive----')
            #打开读取 config.yaml    
            with open(CONFIG_YAML,encoding="UTF-8") as f:
                dict_url = yaml.load(f, Loader=yaml.FullLoader)
            for url in dict_url['sources']:
                if url['name'] == 'subs':
                    url['options']['urls'] = alive
            #save  config.yaml
            with open(CONFIG_YAML, 'w',encoding="utf-8") as f:
                data = yaml.dump(dict_url, f,allow_unicode=True)
"""
