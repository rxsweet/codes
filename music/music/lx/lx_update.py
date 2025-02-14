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
  'Huibq':'https://raw.githubusercontent.com/Huibq/keep-alive/master/render_api.js',
  'ikun0014':'https://lxmusic.ikunshare.com/script',
  'fish':'https://m-api.ceseet.me/script',
  'MusicDownloader':'https://ikun.laoguantx.top:19742/script?key=LXMusic_dmsowplaeq',
  }

md5_addr = "md5.ini"
#Huibq
Huibq_js_addr = './Huibq.js'
ikun0014_js_addr = './ikun0014.js'
fish_js_addr = './fish.js'
MusicDownloader_js_addr = 'MusicDownloader.js'
def saveConfig(customConfig,js_addr):#保存js文件
  
    if customConfig:
    # 配置customConfig及写入文件
        print('保存配置')
        file = open(js_addr, "w")
        file.write(customConfig)
        file.close()
        print('抓取时间：\t',datetime.now())

def getMd5(js_content):
    m = hashlib.md5()
    str_json = str(js_content)
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
        return None
  
def getConfigs(list):#获取列表网站的json内容，将获取的内容存入列表configList返回
    configList={}
    for key,value in list.items():
        config=getUrlContent(value)
        configList[key]=config
    return configList

def diy_Huibq(js_content):
    print('hello,Huibq大佬! diy_Huibq()开始')
    if js_content == None:
        print('Huibq' + ' : KeyError_应该是网址变了，没获取到最新的js数据,去找最新接口地址！')
        #写入错误日志
        file = open("log.txt", "a")
        file.write('\n' + str(datetime.now()) + ' : ' + 'Huibq' + ' : KeyError_应该是网址变了，没获取到最新的js数据,去找最新接口地址！')
        file.close()
        return
    #读取md5.ini
    config = configparser.ConfigParser()
    config.read(md5_addr)
    #获取新plugins.json的md5
    md5 = getMd5(js_content)
  
    #如果MD5不同，改成新的Md5和抓取时间,保存新js文件
    try:
        old_md5 = config.get("Huibq_md5", "js")
        if md5 == old_md5:
            print("Huibq.js file No update needed!")
        else:
            # Update md5.conf
            config.set("Huibq_md5", "js", md5)
            config.set("Huibq_md5", "time", str(datetime.now()))
            with open(md5_addr, "w") as f:
                config.write(f)       
            #保存js文件
            saveConfig(js_content,Huibq_js_addr)
    except Exception as e:
        print(e)
        print('修改md5,保存新js文件时,出现错误了')


def diy_ikun0014(js_content):
    print('hello,ikun0014大佬! diy_ikun0014()开始')
    if js_content == None:
        print('ikun0014' + ' : KeyError_应该是网址变了，没获取到最新的js数据,去找最新接口地址！')
        """
        #因ikun0014网站停用，暂时先关闭写入错误
        #写入错误日志
        file = open("log.txt", "a")
        file.write('\n' + str(datetime.now()) + ' : ' + 'ikun0014' + ' : KeyError_应该是网址变了，没获取到最新的js数据,去找最新接口地址！')
        file.close()
        """
        return
    #读取md5.ini
    config = configparser.ConfigParser()
    config.read(md5_addr)
    #获取新plugins.json的md5
    md5 = getMd5(js_content)
  
    #如果MD5不同，改成新的Md5和抓取时间,保存新js文件
    try:
        old_md5 = config.get("ikun0014_md5", "js")
        if md5 == old_md5:
            print("ikun0014.js file No update needed!")
        else:
            # Update md5.conf
            config.set("ikun0014_md5", "js", md5)
            config.set("ikun0014_md5", "time", str(datetime.now()))
            with open(md5_addr, "w") as f:
                config.write(f)       
            #保存js文件
            saveConfig(js_content,ikun0014_js_addr)
    except Exception as e:
        print(e)
        print('修改md5,保存新js文件时,出现错误了')

def diy_fish(js_content):
    print('hello,fish大佬! diy_fish()开始')
    if js_content == None:
        print('fish' + ' : KeyError_应该是网址变了，没获取到最新的js数据,去找最新接口地址！')
        #写入错误日志
        file = open("log.txt", "a")
        file.write('\n' + str(datetime.now()) + ' : ' + 'fish' + ' : KeyError_应该是网址变了，没获取到最新的js数据,去找最新接口地址！')
        file.close()
        return
    #读取md5.ini
    config = configparser.ConfigParser()
    config.read(md5_addr)
    #获取新plugins.json的md5
    md5 = getMd5(js_content)
  
    #如果MD5不同，改成新的Md5和抓取时间,保存新js文件
    try:
        old_md5 = config.get("fish_md5", "js")
        if md5 == old_md5:
            print("fish.js file No update needed!")
        else:
            # Update md5.conf
            config.set("fish_md5", "js", md5)
            config.set("fish_md5", "time", str(datetime.now()))
            with open(md5_addr, "w") as f:
                config.write(f)       
            #保存js文件
            saveConfig(js_content,fish_js_addr)
    except Exception as e:
        print(e)
        print('修改md5,保存新js文件时,出现错误了')

def diy_MusicDownloader(js_content):
    print('hello,MusicDownloader大佬! diy_MusicDownloader()开始')
    if js_content == None:
        print('MusicDownloader' + ' : KeyError_应该是网址变了，没获取到最新的js数据,去找最新接口地址！')
        #写入错误日志
        file = open("log.txt", "a")
        file.write('\n' + str(datetime.now()) + ' : ' + 'MusicDownloader' + ' : KeyError_应该是网址变了，没获取到最新的js数据,去找最新接口地址！')
        file.close()
        return
    #读取md5.ini
    config = configparser.ConfigParser()
    config.read(md5_addr)
    #获取新plugins.json的md5
    md5 = getMd5(js_content)
  
    #如果MD5不同，改成新的Md5和抓取时间,保存新js文件
    try:
        old_md5 = config.get("MusicDownloader_md5", "js")
        if md5 == old_md5:
            print("MusicDownloader.js file No update needed!")
        else:
            # Update md5.conf
            config.set("MusicDownloader_md5", "js", md5)
            config.set("MusicDownloader_md5", "time", str(datetime.now()))
            with open(md5_addr, "w") as f:
                config.write(f)       
            #保存js文件
            saveConfig(js_content,MusicDownloader_js_addr)
    except Exception as e:
        print(e)
        print('修改md5,保存新js文件时,出现错误了')
        
if "__name__==__main__":#主程序开始
    #获取最新数据
    configList=getConfigs(list)
    #更新Huibq源
    diy_Huibq(configList['Huibq'])
    #更新ikun0014源
    diy_ikun0014(configList['ikun0014'])
    #更新fish源
    diy_fish(configList['fish'])
    #更新MusicDownloader源
    diy_MusicDownloader(configList['MusicDownloader'])
