#!/usr/bin/env python3
#
#带参使用说明：./main.py './source.yaml' './output.yaml' 
#参数：1.测速源  2.输出clash文件位置  

import time
from multiprocessing import Process, Manager, Semaphore
from clash import push, checkenv, filter
from check import check
from tqdm import tqdm
from init import init, cleanup
import subprocess
#import outputsub
from datetime import datetime

import yaml

#cofig文件: config_file_path
config_file_path = './utils/clashspeedtest/config.yaml'

#def set_config(input_file_path, output_clash_Path, output_base64_path):  
    #3个参数：
    #input_file_path需要测速的文件位置, 
    #output_base64_path，输出文件是base64格式,
    #outputClashPath是clash格式
def set_config(input_file_path, output_clash_Path):  
    #打开config.yaml文件
    with open(config_file_path,encoding="UTF-8") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        f.close()
    config.update({'source' : input_file_path})
    config.update({'outfile' : output_clash_Path})
    #config.update({'outfile_base64' : output_base64_path})

    #将修改完成的config.yaml写入文件
    with open(config_file_path, 'w',encoding="utf-8") as f:
        data = yaml.dump(config, f,allow_unicode=True)
        

if __name__ == '__main__':
    #获取参数:如果带了参数
    import sys
    args = sys.argv
    #print(args)
    
    #匹配参数
    if len(args) == 3:  #2个参数
        #下载安装subconverter
        #args[0]是py文件名
        source = args[1]
        output_clash = args[2]
        set_config(input_file_path = source, output_clash_Path = output_clash)

    with Manager() as manager:
        alive = manager.list()
        http_port, api_port, threads, source, timeout, outfile, proxyconfig, apiurl, testurl, config= init()
        clashname, operating_system = checkenv()
        print('Running on '+ operating_system)
        clash = subprocess.Popen([clashname, '-f', './temp/working.yaml', '-d', '.'])
        processes =[]
        sema = Semaphore(threads)
        time.sleep(5)
        for i in tqdm(range(int(len(config['proxies']))), desc="Testing"):
            sema.acquire()
            p = Process(target=check, args=(alive,config['proxies'][i],apiurl,sema,timeout,testurl))
            p.start()
            processes.append(p)
        for p in processes:
            p.join
        time.sleep(5)
        alive=list(alive)
        #测速后，有可用节点再写入
        if int(len(alive)) > 0:
            print(f'alive node total = {len(alive)}')
            push(alive,outfile)
            #outputsub.output()
        else:
            print('speedtest done, ---> No alive node!')
            #记录错误,保存错误文件
            time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            filetime = '[' + time + ']: ' + 'speedtest done, ---> No alive node!' + '  file:' + source + '\n'
            # r只读，w可写，a追加
            file = open('./sub/log_clash.txt', 'a', encoding= 'utf-8')
            file.write(filetime)
            file.close()
