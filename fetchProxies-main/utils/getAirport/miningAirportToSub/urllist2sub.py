import re, os
from tqdm import tqdm   #进度条库
import threading  #线程

#调用自己的模块，先获取执行的目录，再import文件
import sys
sys.path.append(".") #执行目录地址
from utils.subConvert import ip_update
from utils.subConvert.sub_convert import sub_convert
from utils.subConvert import list_to_content

#源文件
urllistfile = './utils/getAirport/miningAirportToSub/sublist_mining'
#输出订阅文件位置
outputUrlSub_path = './sub/mining'
outputBase64Sub_path =  './sub/mining64'
outputClashSub_path = './sub/mining.yaml' 



def urllist_to_sub(urllistfile):  #将url订阅列表内容转换成url,base64,clash文件保存
    urllist_content = list_to_content.read_listfile(urllistfile)
    url_list = re.split(r'\n+',urllist_content)
    allProxy = list_to_content.list_to_content(url_list)
    
    # 将列表内容，以行写入字符串
    ownallProxy = '\n'.join(allProxy)   

    #开始写入文件
    # 写入url 订阅文件
    print('write miningUrl content!')
    list_to_content.write_file(outputUrlSub_path,ownallProxy)

    # 写入base64 订阅文件
    print('write miningUrl64 content!')
    subContent = sub_convert.base64_encode(ownallProxy)
    list_to_content.write_file(outputBase64Sub_path,subContent)

    # 写入Clash 订阅文件
    print('write miningClash content!')
    good_file_path = os.path.abspath(outputBase64Sub_path)
    print('mining_file_path =' + good_file_path)
    content = sub_convert.convert_remote(good_file_path,'clash')
    list_to_content.write_file(outputClashSub_path,content)
  
if __name__ == '__main__':
    ip_update.geoip_update()
    urllist_to_sub(urllistfile)
