#!/usr/bin/env python3
import time
from multiprocessing import Process, Manager, Semaphore
from clash import push, checkenv, filter
from check import check
from tqdm import tqdm
from init import init, cleanup
import subprocess
import outputsub
from datetime import datetime

if __name__ == '__main__':
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
            print(f'ilive node total = {len(alive)}')
            push(alive,outfile)
            outputsub.output()
        else:
            print('speedtest done, ---> No alive node!')
            #记录错误,保存错误文件
            time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            filetime = '[' + time + ']: ' + 'speedtest done, ---> No alive node!' + '  file:' + source + '\n'
            # r只读，w可写，a追加
            file = open('./sub/log_clash.txt', 'a', encoding= 'utf-8')
            file.write(filetime)
            file.close()
