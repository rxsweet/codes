import re, os
from tqdm import tqdm   #进度条库
import threading  #线程
import shutil   #speedtest备份用的拷贝库

#调用自己的模块，先获取执行的目录，再import文件
import sys
sys.path.append(".") #执行目录地址
#from utils.subConvert import ip_update
from utils.subConvert.sub_convert import sub_convert
from utils.subConvert import list_to_content

#源文件
urllistfile = './sub/sources/sublist_mining.txt'
#输出订阅文件位置
outputClashSub_path = './sub/sources/miningAll.yaml'
speedtestBakup_path = './speedtestBak.yaml'



def urllist_to_sub(urllistfile):  #将url订阅列表内容转换成url,base64,clash文件保存
    urllist_content = list_to_content.read_listfile(urllistfile)
    url_list = re.split(r'\n+',urllist_content)
    #追加TG爬取的节点文件地址
    url_list.append('https://rxsub.eu.org/sub/sources/crawlTGnode.txt')
    #将url列表转为节点
    allProxy = list_to_content.list_to_content(url_list)
    
    #读取TG爬取的节点, 添加到测速源
    #tg_node = list_to_content.read_listfile('./sub/sources/crawlTGnode.txt')
    #allProxy.append(tg_node)
    
    # 将列表内容，以行写入字符串
    ownallProxy = '\n'.join(allProxy)   
    
    content = sub_convert.makeup(ownallProxy, dup_rm_enabled=True, format_name_enabled=False)
    #开始写入文件
    # 写入Clash 订阅文件
    print('write miningClash content!')
    shutil.copy(outputClashSub_path,speedtestBakup_path)
    list_to_content.write_file(outputClashSub_path,content)
  
if __name__ == '__main__':
    #ip_update.geoip_update()
    urllist_to_sub(urllistfile)
