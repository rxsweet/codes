import re, yaml
from tqdm import tqdm   #进度条库
import threading  #线程
import requests
from requests.adapters import HTTPAdapter

#调用自己的模块，先获取执行的目录，再import文件
import sys
sys.path.append(".") #执行目录地址
from utils.subConvert import ip_update
from utils.subConvert.sub_convert import sub_convert

#code begin------------------------------------------

def url_updated(url):                                   # 判断远程远程链接是否已经更新
    s = requests.Session()                              # 用requests.session()创建session对象，相当于创建了一个空的会话框，准备保持cookies。
    s.mount('http://', HTTPAdapter(max_retries=3))      # 重试次数为2
    s.mount('https://', HTTPAdapter(max_retries=3))     # 重试次数为2
    try:
        resp = s.get(url, timeout=10)                    # 超时时间为2s
        status = resp.status_code                       # 状态码赋值200？
    except Exception:
        status = 404
    if status == 200:
        url_updated = True
    else:
        url_updated = False
    return url_updated

#检测列表网站挂了没
#使用前先将字符串转列表：url_list = re.split(r'\n+',urllist_content)
def check_url(url_list):
    newlist = []
    for url in url_list:
        if url_updated(url):     # 判断url_updated 地址数据是否更新
            newlist.append(url)            #更新了，返回新地址new_url
    return newlist


#get YAML源文件里面的item列表,
#返回list文件。
#返回后的列表需  new_url_list = '\n'.join(new_url_list)  #将列表内容+'\n'变成字符串        
def get_yaml_list(yamlfile,item_name):
    with open(yamlfile,encoding="UTF-8") as f:
        yamldata = yaml.load(f, Loader=yaml.FullLoader)
    new_url_list = []
    url_list = yamldata[item_name]
    for url in url_list:
        new_url_list.append(url) 
    return new_url_list
    
#将新列表追加到listfile
def update_sublist(urllistfile,new_list):
    with open(listfile,'a',encoding="UTF-8") as fp:     # 打开写入文件
        fp.write(new_list)


#读取列表文件，返回列表格式，追加用extend()
def get_sublist(urllistfile):
    file_urllist = open(urllistfile, 'r', encoding='utf-8')
    urllist_content = file_urllist.read()
    file_urllist.close()
    url_list = re.split(r'\n',urllist_content)
    return url_list

#读取list文件,
#返回str字符串
#读取完成后需  url_list = re.split(r'\n+',urllist_content) #将字符串以'\n'切割为列表   
def read_listfile(urllistfile):
    file_urllist = open(urllistfile, 'r', encoding='utf-8')
    urllist_content = file_urllist.read()
    file_urllist.close()
    return urllist_content

#列表去重   
def list_rm(urlList):
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
    
# 写入文件
def write_file(file,content):
    f = open(file, 'w',encoding="UTF-8")
    f.write(content)
    f.close()
   
def get_sub_content(url,bar,allProxy):   #将url订阅内容append到allProxy列表，并完成进度bar
    if 'http' in url:
        subContent =sub_convert.convert_remote(url,'url')
        #判断是否解析错误
        if '解析错误' not in subContent:
            allProxy.append(subContent)
    bar.update(1)
    
#将url订阅列表转换成url节点列表
#需用 allProxies = '\n'.join(allProxies) # 将列表内容，以行写入字符串
def list_to_content(urlList):  

    allProxy = []
    #计算打印url总数
    lenlines =len(urlList)
    print('urlList total == '+str(lenlines)+'\n')
    
    #进度条添加
    bar = tqdm(total=lenlines, desc='订阅内容获取：')
    for line in urlList:
        get_sub_content(line,bar,allProxy)
    bar.close() #进度条结束
    
    return allProxy
    
if __name__ == '__main__':

    new_list = get_yaml_list(yamlfile,item_name)
    new_list = '\n'.join(new_list)  #将列表内容+'\n'变成字符串
    update_sublist(urllistfile,new_list)
    ip_update.geoip_update()
    urllistContent = read_listfile(urllistfile)
    urlList = re.split(r'\n+',urllistContent) #将字符串以'\n'切割为列表
    urlList = list_rm(urlList)
    write_file(urllistfile,urlList)
    allProxies = list_to_content(urlList)
    # 将列表内容，以行写入字符串
    allProxies = '\n'.join(allProxies)
