import re, os
from tqdm import tqdm   #进度条库
import threading  #线程

#调用自己的模块，先获取执行的目录，再import文件
import sys
sys.path.append(".") #执行目录地址
#from utils.subConvert import ip_update
from utils.subConvert.sub_convert import sub_convert
from utils.subConvert import list_to_content

#源文件
urllistfile = './sub/sources/sublist_free.txt'
#输出订阅文件位置
#outputUrlSub_path = './sub/free'
outputBase64Sub_path =  './sub/free64.txt'
outputClashSub_path = './sub/free.yaml' 

# 有优质free添加至sub_to_url功能模块里if处

#code begin
   
def good_url(url,allProxy):   #将url订阅内容append到allProxy列表，并完成进度bar
    #if 'www.dgycom.com' in url or 'www.iacgbt.com' in url:	#优质free收集，有新goodfree添加至此
    subContent =sub_convert.convert_remote(url,'url')    
    allProxy.append(subContent)    

    
def urllist_to_sub(urllistfile):  #将url订阅列表内容转换成url,base64,clash文件保存
    # 下载最新sublist源
    urllist_content = list_to_content.read_listfile(urllistfile)
    url_list = re.split(r'\n+',urllist_content)
    
    allProxy = []
    
    #得到good free
    for url in url_list:
        good_url(url,allProxy)    
    
    # 将列表内容，以行写入字符串
    ownallProxy = '\n'.join(allProxy)   

    #写入base64 订阅文件
    print('write base64 content!')
    subContent = sub_convert.base64_encode(ownallProxy)
    list_to_content.write_file(outputBase64Sub_path,subContent)

    # 写入Clash 订阅文件
    print('write Clash content!')
    good_file_path = os.path.abspath(outputBase64Sub_path)
    content = sub_convert.convert_remote(good_file_path,'clash')
    list_to_content.write_file(outputClashSub_path,content)
  
if __name__ == '__main__':
    #ip_update.geoip_update()
    urllist_to_sub(urllistfile)


"""
    #开始写入文件
    # 写入url 订阅文件
    print('write Url content!')
    list_to_content.write_file(outputUrlSub_path,ownallProxy)
"""
