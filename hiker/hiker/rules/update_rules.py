#参考

# -*- coding: utf-8 -*-

import requests
import json
import re
import json5
import hashlib
import configparser		#https://blog.csdn.net/happyjacob/article/details/109346625
from datetime import datetime   #时间

list={
  'xyq':'https://raw.githubusercontent.com/xyq254245/HikerRule/main/hikermovie.json',
  'xyq_zyw':'https://raw.githubusercontent.com/xyq254245/HikerRule/main/ZYWCJ.txt',
  'yuanfen':'https://raw.githubusercontent.com/liuzaoyue/haikuo/master/share-home-rules.json',
  'xixifree':'https://raw.githubusercontent.com/xixifree/Hiker/main/ying.json'
  }

md5_addr = "md5.ini"


def saveConfig(customConfig,js_addr):#保存js文件
  
    if customConfig:
    # 配置customConfig及写入文件
        print('保存配置')
        file = open(js_addr, "w")
        file.write(customConfig)
        file.close()
        print('抓取时间：\t',datetime.now())

def getMd5(content):
    m = hashlib.md5()
    str_json = str(content)
    m.update(str_json.encode('utf-8'))
    md5 = m.hexdigest()
    return md5

def getUrlContent(url):  #获取网站的js内容，将获取的config返回
    headers={
    "User-Agent":"okhttp/3.15",
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
    }
    print(url)
    try:
        r=requests.get(url,headers=headers, timeout=5.0)
        if r.status_code==200:
            r.encoding='utf-8'    #编码方式
            return r.text
    except requests.exceptions.RequestException as e:  
        print(e)
        print('getUrlContent()功能中出现的错误！获取js内容失败，或者打开网址错误!')
  
def getConfigs(list):#获取列表网站的json内容，将获取的内容存入列表configList返回
    configList={}
    for key,value in list.items():
        config=getUrlContent(value)
        if config:
            configList[key]=config
    return configList

def save_xyq(url_content):
    #读取md5.ini
    config = configparser.ConfigParser()
    config.read(md5_addr)
    #获取新plugins.json的md5
    md5 = getMd5(url_content)
  
    #如果MD5不同，改成新的Md5和抓取时间,保存新js文件
    try:
        old_md5 = config.get("xyq_md5", "json")
        if md5 == old_md5:
            print("xyq.json file No update needed!")
        else:
            # Update md5.conf
            config.set("xyq_md5", "json", md5)
            config.set("xyq_md5", "time", str(datetime.now()))
            with open(md5_addr, "w") as f:
                config.write(f)       
            #保存js文件
            saveConfig(url_content,'./xyq/hikermovie.json')
    except Exception as e:
        print(e)
        print('修改md5,保存新文件时,出现错误了')
    #获取js数据
    url_content = getUrlContent('https://raw.githubusercontent.com/xyq254245/HikerRule/main/hikermovie.js')
    if url_content:
        md5 = getMd5(url_content)
        try:
            old_md5 = config.get("xyq_md5", "js")
            if md5 == old_md5:
                print("xyq.js file No update needed!")
            else:
                # Update md5.conf
                config.set("xyq_md5", "js", md5)
                config.set("xyq_md5", "time", str(datetime.now()))
                with open(md5_addr, "w") as f:
                    config.write(f)       
                #保存js文件
                saveConfig(url_content,'./xyq/hikermovie.js')
        except Exception as e:
            print(e)
            print('修改md5,保存新文件时,出现错误了')

def save_xyq_zyw(url_content):
    #读取md5.ini
    config = configparser.ConfigParser()
    config.read(md5_addr)
    #获取新plugins.json的md5
    md5 = getMd5(url_content)
  
    #如果MD5不同，改成新的Md5和抓取时间,保存新js文件
    try:
        old_md5 = config.get("xyq_zyw_md5", "txt")
        if md5 == old_md5:
            print("xyq_zyw.json file No update needed!")
        else:
            # Update md5.conf
            config.set("xyq_zyw_md5", "txt", md5)
            config.set("xyq_zyw_md5", "time", str(datetime.now()))
            with open(md5_addr, "w") as f:
                config.write(f)       
            #保存js文件
            saveConfig(url_content,'./xyq/ZYWCJ.txt')
    except Exception as e:
        print(e)
        print('修改md5,保存新文件时,出现错误了')
    #获取js数据
    url_content = getUrlContent('https://raw.githubusercontent.com/xyq254245/HikerRule/main/zywcj.js')
    if url_content:
        md5 = getMd5(url_content)
        try:
            old_md5 = config.get("xyq_zyw_md5", "js")
            if md5 == old_md5:
                print("xyq_zyw.js file No update needed!")
            else:
                # Update md5.conf
                config.set("xyq_zyw_md5", "js", md5)
                config.set("xyq_zyw_md5", "time", str(datetime.now()))
                with open(md5_addr, "w") as f:
                    config.write(f)       
                #保存js文件
                saveConfig(url_content,'./xyq/zywcj.js')
        except Exception as e:
            print(e)
            print('修改md5,保存新文件时,出现错误了')     
            
def save_yuanfen(url_content):
    #读取md5.ini
    config = configparser.ConfigParser()
    config.read(md5_addr)
    #获取新plugins.json的md5
    md5 = getMd5(url_content)
  
    #如果MD5不同，改成新的Md5和抓取时间,保存新js文件
    try:
        old_md5 = config.get("yuanfen_md5", "json")
        if md5 == old_md5:
            print("yuanfen.json file No update needed!")
        else:
            # Update md5.conf
            config.set("yuanfen_md5", "json", md5)
            config.set("yuanfen_md5", "time", str(datetime.now()))
            with open(md5_addr, "w") as f:
                config.write(f)       
            #保存js文件
            saveConfig(url_content,'./yuanfen/share-home-rules.json')
    except Exception as e:
        print(e)
        print('修改md5,保存新文件时,出现错误了')
    #获取js数据
    url_content = getUrlContent('http://hiker.nokia.press/hikerule/rulelist.json?id=4765&auth=b5f23689-2e58-5de1-965a-9fd798c4fc4f')
    if url_content:
        md5 = getMd5(url_content)
        try:
            old_md5 = config.get("yuanfen_md5", "js")
            if md5 == old_md5:
                print("yuanfen.js file No update needed!")
            else:
                # Update md5.conf
                config.set("yuanfen_md5", "js", md5)
                config.set("yuanfen_md5", "time", str(datetime.now()))
                with open(md5_addr, "w") as f:
                    config.write(f)       
                #保存js文件
                saveConfig(url_content,'./yuanfen/share-home-rules.js')
        except Exception as e:
            print(e)
            print('修改md5,保存新文件时,出现错误了')  
 
def save_xixifree(url_content):
    #读取md5.ini
    config = configparser.ConfigParser()
    config.read(md5_addr)
    #获取新plugins.json的md5
    md5 = getMd5(url_content)
  
    #如果MD5不同，改成新的Md5和抓取时间,保存新js文件
    try:
        old_md5 = config.get("xixifree_md5", "ying")
        if md5 == old_md5:
            print("xixifree_ying.json file No update needed!")
        else:
            # Update md5.conf
            config.set("xixifree_md5", "ying", md5)
            config.set("xixifree_md5", "time", str(datetime.now()))
            with open(md5_addr, "w") as f:
                config.write(f)       
            #保存js文件
            saveConfig(url_content,'./xixifree/ying.json')
    except Exception as e:
        print(e)
        print('修改md5,保存新文件时,出现错误了')
    #获取js数据
    url_content = getUrlContent('https://raw.githubusercontent.com/xixifree/Hiker/refs/heads/main/ting.json')
    if url_content:
        md5 = getMd5(url_content)
        try:
            old_md5 = config.get("xixifree_md5", "ting")
            if md5 == old_md5:
                print("xixifree_ting.json file No update needed!")
            else:
                # Update md5.conf
                config.set("xixifree_md5", "ting", md5)
                config.set("xixifree_md5", "time", str(datetime.now()))
                with open(md5_addr, "w") as f:
                    config.write(f)       
                #保存js文件
                saveConfig(url_content,'./xixifree/ting.json')
        except Exception as e:
            print(e)
            print('修改md5,保存新文件时,出现错误了')   
if "__name__==__main__":#主程序开始
    #获取最新数据
    configList=getConfigs(list)
    #更新xyq源
    try:
        save_xyq(configList['xyq'])
    except KeyError as e:
        print(str(e) + ' : KeyError_应该是网址变了，没获取到最新的数据,去找最新接口地址！')
        #写入错误日志
        file = open("log.txt", "a")
        file.write('\n' + str(datetime.now()) + ' : ' + str(e) + ' : KeyError_应该是网址变了，没获取到最新的数据,去找最新接口地址！')
        file.close()
    #更新xyq_资源网
    try:
        save_xyq_zyw(configList['xyq_zyw'])
    except KeyError as e:
        print(str(e) + ' : KeyError_应该是网址变了，没获取到最新的数据,去找最新接口地址！')
        #写入错误日志
        file = open("log.txt", "a")
        file.write('\n' + str(datetime.now()) + ' : ' + str(e) + ' : KeyError_应该是网址变了，没获取到最新的数据,去找最新接口地址！')
        file.close()
    #更新 缘分源
    try:
        save_yuanfen(configList['yuanfen'])
    except KeyError as e:
        print(str(e) + ' : KeyError_应该是网址变了，没获取到最新的数据,去找最新接口地址！')
        #写入错误日志
        file = open("log.txt", "a")
        file.write('\n' + str(datetime.now()) + ' : ' + str(e) + ' : KeyError_应该是网址变了，没获取到最新的数据,去找最新接口地址！')
        file.close()
    #更新 xixifree源
    try:
        save_xixifree(configList['xixifree'])
    except KeyError as e:
        print(str(e) + ' : KeyError_应该是网址变了，没获取到最新的数据,去找最新接口地址！')
        #写入错误日志
        file = open("log.txt", "a")
        file.write('\n' + str(datetime.now()) + ' : ' + str(e) + ' : KeyError_应该是网址变了，没获取到最新的数据,去找最新接口地址！')
        file.close()
