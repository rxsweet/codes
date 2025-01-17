import re
import os
import yaml
import threading
import base64
import requests
from loguru import logger
from tqdm import tqdm
from retry import retry

#爬取源
TGconfigListPath = './config.yaml'
#输出位置
path_yaml = './TGsources.yaml'
node_output_path = './crawlTGnode.txt'

new_sub_list = []
new_clash_list = []
new_v2_list = []
new_info_list = []


@logger.catch
def yaml_check(path_yaml):
    print(os.path.isfile(path_yaml))
    if os.path.isfile(path_yaml): #存在，非第一次
        with open(path_yaml,encoding="UTF-8") as f:
            dict_url = yaml.load(f, Loader=yaml.FullLoader)
    else:
        dict_url = {
            "机场订阅":[],
            "机场信息":[],
            "clash订阅":[],
            "v2订阅":[]
        }
    with open(path_yaml, 'w',encoding="utf-8") as f:
        data = yaml.dump(dict_url, f,allow_unicode=True)
    logger.info('读取文件成功')
    return dict_url

@logger.catch
def get_config():
    with open(TGconfigListPath,encoding="UTF-8") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    list_tg = data['tgchannel']
    new_list = []
    for url in list_tg:
        a = url.split("/")[-1]
        url = 'https://t.me/s/'+a
        new_list.append(url)
    return new_list

@logger.catch
def get_channel_http(channel_url):
    try:
        with requests.post(channel_url) as resp:
            data = resp.text
        #爬取订阅源
        url_list = re.findall("https?://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]", data)  # 使用正则表达式查找订阅链接并创建列表
        #爬取节点
        result = data.encode('utf-8').decode('utf-8')
        crawlNodes = re.findall(r'ss://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]|ssr://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]|trojan://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]|vmess://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]',result)
        logger.info(channel_url+'\t获取成功')
    except Exception as e:
        logger.warning(channel_url+'\t获取失败')
        logger.error(channel_url+e)
        url_list = []
        crawlNodes = []
    finally:
        return url_list, crawlNodes
        

# @logger.catch
# def get_channel_http(channel_url):
#     headers = {
#         'Referer': 'https://t.me/s/wbnet',
#         'sec-ch-ua-mobile': '?0',
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
#     }
#     try:
#         with requests.post(channel_url,headers=headers) as resp:
#             data = resp.text
#         url_list = re.findall("https?://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]", data)  # 使用正则表达式查找订阅链接并创建列表
#         logger.info(channel_url+'\t获取成功')
#     except Exception as e:
#         logger.error('channel_url',e)
#         logger.warning(channel_url+'\t获取失败')
#         url_list = []
#     finally:
#         return url_list

def filter_base64(text):
    ss = ['ss://','ssr://','vmess://','trojan://']
    for i in ss:
        if i in text:
            return True
    return False


@logger.catch
def sub_check(url,bar):
    headers = {'User-Agent': 'ClashforWindows/0.18.1'}
    with thread_max_num:
        @retry(tries=2)
        def start_check(url):
            res=requests.get(url,headers=headers,timeout=5)#设置5秒超时防止卡死
            if res.status_code == 200:
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
                                liuliang_str = str((int(info_num[2])-int(info_num[1])-int(info_num[0]))/1024/1024/1024)
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
                                            print(url_yaml)
                                            new_info_list.append(url_yaml)
                                            new_sub_list.append(url)
                                    except Exception as e: 
                                        print('获取机场信息失败')
                                        print(e)
                                
                                #print(url+' 到期时间：' + date_str +' -- 剩余流量：' + liuliang_str)
                            else: # 已经过期
                                old_list.append(url)
                        else: # 没有时间信息
                            liuliang_str = str((int(info_num[2])-int(info_num[1])-int(info_num[0]))/1024/1024/1024)
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
                                        print(url_yaml)
                                        new_info_list.append(url_yaml)
                                        new_sub_list.append(url)
                                except Exception as e: 
                                    print('获取机场信息失败')
                                    print(e)
                            #print(url+' 到期时间：无 -- 剩余流量：'+ liuliang_str)
                except:
                    # 判断是否为clash
                    try:
                        u = re.findall('proxies:', res.text)[0]
                        if u == "proxies:":
                            new_clash_list.append(url)
                    except:
                        # 判断是否为v2
                        try:
                            # 解密base64
                            text = res.text[:64]
                            text = base64.b64decode(text)
                            text = str(text)
                            if filter_base64(text):
                                new_v2_list.append(url)
                        # 均不是则非订阅链接
                        except:
                            pass
            else:
                pass
        try:
            start_check(url)
        except:
            pass
        bar.update(1)

def list_rm(urlList):  
    begin = 0
    length = len(urlList)
    print(f'\n-----去重开始-----\n')
    while begin < length:
        proxy_compared = urlList[begin]
        begin_2 = begin + 1
        while begin_2 <= (length - 1):
            if proxy_compared == urlList[begin_2] or 'https://t.me/' in urlList[begin_2] or 'telegram-cdn.org' in urlList[begin_2]:
                urlList.pop(begin_2)
                length -= 1
            begin_2 += 1
        begin += 1
    print(f'\n-----去重结束-----\n')
    return urlList
if __name__=='__main__':

    dict_url = yaml_check(path_yaml)
    # print(dict_url)
    list_tg = get_config()
    logger.info('读取config成功')
    #循环获取频道订阅
    url_list = []
    node_list = []
    for channel_url in list_tg:
        temp_list,node_temp_list = get_channel_http(channel_url)
        url_list.extend(temp_list)
        node_list.extend(node_temp_list)
    #爬取节点
    logger.info('节点爬取结束---')
    subnodes = '\n'.join(node_list)
    subnodes = base64.b64encode(subnodes.encode('utf-8')).decode('ascii')
    f = open(node_output_path, 'w',encoding="UTF-8")
    f.write(subnodes)
    f.close()
    logger.info('爬取节点写入文件结束---')
	
    #列表去重和删除无用的网站
    list_rm(url_list)
	
    logger.info('开始筛选订阅源---')
    thread_max_num = threading.Semaphore(32)  # 32线程
    bar = tqdm(total=len(url_list), desc='订阅源筛选：')
    thread_list = []
    for url in url_list:
        # 为每个新URL创建线程
        t = threading.Thread(target=sub_check, args=(url, bar))
        # 加入线程池并启动
        thread_list.append(t)
        t.daemon=True
        t.start()
    for t in thread_list:
        t.join()
    bar.close()
    logger.info('筛选完成')
	
    #爬取订阅源
    old_sub_list = dict_url['机场订阅']
    old_clash_list = dict_url['clash订阅']
    old_v2_list = dict_url['v2订阅']
    old_info_list = dict_url['机场信息']
    new_sub_list.extend(old_sub_list)
    new_clash_list.extend(old_clash_list)
    new_v2_list.extend(old_v2_list)
    new_info_list.extend(old_info_list)
    new_sub_list = list(set(new_sub_list))
    new_clash_list = list(set(new_clash_list))
    new_v2_list = list(set(new_v2_list))
    #new_info_list = list(set(new_info_list))
    dict_url.update({'机场订阅':new_sub_list})
    dict_url.update({'clash订阅': new_clash_list})
    dict_url.update({'v2订阅': new_v2_list})
    dict_url.update({'机场信息': new_info_list})
    print(str(new_info_list))
    with open(path_yaml, 'w',encoding="utf-8") as f:
        data = yaml.dump(dict_url, f,allow_unicode=True)
    logger.info('爬取订阅源写入文件结束---')
    new_info_list = list(set(new_info_list))
    print(str(new_info_list))
