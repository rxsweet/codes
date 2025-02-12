import os
import yaml
import requests
import shutil
from clash import filter

#调用自己的模块，先获取执行的目录，再import文件
import sys
sys.path.append(".") #执行目录地址
from utils.subConvert import log

speedtestBakup_path = './speedtestBak.yaml'
outputClashSubErr_path = './sub/sources/err.yaml' 

config_yaml_path = './utils/clashspeedtest/config.yaml'

def init():
    if not os.path.exists('./temp'):
        os.mkdir('temp')

    # read from config file
    with open(config_yaml_path, 'r') as reader:
        config = yaml.load(reader, Loader=yaml.FullLoader)
        http_port = config['http-port']
        api_port = config['api-port']
        threads = config['threads']
        source = str(config['source'])
        timeout = config['timeout']
        testurl = config['test-url']
        outfile = config['outfile']
        
    # get clash config file
    if source.startswith('https://'):
        proxyconfig = yaml.load(requests.get(source).text, Loader=yaml.FullLoader)
    else:
        with open(source, 'r') as reader:
            try:
                proxyconfig = yaml.load(reader, Loader=yaml.FullLoader)
            except Exception as err:
                log.log(str(err))
                log.log_update_time(str(err),'./sub/err.txt') #设置错误输出位置，默认是日志log位置
                shutil.copy(source,outputClashSubErr_path)
                shutil.copy(speedtestBakup_path,source)
                with open(speedtestBakup_path, 'r') as reader:
                    proxyconfig = yaml.load(reader, Loader=yaml.FullLoader)
            
    # set clash api url
    baseurl = '127.0.0.1:' + str(api_port)
    apiurl = 'http://'+baseurl

    # filter config files
    proxyconfig = filter(proxyconfig)

    config = {'port': http_port, 'external-controller': baseurl, 'mode': 'global',
              'log-level': 'silent', 'proxies': proxyconfig['proxies']}

    with open('./temp/working.yaml', 'w') as file:
        file = yaml.dump(config, file)

    # return all variables
    return http_port, api_port, threads, source, timeout, outfile, proxyconfig, apiurl, testurl, config

def cleanup(clash):
    shutil.rmtree('./temp')
    clash.terminate()
    exit(0)
