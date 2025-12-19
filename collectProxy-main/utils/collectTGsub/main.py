import re
import os
import yaml
import threading
import base64
import requests
from loguru import logger
from tqdm import tqdm
from retry import retry
from concurrent.futures import ThreadPoolExecutor, as_completed

#爬取源
TGconfigListPath = './utils/collectTGsub/config.yaml'
#输出位置
path_yaml = './utils/collectTGsub/TGsources.yaml'
node_output_path = './sub/sources/crawlTGnode.txt'

new_sub_list = []
new_clash_list = []
new_v2_list = []



@logger.catch
def yaml_check(path_yaml):
    print(os.path.isfile(path_yaml))
    if os.path.isfile(path_yaml): #存在，非第一次
        with open(path_yaml,encoding="UTF-8") as f:
            dict_url = yaml.load(f, Loader=yaml.FullLoader)
    else:
        dict_url = {
            "机场订阅":[],
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


def check_single_url(url):
    """检查单个订阅链接，返回是否处理完成（始终返回 True，便于 tqdm 更新）"""
    
    #暂时先关闭，需要调试的时候打开，查看哪个网址慢
    #logger.debug(f"正在检查: {url}")  # 关键：记录每个开始检查的 URL

    headers = {'User-Agent': 'ClashforWindows/0.18.1'}
    
    try:
        with requests.get(url, headers=headers, timeout=5) as res:
            if res.status_code == 200:
                try:  # 有流量信息
                    info = res.headers.get('subscription-userinfo')
                    if info:
                        info_num = re.findall(r'\d+', info)
                        if info_num:
                            upload = int(info_num[0])
                            download = int(info_num[1])
                            total = int(info_num[2])
                            unused = (total - upload - download) / 1024 / 1024 / 1024
                            unused_rounded = round(unused, 2)
                            if unused_rounded > 0:
                                new_sub_list.append(url)
                                # play_list.append('可用流量:' + str(unused_rounded) + ' GB                    ' + url)
                except Exception:
                    # 判断是否为 clash 配置
                    try:
                        if "proxies:" in res.text:
                            new_clash_list.append(url)
                    except Exception:
                        # 判断是否为 v2ray 订阅（base64）
                        try:
                            text = res.text[:64]
                            decoded = base64.b64decode(text).decode('utf-8', errors='ignore')
                            if filter_base64(decoded):
                                new_v2_list.append(url)
                        except Exception:
                            pass
            # else: 状态码不是 200，直接跳过
    except Exception as e:
        # 所有异常（超时、连接错误等）都捕获，不影响其他线程
        #暂时先关掉，需要调试查看时打开
        #logger.debug(f"检查失败（已跳过）: {url} ")
        pass
    
    return True  # 表示这个 URL 已处理完
    
def list_rm(urlList):  
    begin = 0
    length = len(urlList)
    print(f'\n-----去重开始-----\n')
    while begin < length:
        proxy_compared = urlList[begin]
        begin_2 = begin + 1
        while begin_2 <= (length - 1):
            if proxy_compared == urlList[begin_2] or 'https://t.me/' in urlList[begin_2] or 'http://t.me/' in urlList[begin_2] or 'telegram-cdn.org' in urlList[begin_2] or 'https://github.com' in urlList[begin_2] or 'dl5.cdnhost.lol' in urlList[begin_2]:
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
    # 使用 ThreadPoolExecutor，最大并发 16
    with ThreadPoolExecutor(max_workers=16) as executor:
        # 提交所有任务
        futures = [executor.submit(check_single_url, url) for url in url_list]
        # 使用 as_completed + tqdm 显示进度条
        for _ in tqdm(as_completed(futures), total=len(url_list), desc='订阅源筛选：'):
            pass  # 这里不需要 future.result()，因为异常已在函数内处理
    logger.info('筛选完成')
    
    #爬取订阅源
    old_sub_list = dict_url['机场订阅']
    #old_clash_list = dict_url['clash订阅']
    #old_v2_list = dict_url['v2订阅']
    new_sub_list.extend(old_sub_list)
    #new_clash_list.extend(old_clash_list)
    #new_v2_list.extend(old_v2_list)
    new_sub_list = list(set(new_sub_list))
    new_clash_list = list(set(new_clash_list))
    new_v2_list = list(set(new_v2_list))
    dict_url.update({'机场订阅':new_sub_list})
    dict_url.update({'clash订阅': new_clash_list})
    dict_url.update({'v2订阅': new_v2_list})
    with open(path_yaml, 'w',encoding="utf-8") as f:
        data = yaml.dump(dict_url, f,allow_unicode=True)
    logger.info('爬取订阅源写入文件结束---')
