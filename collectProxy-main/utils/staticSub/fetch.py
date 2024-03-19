import re, os
import shutil
#调用自己的模块，先获取执行的目录，再import文件
import sys
sys.path.append(".") #执行目录地址
#from utils.subConvert import ip_update
from utils.subConvert.sub_convert import sub_convert
from utils.subConvert import list_to_content

#源文件
urllistfile = './utils/staticSub/sublist'
#输出订阅文件位置

outputClashSub_path = './sub/sources/staticAll.yaml' 
speedtestBakup_path = './speedtestBak.yaml'

def urllist_to_sub(goodurl):

    allProxy = list_to_content.list_to_content(goodurl)
    
    # 将列表内容，以行写入字符串
    ownallProxy = '\n'.join(allProxy)   
    content = sub_convert.makeup(ownallProxy, dup_rm_enabled=True, format_name_enabled=False)
    #开始写入文件
    # 写入Clash 订阅文件
    shutil.copy(outputClashSub_path,speedtestBakup_path)
    print('write staticClash content!')
    list_to_content.write_file(outputClashSub_path,content)
  
if __name__ == '__main__':
    #ip_update.geoip_update()
    urllist_content = list_to_content.read_listfile(urllistfile)
    url_list = re.split(r'\n+',urllist_content)
#    goodurl = list_to_content.check_url(url_list)
#    x = '\n'.join(goodurl)
#    list_to_content.write_file(urllistfile,x)
#    urllist_to_sub(goodurl)
    urllist_to_sub(url_list)
