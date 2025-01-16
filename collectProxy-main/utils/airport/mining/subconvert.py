#subconvert使用方法：python subconvert.py './subs/11.yaml' 'clash' './subs/22.yaml'
#转换 type: clash base64 url YAML
#####################################
#rm 使用方法：python subconvert.py './subs/11.yaml' 'rm'
#
#
import os
import requests
import urllib.parse
from datetime import datetime
import time
import yaml


#默认转clash配置文件.ini地址
INI_CONFIG = 'https://raw.githubusercontent.com/rxsweet/all/main/githubTools/clashConfig.ini'


def proxies_rm(proxies_list):
    # 去重复，重名，空名，float型password
    raw_length = len(proxies_list)
    length = len(proxies_list)
    begin = 0
    rm = 0
    name_none = 0
    passErr = 0
    print(f'proxies: 列表去重')
    while begin < length:
        if (begin + 1) == 1:
            print(f'\n-----去重开始-----\n起始数量{length}')
        elif (begin + 1) % 100 == 0:
            print(f'当前基准{begin + 1}-----当前数量{length}')
        elif (begin + 1) == length and (begin + 1) % 100 != 0:
            repetition = raw_length - length - passErr
            print(f'当前基准{begin + 1}-----当前数量{length}\n--------\n重复数量{repetition}\n重名数量{rm}\n空名数{name_none}\nfloat型password数量{passErr}\n-----去重完成-----\n')
        if proxies_list[begin]['name'] == None or proxies_list[begin]['name'] == '' or proxies_list[begin]['name'] == ' ':
            proxies_list[begin]['name'] = 'name-None' + '-' + proxies_list[begin]['type'] + '+' +  str(name_none)
            name_none += 1
        begin_2 = begin + 1
        name_same = 0
        while begin_2 <= (length - 1):
            if proxies_list[begin]['server'] == proxies_list[begin_2]['server'] and proxies_list[begin]['port'] == proxies_list[begin_2]['port']:
                if 'password' in proxies_list[begin] and 'password' in proxies_list[begin_2]:
                    if proxies_list[begin]['password'] == proxies_list[begin_2]['password']:
                        proxies_list.pop(begin_2)
                        length -= 1
                        begin_2 -= 1
                if 'uuid' in proxies_list[begin] and 'uuid' in proxies_list[begin_2]:
                    if proxies_list[begin]['uuid'] == proxies_list[begin_2]['uuid']:
                        proxies_list.pop(begin_2)
                        length -= 1
                        begin_2 -= 1
            else:
                if proxies_list[begin]['name'] == proxies_list[begin_2]['name']:
                    name_same += 1
                    proxies_list[begin_2]['name'] = str(proxies_list[begin_2]['name']) + '+' + str(name_same)
            begin_2 += 1
        #if name_same > 0:
            #print(f"{proxies_list[begin]['name']} 重名数量：{name_same}")
        rm += name_same
        #删除空密码和password为float型的节点
        if proxies_list[begin]['type'] == 'ss' or proxies_list[begin]['type'] == 'trojan' or proxies_list[begin]['type'] == 'ssr':  
            try:
                if proxies_list[begin]['password'] == None or proxies_list[begin]['password'] == '':    #空密码
                    print(f"{proxies_list[begin]['name']}的password为空！")
                    #print(proxies_list[begin])
                    proxies_list.pop(begin)
                    length -= 1
                    begin -= 1
                else:
                    try:  # 如果能运行float(s)语句，返回True（字符串s是浮点数）
                        float(proxies_list[begin]['password'])
                        #print(f"{proxies_list[begin]['name']}的password为float型！")
                        proxies_list.pop(begin)
                        length -= 1
                        begin -= 1
                    except ValueError:  # ValueError为Python的一种标准异常，表示"传入无效的参数"
                        pass
            except:
                proxies_list.pop(begin)
                length -= 1
                begin -= 1
        begin += 1 
    print(f'去重后剩余总数:{len(proxies_list)}')
    return proxies_list
    
def YAML_rm(source):
    #读取yaml文件
    with open(source, 'r',encoding = 'utf-8') as f:
        try:
            proxyconfig = yaml.load(f.read(), Loader=yaml.FullLoader)
        except Exception as err:
            print(f"读取{source}文件失败")
    #去重
    proxyconfig['proxies'] = proxies_rm(proxyconfig['proxies'])
    #写入
    with open(source, 'w',encoding = 'utf-8') as file:
        #file = yaml.dump(proxyconfig, file,default_flow_style=False, sort_keys=False, allow_unicode=True, width=750, indent=2)
        file = yaml.dump(proxyconfig, file, allow_unicode=True, indent=2)
    #下载安装subconverter
    subconverter_install()
    time.sleep(3)
    sub_convert(source,'YAML',source)
# 注意 订阅地址必须是base64,或者yaml，(直接是url节点内容的话，会解析错误)
def convert_remote(url='', output_type='clash',configUrl = INI_CONFIG):
    #url='源', 
    #output_type={'clash': 输出可以订阅的Clash配置, 'base64': 输出 Base64 配置, 'url': 输出 url 配置, 'YAML': 输出 YAML 配置}, 
    #host='http://127.0.0.1:25500'
    #sever_host = host
    sever_host = 'http://127.0.0.1:25500'
    url = urllib.parse.quote(url, safe='') # https://docs.python.org/zh-cn/3/library/urllib.parse.html
    if output_type == 'clash':
        converted_url = sever_host+'/sub?target=clash&url='+url+'&insert=false&config='+configUrl+'&emoji=false'
        try:
            resp = requests.get(converted_url)
            #print(resp)
        except Exception as err:
            print(err)
            return 'Url 解析错误'
        if resp.text == 'No nodes were found!':
            sub_content = 'Url 解析错误'
            print('Url 解析错误: No nodes were found! -->' + url + '\n')
        else:
            sub_content = resp.text
    elif output_type == 'base64':
        converted_url = sever_host+'/sub?target=mixed&url='+url+'&insert=false&emoji=false'
        try:
            resp = requests.get(converted_url)
        except Exception as err:
            print(err)
            return 'Url 解析错误'
        if resp.text == 'No nodes were found!':
            sub_content = 'Url 解析错误'
            print('Url 解析错误: No nodes were found! -->' + url + '\n')
        else:
            sub_content = resp.text
    elif output_type == 'url':
        converted_url = sever_host+'/sub?target=mixed&url='+url+'&insert=false&emoji=false&list=true'
        try:
            resp = requests.get(converted_url)
        except Exception as err:
            print(err)
            return 'Url 解析错误'
        if resp.text == 'No nodes were found!':
            sub_content = 'Url 解析错误'
            print('Url 解析错误: No nodes were found! -->' + url + '\n')
        else:
            sub_content = resp.text
    elif output_type == 'YAML':
        converted_url = sever_host+'/sub?target=clash&url='+url+'&insert=false&emoji=false&list=true'
        try:
            resp = requests.get(converted_url)
        except Exception as err:
            print(err)
            return 'Url 解析错误'
        if resp.text == 'No nodes were found!':
            sub_content = 'Url 解析错误'
            print('Url 解析错误: No nodes were found! -->' + url + '\n')
        else:
            sub_content = resp.text
    return sub_content

#源文件转到目标文件，类型为output_type，共4个类型：clash,base64,url,YAML
def sub_convert(source,output_type,output):

    time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    print(f'[{time}]: subconvert [{output_type}]- [{source}] to [{output}]')
    #获取文件绝对路径
    source_path = os.path.abspath(source)
    temp = convert_remote(source_path,output_type)
    with open(output, 'w') as f:
        f.write(temp)

#下载subconverter
def subconverter_install():    
    try:
        #os.system()
        if not os.path.exists('./subconverter.tar.gz'):
            os.system("wget -O subconverter.tar.gz https://github.com/tindy2013/subconverter/releases/latest/download/subconverter_linux64.tar.gz")
            #os.system("wget -O subconverter.tar.gz https://github.com/lonelam/subconverter/releases/latest/download/subconverter_linux64.tar.gz")    #支持hy2
            os.system("tar -zxf subconverter.tar.gz -C ./")
            os.system("chmod +x ./subconverter/subconverter && nohup ./subconverter/subconverter >./subconverter.log 2>&1 &")
            print('=subconverter已经启动=')
        #if config_url and (config_cover or not os.path.exists(config_path)):
            #download(config_url, config_path)#下载config.yaml（实际就是节点文件）
        #os.system("docker run -d --restart always -p 25500:25500 tindy2013/subconverter")
        #else:
            #print('======subconverter已经下载过了，不用重复下载！======')
    except Exception as err:
        print(err)
        print('subconverter安装失败')
        

if __name__=='__main__':
    #获取参数携带的参数

    import sys
    args = sys.argv
    #print(args)

    if len(args) == 4:
        #下载安装subconverter
        subconverter_install()
        time.sleep(3)
        #args[0]是py文件名
        source = args[1]
        output_type = args[2]
        output = args[3]
        sub_convert(source,output_type,output)
    if len(args) == 3:
        source = args[1]
        act = args[2]
        if act == 'rm':
            YAML_rm(source)
    
