import re, os
import shutil #copyfile() https://blog.csdn.net/Jerry_1126/article/details/86602517
from sub_convert import sub_convert

#源文件
airportListFile = './utils/mailCloud/getGoodSub/list.txt'
inputBasePath = './utils/mailCloud/trials/'
#输出订阅文件位置
outputBase64Sub_path =  './sub/g.txt'
outputClashSub_path = './sub/g.yaml' 

def write_file(file,content):
    f = open(file, 'w',encoding="UTF-8")
    f.write(content)
    f.close()
    
def get_list(listfile):
    file_list = open(listfile, 'r', encoding='utf-8')
    list_content = file_list.read()
    file_list.close()
    url_list = re.split(r'\n',list_content)
    return url_list

def list_to_node(airportList):
    allProxy = []
    for url in airportList:
        url = inputBasePath + url
        url = os.path.abspath(url)
        subContent =sub_convert.convert_remote(url,'url')
        allProxy.append(subContent)
    return allProxy
def urllist_to_sub(airportListFile):    #将url订阅列表内容转换成url,base64,clash文件保存
    airportList = get_list(airportListFile)
    allProxy = list_to_node(airportList)
    node = '\n'.join(allProxy) 
    #写入base64 订阅文件
    print('write base64 content!')
    subContent = sub_convert.base64_encode(node)
    write_file(outputBase64Sub_path,subContent)
    # 写入Clash 订阅文件
    print('write Clash content!')
    good_file_path = os.path.abspath(outputBase64Sub_path)
    content = sub_convert.convert_remote(good_file_path,'clash')
    write_file(outputClashSub_path,content)
  
if __name__ == '__main__':
    #good文件
    urllist_to_sub(airportListFile)
    #copy原文件
    shutil.copyfile('./utils/mailCloud/trial', './sub/v.txt')
    shutil.copyfile('./utils/mailCloud/trial.yaml', './sub/v.yaml')
