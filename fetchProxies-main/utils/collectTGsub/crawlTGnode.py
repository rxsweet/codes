import re
import os
import yaml
import requests
from tqdm import tqdm
#import base64
"""
import sys
sys.path.append(".") #执行目录地址
from utils.subConvert import ip_update
from utils.subConvert.sub_convert import sub_convert
from utils.subConvert import list_to_content
"""

#爬取源
TGconfigListPath = './utils/collectTGsub/config.yaml'
#输出位置
output_path = './sub/sources/crawTGnodeAll'

headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.53"}

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
    
"""
@logger.catch
def get_channel_http(channel_url):
    try:
        with requests.post(channel_url) as resp:
            data = resp.text
        url_list = re.findall("https?://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]", data)  # 使用正则表达式查找订阅链接并创建列表
        logger.info(channel_url+'\t获取成功')
    except Exception as e:
        logger.warning(channel_url+'\t获取失败')
        logger.error(channel_url+e)
        url_list = []
    finally:
        return url_list
def filter_base64(text):
    ss = ['ss://','ssr://','vmess://','trojan://']
    for i in ss:
        if i in text:
            return True
    return False
"""

def crawl_TG_node(channel_url,bar):
    resp = requests.get(channel_url,headers = headers)
    result = resp.text.encode('utf-8').decode('utf-8')
    #result = str(base64.b64decode(resp.text.encode('utf-8')))
    crawlNodes = re.findall(r'ss://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]|ssr://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]|trojan://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]|vmess://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]',result)
    bar.update(1)
    return crawlNodes

if __name__=='__main__':
    list_tg = get_config()
    #循环获取频道订阅
    url_list = []
    bar = tqdm(total=len(list_tg), desc='订阅内容获取：')
    for channel_url in list_tg:
        temp_list = crawl_TG_node(channel_url,bar)
        url_list.extend(temp_list)
    bar.close()    
    subnodes = '\n'.join(url_list)
    f = open(output_path, 'w',encoding="UTF-8")
    f.write(subnodes)
    f.close()
    """
    #去重
    allyaml = sub_convert.makeup(subnodes, dup_rm_enabled=True, format_name_enabled=False)
    # 写入YAML 文件
    print('write YAML file content!')
    #     if not os.path.exists(dirs):
    #         os.makedirs(dirs)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(allyaml)
        f.close()
    """
