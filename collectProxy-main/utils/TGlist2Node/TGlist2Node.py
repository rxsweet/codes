import re, os
from tqdm import tqdm   #进度条库
import threading  #线程

#调用自己的模块，先获取执行的目录，再import文件
import sys
sys.path.append(".") #执行目录地址
from utils.subConvert.sub_convert import sub_convert
from utils.subConvert import list_to_content

#源文件
source_sublist_path = './utils/collectTGsub/TGsources.yaml'
#爬取的TG分享的节点
crawlTGnodeAll = 'https://raw.githubusercontent.com/rxsweet/useProxies/main/sub/sources/crawlTGnode'

#输出订阅文件位置
outputAllyaml_path = './sub/sources/TGnodeAll.yaml'
#outputUrlSub_path = './sub/sources/TGsubUrl'
#outputBase64Sub_path =  './sub/sources/TGsubUrl64'


def get_sublist():
    new_url_list = []
    clashlist = list_to_content.get_yaml_list(source_sublist_path,'clash订阅')
    new_url_list.extend(clashlist)	#列表追加用extend
    v2list = list_to_content.get_yaml_list(source_sublist_path,'v2订阅')
    new_url_list.extend(v2list)
    return new_url_list


def urllist_to_sub(new_url_list):  #将url订阅列表内容转换成url,base64,clash文件保存

    allProxy = list_to_content.list_to_content(new_url_list)
    
    # 将列表内容，以行写入字符串？
    allProxy = '\n'.join(allProxy)
	
    #先格式化allProxy列表为YAML
    allyaml = sub_convert.format(allProxy)
    #去重
    if isinstance(allyaml, dict): #如果返回解析错误，不执行makeup
        allyaml = sub_convert.makeup(allyaml, dup_rm_enabled=True, format_name_enabled=False)
        
    # 写入YAML 文件
    print('write YAML file content!')
    list_to_content.write_file(outputAllyaml_path,allyaml)
"""   
    #获取allyaml_path文件路径
    good_file_path = os.path.abspath(outputAllyaml_path)

    # 写入url 订阅文件 
    print('write URL file content!')
    subContent = sub_convert.convert_remote(good_file_path,'url')
    list_to_content.write_file(outputUrlSub_path,subContent)

    # 写入base64 订阅文件
    print('write Base64 file content!')
    subContent = sub_convert.base64_encode(subContent)
    list_to_content.write_file(outputBase64Sub_path,subContent)
"""  

    
if __name__ == '__main__':
    new_url_list = get_sublist()
    new_url_list.append(crawlTGnodeAll)#爬取的TG分享的节点
    #sub_convert.geoip_update()
    urllist_to_sub(new_url_list)
