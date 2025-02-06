#subconvert.py
#功能:[获取cofig列表节点，去重，转换]
#1.获取cofig.yaml列表节点：python subconvert.py './config.yaml' 'config'
#2.去重：python subconvert.py './sources.yaml' 'rm'
#3.转换：python subconvert.py './subs/11.yaml' 'clash' './subs/22.yaml'    ##type: clash base64 url YAML

import os
import re
import requests
import urllib.parse
from datetime import datetime
import time
import yaml


#默认转clash配置文件.ini地址
INI_CONFIG = 'https://raw.githubusercontent.com/rxsweet/all/main/githubTools/clashConfig.ini'

#记录错误,出错时，错误文件有默认地址
def log_err(msg,log_path = './sub/err.txt'):
    time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    filetime = '[' + time + ']: ' + msg + '\n'
    # r只读，w可写，a追加

    file = open(log_path, 'a', encoding= 'utf-8')
    file.write(filetime)
    file.close()

#获取cofig.yaml列表节点,出错时，错误文件有默认地址
#def collect_sub(source,ERR_PATH = './sub/sources/err.yaml'):#暂时不需要将错误内容写入文件,只记录错误信息
def collect_sub(source):
    print(f'collect {source} begin:')
    #读取yaml文件
    with open(source, 'r',encoding = 'utf-8') as f:
        try:
            config = yaml.load(f.read(), Loader=yaml.FullLoader)
        except Exception as err:
            print(f"读取{source}文件失败")
    if len(config['sources']) > 0:
        i = 0
        while i < len(config['sources']):
            #获取订阅转成yaml
            if config['sources'][i]['options']['urls']:
                #下载安装subconverter
                subconverter_install()
                time.sleep(3)
                #转成subconverter可识别的字符串
                urllist = '|'.join(config['sources'][i]['options']['urls']) 
                temp = convert_remote(urllist,'YAML')
                try:
                    yaml_list = yaml.safe_load(temp)
                except yaml.YAMLError as exc:
                    print('----------出现错误,下面是错误提示：----------\n')
                    print(exc)
                    print('----------上面是错误提示内容!----------------\n')
                    print(f'sweetrx: subconvert.py  collect_sub中yaml.safe_load解析返回的tamp值时，出错了！尝试重新单url解析！')
                    yaml_list = {'proxies':[]}
                    for url in config['sources'][i]['options']['urls']:
                        try:
                            temp = convert_remote(url,'YAML')
                            url_yaml_list = yaml.safe_load(temp)
                            yaml_list['proxies'].extend(url_yaml_list['proxies'])
                        except:
                            print(f"{url} 解析出错！")
                            #记录错误,保存错误文件
                            log_err(f' 源文件{source}中，{url}\n{str(exc)}')
                            #将得到的错误内容写入文件，暂时不需要
                            #print(f'错误文件保存至{ERR_PATH}')
                            #with open(ERR_PATH, 'w') as f:
                                #f.write(temp)
                if 'proxies' not in yaml_list and len(yaml_list['proxies']) > 0:
                    continue
                yaml_list['proxies'] = proxies_rm(yaml_list['proxies'])
                
                #写入,配置文件的写入地址config['sources'][i]['output']
                with open(config['sources'][i]['output'], 'w',encoding = 'utf-8') as file:
                    file = yaml.dump(yaml_list, file, allow_unicode=True, indent=2)
                #调整显示方式
                sub_convert(config['sources'][i]['output'],'YAML',config['sources'][i]['output'])
            i = i+1
    else:
        print(f"sweetrx: subconvert.py，collect_sub()中config.yaml no url！")
#dict列表去重
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
                    #print(f"{proxies_list[begin]['name']}的password为空！")
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
        #出现的错误：TLS must be true with h2/grpc network
        try:
            if 'network' in proxies_list[begin]:
                if proxies_list[begin]['network'] == 'grpc' or proxies_list[begin]['network'] == 'h2':  
                    if 'tls' not in proxies_list[begin] or proxies_list[begin]['tls'] != True:    #
                        #print(proxies_list[begin])
                        proxies_list.pop(begin)
                        length -= 1
                        begin -= 1
        except:
            pass
        begin += 1 
    print(f'去重后剩余总数:{len(proxies_list)}')
    return proxies_list

#去重
def YAML_rm(source):
    #读取yaml文件
    with open(source, 'r',encoding = 'utf-8') as f:
        try:
            proxyconfig = yaml.load(f.read(), Loader=yaml.FullLoader)
        except Exception as err:
            print(f"读取{source}文件失败")
            return
    #列表去重
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
            print('Url 解析错误: No nodes were found! -->' + url)
        else:
            sub_content = resp.text
            sub_content = re.sub(r'!<str>','',sub_content)#https://blog.csdn.net/Dontla/article/details/134602233
    elif output_type == 'base64':
        converted_url = sever_host+'/sub?target=mixed&url='+url+'&insert=false&emoji=false'
        try:
            resp = requests.get(converted_url)
        except Exception as err:
            print(err)
            return 'Url 解析错误'
        if resp.text == 'No nodes were found!':
            sub_content = 'Url 解析错误'
            print('Url 解析错误: No nodes were found! -->' + url)
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
            print('Url 解析错误: No nodes were found! -->' + url)
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
            print('Url 解析错误: No nodes were found! -->' + url)
        else:
            sub_content = resp.text
            sub_content = re.sub(r'!<str>','',sub_content)#https://blog.csdn.net/Dontla/article/details/134602233
    return sub_content

#源文件转到目标文件，类型为output_type，共4个类型：clash,base64,url,YAML
def sub_convert(source,output_type,output):

    time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    print(f'[{time}]: subconvert [{output_type}]- [{source}] to [{output}]')
    #获取文件绝对路径
    source_url = os.path.abspath(source)
    temp = convert_remote(source_url,output_type)
    with open(output, 'w') as f:
        f.write(temp)

#下载subconverter
def subconverter_install():    
    try:
        #os.system()
        if not os.path.exists('./subconverter.tar.gz'):
            r=requests.get('https://github.com/lonelam/subconverter/releases/latest/download/subconverter_linux64.tar.gz')
            if r.status_code==200:
                os.system("wget -q -O subconverter.tar.gz https://github.com/lonelam/subconverter/releases/latest/download/subconverter_linux64.tar.gz")    #支持hy2
            else:
                os.system("wget -q -O subconverter.tar.gz https://github.com/tindy2013/subconverter/releases/latest/download/subconverter_linux64.tar.gz")  #-q安静模式(没有输出)
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
    
    #匹配参数
    if len(args) == 4:  #3个参数
        #下载安装subconverter
        subconverter_install()
        time.sleep(3)
        #args[0]是py文件名
        source = args[1]
        output_type = args[2]
        output = args[3]
        sub_convert(source,output_type,output)
    if len(args) == 3:  #2个参数
        source = args[1]
        act = args[2]
        if act == 'rm': #匹配去重
            YAML_rm(source)
        elif act == 'config':   #匹配config文件
            collect_sub(source)
