import re
import time
import requests
import threading
from tqdm import tqdm
from retry import retry
from datetime import datetime
import math
#调用自己的模块，先获取执行的目录，再import文件
import sys
sys.path.append(".") #执行目录地址
from utils.subConvert import list_to_content

#mining源文件
source_sublist_path = './utils/collectTGsub/TGsources.yaml'

#check列表的位置
urllist_path = './sub/sources/sublist_mining.txt'

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


def list_rm(url_list):  #列表去重
    begin = 0
    length = len(url_list)
    print(f'\n-----去重开始-----\n')
    while begin < length:
        proxy_compared = url_list[begin]
        begin_2 = begin + 1
        while begin_2 <= (length - 1):
            if proxy_compared == url_list[begin_2]:
                url_list.pop(begin_2)
                length -= 1
            begin_2 += 1
        begin += 1
    print(f'\n-----去重结束-----\n')
    return url_list
    
def sub_check(url,bar):
    headers = {'User-Agent': 'ClashforWindows/0.18.1'}
    with thread_max_num:
        @retry(tries=3)
        def start_check(url):
            res=requests.get(url,headers=headers,timeout=5)#设置5秒超时防止卡死
            if res.status_code == 200:
                try: #有流量信息
                    info = res.headers['subscription-userinfo']
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
                                #date_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(usetime))
                                date_str = time.strftime('%Y-%m-%d', time.localtime(usetime))
                                liuliang_str = pybyte(int(info_num[2])-int(info_num[1])-int(info_num[0]))
                                new_list.append('到期时间：' + date_str +' -- 剩余流量：' + liuliang_str)
                                new_list.append(url)
                                print(url+' 到期时间：' + date_str +' -- 剩余流量：' + liuliang_str)
                            else: # 已经过期
                                old_list.append(url)
                        else: # 没有时间信息
                            liuliang_str = pybyte(int(info_num[2])-int(info_num[1])-int(info_num[0]))
                            new_list.append('到期时间：无 -- 剩余流量：'+ liuliang_str)
                            new_list.append(url)
                            print(url+' 到期时间：无 -- 剩余流量：'+ liuliang_str)
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

if __name__=='__main__':
    new_list = []
    #old_list = []
    #添加更新时间
    currentTime = datetime.now().strftime("%Y-%m-%d\t%H:%M:%S")
    new_list.append('更新时间:\t'+currentTime+'\n')
    
    yaml_list = list_to_content.get_yaml_list(source_sublist_path,'机场订阅')
    urllist_content = list_to_content.read_listfile(urllist_path)
    url_list = re.split(r'\n+',urllist_content)
    url_list.extend(yaml_list)
    url_list=list_to_content.list_rm(url_list)    # 去重
    # url_list = data.split() :list
    thread_max_num =threading.Semaphore(32) #32线程
    bar = tqdm(total=len(url_list), desc='订阅筛选：')
    thread_list = []
    for url in url_list:
        #为每个新URL创建线程
        t = threading.Thread(target=sub_check, args=(url,bar))
        #加入线程池并启动
        thread_list.append(t)
        t.daemon=True
        t.start()
    for t in thread_list:
        t.join()
    bar.close()
    with open(urllist_path,"w+") as f:
        # str = '\n'
        # f.write(str.join(list))
        for url in new_list:
            f.write(url+'\n')
     
"""         
    with open("./logs/old/old","a") as f:
        for url in old_list:
            f.write(url+'\n')
    with open("./logs/old/time","w",encoding="UTF-8") as f:
        currentTime = datetime.now().strftime("%Y-%m-%d\t%H:%M:%S")
        f.write('更新时间:\t'+currentTime+'\n')
 """          
