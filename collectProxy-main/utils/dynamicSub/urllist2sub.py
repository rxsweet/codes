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
urllistfile1 = './sub/sources/subList_dynamic.txt'

#输出订阅文件位置
outputAllyaml_path = './sub/sources/dynamicAll.yaml'
#outputUrlSub_path = './sub/sources/fetchShare'
#outputBase64Sub_path =  './sub/sources/fetchShare64'
#outputClashSub_path = './sub/sources/fetchShare.yaml'
speedtestBakup_path = './speedtestBak.yaml'
#code begin-----------------------------------------------------------------

def urllist_to_sub(urllist):  #将url订阅列表内容转换成url,base64,clash文件保存

    allProxy = list_to_content.list_to_content(urllist)
    
    # 将列表内容，以行写入字符串
    allProxy = '\n'.join(allProxy)
    allyaml = sub_convert.makeup(allProxy, dup_rm_enabled=True, format_name_enabled=False)
        
    # 写入YAML 文件
    print('write fetchShareYaml file content!')
    shutil.copy(outputAllyaml_path,speedtestBakup_path)
    list_to_content.write_file(outputAllyaml_path,allyaml)
"""    
    #获取allyaml_path文件路径
    good_file_path = os.path.abspath(outputAllyaml_path)

    # 写入url 订阅文件 
    print('write fetchShare file content!')
    subContent = sub_convert.convert_remote(good_file_path,'url')
    list_to_content.write_file(outputUrlSub_path,subContent)

    # 写入base64 订阅文件
    print('write fetchShare64 file content!')
    subContent = sub_convert.base64_encode(subContent)
    list_to_content.write_file(outputBase64Sub_path,subContent)
    
    # 写入Clash 订阅文件
    print('write fetchShareClash file content!')
    subContent = sub_convert.convert_remote(good_file_path,'clash')
    list_to_content.write_file(outputClashSub_path,subContent)
"""   

if __name__ == '__main__':
    ##更新IP库
    #ip_update.geoip_update()
    #读取列表
    urllist = list_to_content.get_sublist(urllistfile1)
    #转换
    urllist_to_sub(urllist)
"""	
    #网络获取
    res = requests.get('https://raw.githubusercontent.com/rxsweet/test/main/subList.txt', timeout=5)
    raw_content = res.text
    lines = lines + re.split(r'\n+',raw_content)
"""	


