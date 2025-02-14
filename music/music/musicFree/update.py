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
  'Huibq':'https://raw.githubusercontent.com/Huibq/keep-alive/master/Music_Free/myPlugins.json',
  'ikun0014':'https://mf.ikunshare.com/plugins.json',
  'fish':'https://rxsub.eu.org/music/musicFree/fish/rx.json',
  'musicDownloader':'https://rxsub.eu.org/music/musicFree/musicDownloader/rx.json'
  }

md5_addr = "md5.ini"
#Huibq
Huibq_json_addr = './Huibq/rx.json'
ikun0014_json_addr = './ikun0014/rx.json'

def saveConfig(customConfig,json_addr):#保存json文件
  
    if customConfig:
    # 配置customConfig及写入文件
        print('保存配置')
        with open(json_addr, "w",encoding='utf-8') as file:
        # 使用json.dump将数据写入文件
            json.dump(customConfig,file,ensure_ascii=False)
            print('抓取时间：\t',datetime.now())

def getMd5(json_content):
    m = hashlib.md5()
    str_json = str(json_content)
    m.update(str_json.encode('utf-8'))
    md5 = m.hexdigest()
    return md5

def getUrlContent(url):  
    headers={
    "User-Agent":"okhttp/3.15",
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
    }
    #print(url)
    try:
        r=requests.get(url,headers=headers, timeout=5.0)
        if r.status_code==200:
            r.encoding='utf-8'    #编码方式
            return r.text
    except requests.exceptions.RequestException as e:  
        print(e)
        print('getUrlContent()功能中出现的错误！获取js内容失败，或者打开网址错误!')
        return None

def getConfig(url):#获取网站的json内容，将获取的config返回
    headers={
    "User-Agent":"okhttp/3.15",
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
    }
    try:
        r=requests.get(url,headers=headers, timeout=3.0)
        if r.status_code==200:
            r.encoding='utf-8'    #编码方式
            jsonText=json5.loads(r.text)
            return jsonText
    except requests.exceptions.RequestException as e:  
        print(e)
        print('getConfig()功能中出现的错误！获取json失败，或者打开网址错误!')
        return None
        
def getConfigs(list):#获取列表网站的json内容，将获取的内容存入列表configList返回
    configList={}
    for key,value in list.items():
        config=getConfig(value)
        configList[key]=config
    return configList

def diy_Huibq(json_content):
    print('hello,Huibq大佬! diy_Huibq()开始')
    if json_content == None:
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
    md5 = getMd5(json_content)

    #提取json里面的url地址使用
    qq_url = ''
    kw_url = ''
    wy_url = ''
    kg_url = ''
    mg_url = ''
    #将数据转成json5格式
    json_format = json5.loads(json_content)
    #提取网址信息，后面更新要使用，再将地址改成自己的网址
    for site in json_format["plugins"]:
        if site["name"] == '小秋音乐':
            qq_url = site['url']
            site['url'] = 'https://rxsub.eu.org/music/musicFree/Huibq/qq.js'
        if site["name"] == '小蜗音乐':
            kw_url = site['url']
            site['url'] = 'https://rxsub.eu.org/music/musicFree/Huibq/kw.js'
        if site["name"] == '小芸音乐':
            wy_url = site['url']
            site['url'] = 'https://rxsub.eu.org/music/musicFree/Huibq/wy.js'
        if site["name"] == '小枸音乐':
            kg_url = site['url']
            site['url'] = 'https://rxsub.eu.org/music/musicFree/Huibq/kg.js'
        if site["name"] == '小蜜音乐':
            mg_url = site['url']
            site['url'] = 'https://rxsub.eu.org/music/musicFree/Huibq/mg.js'     
    #如果MD5不同，改成新的Md5和抓取时间
    try:
        old_md5 = config.get("Huibq_md5", "json")
        if md5 == old_md5:
            print("plugins.json file No update needed!")
        else:
            # Update md5.conf
            config.set("Huibq_md5", "json", md5)
            config.set("Huibq_md5", "time", str(datetime.now()))
            with open(md5_addr, "w") as f:
                config.write(f)       
            #保存json文件
            saveConfig(json_format,Huibq_json_addr)
    except Exception as e:
        print(e)
        print('修改md5出现错误了')
        
    #小秋音乐
    url_content = getUrlContent(qq_url)
    if url_content != None:
        md5 = getMd5(url_content)
        old_md5 = config.get("Huibq_md5", "xiaoqiu")
        if md5 != old_md5:
            #写入新md5和抓取时间
            config.set("Huibq_md5", "xiaoqiu", md5)
            config.set("Huibq_md5", "time", str(datetime.now())) 
            with open(md5_addr, "w") as f:
                config.write(f) 
            #diy信息
            try:
                #修改显示名字
                old_name = '小秋音乐'
                new_name = '<QQ>'
                url_content = re.sub(old_name, new_name, url_content)
                #修改更新地址
                old_url_list = re.findall(r'srcUrl: "(.*?).js"',url_content)
                old_url = old_url_list[0]
                new_url = 'https://rxsub.eu.org/music/musicFree/Huibq/qq'
                url_content = re.sub(old_url, new_url, url_content)
                #写入文件
                file = open("./Huibq/qq.js", "w")
                file.write(url_content)
                file.close()
                print("小秋音乐 update 成功!")
            except Exception as e:#万能异常
                print(str(e) + 'Exception_出现异常')
                pass
        else:
            print("小秋音乐 file No update needed!")
    else:
        print('小秋音乐 获取失败！')
        
    #小蜗音乐
    url_content = getUrlContent(kw_url)
    if url_content != None:
        md5 = getMd5(url_content)
        old_md5 = config.get("Huibq_md5", "xiaowo")
        if md5 != old_md5:
            #写入新md5和抓取时间
            config.set("Huibq_md5", "xiaowo", md5)
            config.set("Huibq_md5", "time", str(datetime.now())) 
            with open(md5_addr, "w") as f:
                config.write(f) 
            #diy信息
            try:
                #修改显示名字
                old_name = '小蜗音乐'
                new_name = '<酷我>'
                url_content = re.sub(old_name, new_name, url_content)
                #修改更新地址
                old_url_list = re.findall(r'srcUrl: "(.*?).js"',url_content)
                old_url = old_url_list[0]
                new_url = 'https://rxsub.eu.org/music/musicFree/Huibq/kw'
                url_content = re.sub(old_url, new_url, url_content)
                #写入文件
                file = open("./Huibq/kw.js", "w")
                file.write(url_content)
                file.close()
                print("小蜗音乐 update 成功!")
            except Exception as e:#万能异常
                print(str(e) + 'Exception_出现异常')
                pass
        else:
            print("小蜗音乐 file No update needed!")
    else:
        print('小蜗音乐 获取失败！')  
        
    #小芸音乐
    url_content = getUrlContent(wy_url)
    if url_content != None:
        md5 = getMd5(url_content)
        old_md5 = config.get("Huibq_md5", "xiaoyun")
        if md5 != old_md5:
            #写入新md5和抓取时间
            config.set("Huibq_md5", "xiaoyun", md5)
            config.set("Huibq_md5", "time", str(datetime.now())) 
            with open(md5_addr, "w") as f:
                config.write(f) 
            #diy信息
            try:
                #修改显示名字
                old_name = '小芸音乐'
                new_name = '<网易云>'
                url_content = re.sub(old_name, new_name, url_content)
                #修改更新地址
                old_url_list = re.findall(r'srcUrl: "(.*?).js"',url_content)
                old_url = old_url_list[0]
                new_url = 'https://rxsub.eu.org/music/musicFree/Huibq/wy'
                url_content = re.sub(old_url, new_url, url_content)
                #写入文件
                file = open("./Huibq/wy.js", "w")
                file.write(url_content)
                file.close()
                print("小芸音乐 update 成功!")
            except Exception as e:#万能异常
                print(str(e) + 'Exception_出现异常')
                pass
        else:
            print("小芸音乐 file No update needed!")
    else:
        print('小芸音乐 获取失败！')  
        
    #小枸音乐
    url_content = getUrlContent(kg_url)
    if url_content != None:
        md5 = getMd5(url_content)
        old_md5 = config.get("Huibq_md5", "xiaogou")
        if md5 != old_md5:
            #写入新md5和抓取时间
            config.set("Huibq_md5", "xiaogou", md5)
            config.set("Huibq_md5", "time", str(datetime.now())) 
            with open(md5_addr, "w") as f:
                config.write(f) 
            #diy信息
            try:
                #修改显示名字
                old_name = '小枸音乐'
                new_name = '<酷狗>'
                url_content = re.sub(old_name, new_name, url_content)
                #修改更新地址
                old_url_list = re.findall(r'srcUrl: "(.*?).js"',url_content)
                old_url = old_url_list[0]
                new_url = 'https://rxsub.eu.org/music/musicFree/Huibq/kg'
                url_content = re.sub(old_url, new_url, url_content)
                #写入文件
                file = open("./Huibq/kg.js", "w")
                file.write(url_content)
                file.close()
                print("小枸音乐 update 成功!")
            except Exception as e:#万能异常
                print(str(e) + 'Exception_出现异常')
                pass
        else:
            print("小枸音乐 file No update needed!")
    else:
        print('小枸音乐 获取失败！')    
        
    #小蜜音乐
    url_content = getUrlContent(mg_url)
    if url_content != None:
        md5 = getMd5(url_content)
        old_md5 = config.get("Huibq_md5", "xiaomi")
        if md5 != old_md5:
            #写入新md5和抓取时间
            config.set("Huibq_md5", "xiaomi", md5)
            config.set("Huibq_md5", "time", str(datetime.now())) 
            with open(md5_addr, "w") as f:
                config.write(f)             
            #diy信息
            try:
                #修改显示名字
                old_name = '小蜜音乐'
                new_name = '<咪咕>'
                url_content = re.sub(old_name, new_name, url_content)
                #修改更新地址
                old_url_list = re.findall(r'srcUrl: "(.*?).js"',url_content)
                old_url = old_url_list[0]
                new_url = 'https://rxsub.eu.org/music/musicFree/Huibq/mg'
                url_content = re.sub(old_url, new_url, url_content)
                #写入文件
                file = open("./Huibq/mg.js", "w")
                file.write(url_content)
                file.close()
                print("小蜜音乐 update 成功!")
            except Exception as e:#万能异常
                print(str(e) + 'Exception_出现异常')
                pass
        else:
            print("小蜜音乐 file No update needed!")
    else:
        print('小蜜音乐 获取失败！')   

def diy_ikun0014(json_content):
    print('hello,ikun0014大佬! diy_ikun0014()开始')
    if json_content == None:
        print('ikun0014' + ' : KeyError_应该是网址变了，没获取到最新的js数据,去找最新接口地址！')
        #因ikun0014网站停用，暂时先关闭写入错误
        #写入错误日志
        file = open("log.txt", "a")
        file.write('\n' + str(datetime.now()) + ' : ' + 'ikun0014' + ' : KeyError_应该是网址变了，没获取到最新的js数据,去找最新接口地址！')
        file.close()
        return
    #读取md5.ini
    config = configparser.ConfigParser()
    config.read(md5_addr)
    #获取新plugins.json的md5
    md5 = getMd5(json_content)
    
    #提取json里面的url地址使用
    qq_url = ''
    kw_url = ''
    wy_url = ''
    kg_url = ''
    mg_url = ''
    klrc_url = ''
    
    #将数据转成json5格式
    json_format = json5.loads(json_content)
    #提取网址信息，后面更新要使用，再将地址改成自己的网址
    for site in json_format["plugins"]:
        if '/qq' in site["url"]:
            qq_url = site['url']
            site['url'] = 'https://rxsub.eu.org/music/musicFree/ikun0014/qq.js'
        if '/kw' in site["url"]:
            kw_url = site['url']
            site['url'] = 'https://rxsub.eu.org/music/musicFree/ikun0014/kw.js'
        if '/wy' in site["url"]:
            wy_url = site['url']
            site['url'] = 'https://rxsub.eu.org/music/musicFree/ikun0014/wy.js'
        if '/kg' in site["url"]:
            kg_url = site['url']
            site['url'] = 'https://rxsub.eu.org/music/musicFree/ikun0014/kg.js'
        if '/mg' in site["url"]:
            mg_url = site['url']
            site['url'] = 'https://rxsub.eu.org/music/musicFree/ikun0014/mg.js'  
        if '/klrc' in site["url"]:
            klrc_url = site['url']
            site['url'] = 'https://rxsub.eu.org/music/musicFree/ikun0014/klrc.js'  
                    
    #如果MD5不同，改成新的Md5和抓取时间
    try:
        old_md5 = config.get("ikun0014_md5", "json")
        if md5 == old_md5:
            print("plugins.json file No update needed!")
        else:
            # Update md5.conf
            config.set("ikun0014_md5", "json", md5)
            config.set("ikun0014_md5", "time", str(datetime.now()))
            with open(md5_addr, "w") as f:
                config.write(f)
            #保存json文件
            saveConfig(json_format,ikun0014_json_addr)
    except Exception as e:
        print(e)
        print('修改md5出现错误了')
        
    #小秋音乐
    url_content = getUrlContent(qq_url)
    if url_content != None:
        md5 = getMd5(url_content)
        old_md5 = config.get("ikun0014_md5", "qq")
        if md5 != old_md5:
            #写入新md5和抓取时间
            config.set("ikun0014_md5", "qq", md5)
            config.set("ikun0014_md5", "time", str(datetime.now())) 
            with open(md5_addr, "w") as f:
                config.write(f) 
            #diy信息
            try:
                #修改显示名字
                old_name_list = re.findall(r'platform: ".*?",',url_content)
                for old_name in old_name_list:
                    new_name = f'platform: "-QQ音乐-",'
                    url_content = re.sub(old_name, new_name, url_content)
                #修改更新地址
                old_url_list = re.findall(r'srcUrl: "(.*?).js"',url_content)
                old_url = old_url_list[0]
                new_url = 'https://rxsub.eu.org/music/musicFree/ikun0014/qq'
                url_content = re.sub(old_url, new_url, url_content)
            except Exception as e:#万能异常
                print(str(e) + 'Exception_出现异常')
                pass
            #写入文件
            file = open("./ikun0014/qq.js", "w")
            file.write(url_content)
            file.close()
            print("qq音乐 update 成功!")
        else:
            print("qq音乐 file No update needed!")
    else:
        print('qq音乐 获取失败！')
        
    #小蜗音乐
    url_content = getUrlContent(kw_url)
    if url_content != None:
        md5 = getMd5(url_content)
        old_md5 = config.get("ikun0014_md5", "kw")
        if md5 != old_md5:
            #写入新md5和抓取时间
            config.set("ikun0014_md5", "kw", md5)
            config.set("ikun0014_md5", "time", str(datetime.now())) 
            with open(md5_addr, "w") as f:
                config.write(f) 
            #diy信息
            try:
                #修改显示名字
                old_name_list = re.findall(r'platform: ".*?",',url_content)
                for old_name in old_name_list:
                    new_name = f'platform: "-酷我-",'
                    url_content = re.sub(old_name, new_name, url_content)
                #修改更新地址
                old_url_list = re.findall(r'srcUrl: "(.*?).js"',url_content)
                old_url = old_url_list[0]
                new_url = 'https://rxsub.eu.org/music/musicFree/ikun0014/kw'
                url_content = re.sub(old_url, new_url, url_content)
            except Exception as e:#万能异常
                print(str(e) + 'Exception_出现异常')
                pass
            #写入文件
            file = open("./ikun0014/kw.js", "w")
            file.write(url_content)
            file.close()
            print("小蜗音乐 update 成功!")
        else:
            print("小蜗音乐 file No update needed!")
    else:
        print('小蜗音乐 获取失败！')  
        
    #小芸音乐
    url_content = getUrlContent(wy_url)
    if url_content != None:
        md5 = getMd5(url_content)
        old_md5 = config.get("ikun0014_md5", "wy")
        if md5 != old_md5:
            #写入新md5和抓取时间
            config.set("ikun0014_md5", "wy", md5)
            config.set("ikun0014_md5", "time", str(datetime.now())) 
            with open(md5_addr, "w") as f:
                config.write(f)
            #diy信息
            try:                
                #修改显示名字
                old_name_list = re.findall(r'platform: ".*?",',url_content)
                for old_name in old_name_list:
                    new_name = f'platform: "-网易云-",'
                    url_content = re.sub(old_name, new_name, url_content)
                #修改更新地址
                old_url_list = re.findall(r'srcUrl: "(.*?).js"',url_content)
                old_url = old_url_list[0]
                new_url = 'https://rxsub.eu.org/music/musicFree/ikun0014/wy'
                url_content = re.sub(old_url, new_url, url_content)
            except Exception as e:#万能异常
                print(str(e) + 'Exception_出现异常')
                pass
            #写入文件
            file = open("./ikun0014/wy.js", "w")
            file.write(url_content)
            file.close()
            print("小芸音乐 update 成功!")
        else:
            print("小芸音乐 file No update needed!")
    else:
        print('小芸音乐 获取失败！')  
        
    #小枸音乐
    url_content = getUrlContent(kg_url)
    if url_content != None:
        md5 = getMd5(url_content)
        old_md5 = config.get("ikun0014_md5", "kg")
        if md5 != old_md5:
            #写入新md5和抓取时间
            config.set("ikun0014_md5", "kg", md5)
            config.set("ikun0014_md5", "time", str(datetime.now())) 
            with open(md5_addr, "w") as f:
                config.write(f)
            #diy信息
            try:                
                #修改显示名字
                old_name_list = re.findall(r'platform: ".*?",',url_content)
                for old_name in old_name_list:
                    new_name = f'platform: "-酷狗-",'
                    url_content = re.sub(old_name, new_name, url_content)
                #修改更新地址
                old_url_list = re.findall(r'srcUrl: "(.*?).js"',url_content)
                old_url = old_url_list[0]
                new_url = 'https://rxsub.eu.org/music/musicFree/ikun0014/kg'
                url_content = re.sub(old_url, new_url, url_content)
            except Exception as e:#万能异常
                print(str(e) + 'Exception_出现异常')
                pass
            #写入文件
            file = open("./ikun0014/kg.js", "w")
            file.write(url_content)
            file.close()
            print("小枸音乐 update 成功!")
        else:
            print("小枸音乐 file No update needed!")
    else:
        print('小枸音乐 获取失败！')    
        
    #小蜜音乐
    url_content = getUrlContent(mg_url)
    if url_content != None:
        md5 = getMd5(url_content)
        old_md5 = config.get("ikun0014_md5", "mg")
        if md5 != old_md5:
            #写入新md5和抓取时间
            config.set("ikun0014_md5", "mg", md5)
            config.set("ikun0014_md5", "time", str(datetime.now())) 
            with open(md5_addr, "w") as f:
                config.write(f) 
            #diy信息
            try:
                #修改显示名字
                old_name_list = re.findall(r'platform: ".*?",',url_content)
                for old_name in old_name_list:
                    new_name = f'platform: "-咪咕-",'
                    url_content = re.sub(old_name, new_name, url_content)
                #修改更新地址
                old_url_list = re.findall(r'srcUrl: "(.*?).js"',url_content)
                old_url = old_url_list[0]
                new_url = 'https://rxsub.eu.org/music/musicFree/ikun0014/mg'
                url_content = re.sub(old_url, new_url, url_content)
            except Exception as e:#万能异常
                print(str(e) + 'Exception_出现异常')
                pass
            #写入文件
            file = open("./ikun0014/mg.js", "w")
            file.write(url_content)
            file.close()
            print("小蜜音乐 update 成功!")
        else:
            print("小蜜音乐 file No update needed!")
    else:
        print('小蜜音乐 获取失败！')  

    #酷歌词
    url_content = getUrlContent(klrc_url)
    if url_content != None:
        md5 = getMd5(url_content)
        old_md5 = config.get("ikun0014_md5", "klrc")
        if md5 != old_md5:
            #写入新md5和抓取时间
            config.set("ikun0014_md5", "klrc", md5)
            config.set("ikun0014_md5", "time", str(datetime.now())) 
            with open(md5_addr, "w") as f:
                config.write(f) 
            #写入文件
            file = open("./ikun0014/klrc.js", "w")
            file.write(url_content)
            file.close()
            print("酷歌词 update 成功!")
        else:
            print("酷歌词 file No update needed!")
    else:
        print('酷歌词 获取失败！')  

def diy_fish(json_content):
    print('hello,fish大佬! diy_fish()开始')
    if json_content == None:
        print('fish' + ' : KeyError_应该是网址变了，没获取到最新的js数据,去找最新接口地址！')
        #写入错误日志
        file = open("log.txt", "a")
        file.write('\n' + str(datetime.now()) + ' : ' + 'fish' + ' : KeyError_应该是网址变了，没获取到最新的js数据,去找最新接口地址！')
        file.close()
        return
    #获取fish的lx音源文件
    fish_content = getUrlContent('https://m-api.ceseet.me/script')
    
    #获取最新的版本md5
    new_md5 = re.findall(r"SCRIPT_MD5 = '(.*?)'",fish_content)
    if new_md5:
        #print(new_md5[0])
        md5 = new_md5[0]
    else:
        new_md5 = re.findall(r'SCRIPT_MD5 = "(.*?)"',fish_content)
        if new_md5:
            #print(new_md5[0])
            md5 = new_md5[0]
        else:
            print("not get new_md5,so no update!")
            return
    #获取最新的api地址API_URL
    API_URL = re.findall(r'API_URL = "(.*?)"',fish_content)
    if API_URL:
        #print(API_URL[0])
        api = API_URL[0]
    else:
        API_URL = re.findall(r"API_URL = '(.*?)'",fish_content)
        if API_URL:
            #print(API_URL[0])
            api = API_URL[0]
        else:
            print("not get API_URL,so no update!")
            return
    #获取最新的api地址API_key
    api_key_list = re.findall(r"API_KEY = `(.*?)`",fish_content)
    if api_key_list:
        if api_key_list[0]!= '':
            api_key = api_key_list[0]
        else:
            api_key = None
    else:
        print("not get API_KEY!")
        api_key = None

    #读取md5.ini
    config = configparser.ConfigParser()
    config.read(md5_addr)

    #如果MD5不同，改成新的Md5和抓取时间
    try:
        old_md5 = config.get("fish_md5", "js")
        old_api = config.get("fish_md5", "api")
        if md5 == old_md5 and api == old_api:
            print("fish.json file No update needed!")
            return
        else:
            # Update md5.conf
            config.set("fish_md5", "js", md5)
            config.set("fish_md5", "api", api)
            config.set("fish_md5", "time", str(datetime.now()))
            with open(md5_addr, "w") as f:
                config.write(f)
    except Exception as e:
        print(e)
        print('修改md5出现错误了')

    #提取json里面的url地址使用
    qq_url = ''
    kw_url = ''
    wy_url = ''
    kg_url = ''
    mg_url = ''
    klrc_url = ''
    #将数据转成json5格式
    #json_format = json5.loads(json_content)
    json_format = json_content
    #提取网址信息，后面更新要使用，再将地址改成自己的网址
    for site in json_format["plugins"]:
        if site["name"] == 'QQ Music':
            qq_url = site['url']
        if site["name"] == 'Kuwo Music':
            kw_url = site['url']
        if site["name"] == 'Netease Cloud Music':
            wy_url = site['url']
        if site["name"] == 'Kugou Music':
            kg_url = site['url']
        if site["name"] == 'Migu Music':
            mg_url = site['url']

    #小秋音乐
    url_content = getUrlContent(qq_url)
    if url_content != None:
        #diy信息
        try:
            #修改更新地址
            old_url_list = re.findall(r'`(.*?)/url/tx/',url_content)
            old_url = old_url_list[0]
            url_content = re.sub(old_url, api, url_content)
            #如果有key,更新key
            if api_key:
                old_key_list = re.findall(r'"X-Request-Key": "(.*?)"',url_content)
                if old_key_list:
                    old_key = old_key_list[0]
                    if old_key != '':
                        url_content = re.sub(old_key, api_key, url_content)
                    else:
                        url_content = re.sub(f'"X-Request-Key": ""', f'"X-Request-Key": "{api_key}"', url_content)
            #写入文件
            file = open("./fish/qq.js", "w")
            file.write(url_content)
            file.close()
            print("qq音乐 update 成功!")
        except Exception as e:#万能异常
            print(str(e) + 'Exception_出现异常')
            pass
    else:
        print('qq音乐 获取失败！')
        
    #小蜗音乐
    url_content = getUrlContent(kw_url)
    if url_content != None:
        #diy信息
        try:
            #修改更新地址
            old_url_list = re.findall(r'`(.*?)/url/kw/',url_content)
            old_url = old_url_list[0]
            url_content = re.sub(old_url, api, url_content)
            #如果有key,更新key
            if api_key:
                old_key_list = re.findall(r'"X-Request-Key": "(.*?)"',url_content)
                if old_key_list:
                    old_key = old_key_list[0]
                    if old_key != '':
                        url_content = re.sub(old_key, api_key, url_content)
                    else:
                        url_content = re.sub(f'"X-Request-Key": ""', f'"X-Request-Key": "{api_key}"', url_content)
            #写入文件
            file = open("./fish/kw.js", "w")
            file.write(url_content)
            file.close()
            print("小蜗音乐 update 成功!")
        except Exception as e:#万能异常
            print(str(e) + 'Exception_出现异常')
            pass
    else:
        print('小蜗音乐 获取失败！')  
        
    #小芸音乐
    url_content = getUrlContent(wy_url)
    if url_content != None:
        #diy信息
        try:
            #修改更新地址
            old_url_list = re.findall(r'`(.*?)/url/wy/',url_content)
            i=0
            while i<len(old_url_list):
                old_url = old_url_list[i]
                url_content = re.sub(old_url, api, url_content)
                i=i+1
            #如果有key,更新key
            if api_key:
                old_key_list = re.findall(r'"X-Request-Key": "(.*?)"',url_content)
                if old_key_list:
                    old_key = old_key_list[0]
                    if old_key != '':
                        url_content = re.sub(old_key, api_key, url_content)
                    else:
                        url_content = re.sub(f'"X-Request-Key": ""', f'"X-Request-Key": "{api_key}"', url_content)
            #写入文件
            file = open("./fish/wy.js", "w")
            file.write(url_content)
            file.close()
            print("小芸音乐 update 成功!")
        except Exception as e:#万能异常
            print(str(e) + 'Exception_出现异常')
            pass
    else:
        print('小芸音乐 获取失败！')  
        
    #小枸音乐
    url_content = getUrlContent(kg_url)
    if url_content != None:
        #diy信息
        try:
            #修改更新地址
            old_url_list = re.findall(r'`(.*?)/url/kg/',url_content)
            old_url = old_url_list[0]
            url_content = re.sub(old_url, api, url_content)
            #如果有key,更新key
            if api_key:
                old_key_list = re.findall(r'"X-Request-Key": "(.*?)"',url_content)
                if old_key_list:
                    old_key = old_key_list[0]
                    if old_key != '':
                        url_content = re.sub(old_key, api_key, url_content)
                    else:
                        url_content = re.sub(f'"X-Request-Key": ""', f'"X-Request-Key": "{api_key}"', url_content)
            #写入文件
            file = open("./fish/kg.js", "w")
            file.write(url_content)
            file.close()
            print("小枸音乐 update 成功!")
        except Exception as e:#万能异常
            print(str(e) + 'Exception_出现异常')
            pass
    else:
        print('小枸音乐 获取失败！')    
        
    #小蜜音乐
    url_content = getUrlContent(mg_url)
    if url_content != None:
        #diy信息
        try:
            #修改更新地址
            old_url_list = re.findall(r'`(.*?)/url/mg/',url_content)
            old_url = old_url_list[0]
            url_content = re.sub(old_url, api, url_content)
            #如果有key,更新key
            if api_key:
                old_key_list = re.findall(r'"X-Request-Key": "(.*?)"',url_content)
                if old_key_list:
                    old_key = old_key_list[0]
                    if old_key != '':
                        url_content = re.sub(old_key, api_key, url_content)
                    else:
                        url_content = re.sub(f'"X-Request-Key": ""', f'"X-Request-Key": "{api_key}"', url_content)
            #写入文件
            file = open("./fish/mg.js", "w")
            file.write(url_content)
            file.close()
            print("小蜜音乐 update 成功!")
        except Exception as e:#万能异常
            print(str(e) + 'Exception_出现异常')
            pass
    else:
        print('小蜜音乐 获取失败！')  

def diy_musicDownloader(json_content):
    print('hello! diy_musicDownloader()开始')
    if json_content == None:
        print('musicDownloader' + ' : KeyError_应该是网址变了，没获取到最新的js数据,去找最新接口地址！')
        #写入错误日志
        file = open("log.txt", "a")
        file.write('\n' + str(datetime.now()) + ' : ' + 'musicDownloader' + ' : KeyError_应该是网址变了，没获取到最新的js数据,去找最新接口地址！')
        file.close()
        return
    #获取musicDownloader的lx音源文件
    musicDownloader_content = getUrlContent('https://ikun.laoguantx.top:19742/script?key=LXMusic_dmsowplaeq')
    
    #获取最新的版本md5
    new_md5 = re.findall(r"SCRIPT_MD5 = '(.*?)'",musicDownloader_content)
    if new_md5:
        #print(new_md5[0])
        md5 = new_md5[0]
    else:
        new_md5 = re.findall(r'SCRIPT_MD5 = "(.*?)"',musicDownloader_content)
        if new_md5:
            #print(new_md5[0])
            md5 = new_md5[0]
        else:
            print("not get new_md5,so no update!")
            return
    #获取最新的api地址API_URL
    API_URL = re.findall(r'API_URL = "(.*?)"',musicDownloader_content)
    if API_URL:
        #print(API_URL[0])
        api = API_URL[0]
    else:
        API_URL = re.findall(r"API_URL = '(.*?)'",musicDownloader_content)
        if API_URL:
            #print(API_URL[0])
            api = API_URL[0]
        else:
            print("not get API_URL,so no update!")
            return
    API_URL_add = re.findall(r'\{API_URL\}(.*?)url/\$\{source\}/',musicDownloader_content)
    if API_URL_add:
        api = api + API_URL_add[0]
    #获取最新的api地址API_key
    api_key_list = re.findall(r"API_KEY = `(.*?)`",musicDownloader_content)
    if api_key_list:
        if api_key_list[0]!= '':
            api_key = api_key_list[0]
        else:
            api_key = None
    else:
        print("not get API_KEY!")
        api_key = None

    #读取md5.ini
    config = configparser.ConfigParser()
    config.read(md5_addr)

    #如果MD5不同，改成新的Md5和抓取时间
    try:
        old_md5 = config.get("musicDown_md5", "js")
        old_api = config.get("musicDown_md5", "api")
        if md5 == old_md5 and api == old_api:
            print("musicDown.json file No update needed!")
            return
        else:
            # Update md5.conf
            config.set("musicDown_md5", "js", md5)
            config.set("musicDown_md5", "api", api)
            config.set("musicDown_md5", "time", str(datetime.now()))
            with open(md5_addr, "w") as f:
                config.write(f)
    except Exception as e:
        print(e)
        print('修改md5出现错误了')

    #提取json里面的url地址使用
    qq_url = ''
    kw_url = ''
    wy_url = ''
    kg_url = ''
    mg_url = ''
    klrc_url = ''
    #将数据转成json5格式
    #json_format = json5.loads(json_content)
    json_format = json_content
    #提取网址信息，后面更新要使用，再将地址改成自己的网址
    for site in json_format["plugins"]:
        if site["name"] == 'QQ Music':
            qq_url = site['url']
        if site["name"] == 'Kuwo Music':
            kw_url = site['url']
        if site["name"] == 'Netease Cloud Music':
            wy_url = site['url']
        if site["name"] == 'Kugou Music':
            kg_url = site['url']
        if site["name"] == 'Migu Music':
            mg_url = site['url']
    
    #小秋音乐
    url_content = getUrlContent(qq_url)
    if url_content != None:
        #diy信息
        try:
            #修改更新地址
            old_url_list = re.findall(r'`(.*?)url/tx/',url_content)
            old_url = old_url_list[0]
            url_content = re.sub(old_url, api, url_content)
            #如果有key,更新key
            if api_key:
                old_key_list = re.findall(r'"X-Request-Key": "(.*?)"',url_content)
                if old_key_list:
                    old_key = old_key_list[0]
                    if old_key != '':
                        url_content = re.sub(old_key, api_key, url_content)
                    else:
                        url_content = re.sub(f'"X-Request-Key": ""', f'"X-Request-Key": "{api_key}"', url_content)
            #写入文件
            file = open("./musicDownloader/qq.js", "w")
            file.write(url_content)
            file.close()
            print("qq音乐 update 成功!")
        except Exception as e:#万能异常
            print(str(e) + 'Exception_出现异常')
            pass
    else:
        print('qq音乐 获取失败！')
    #小蜗音乐
    url_content = getUrlContent(kw_url)
    if url_content != None:
        #diy信息
        try:
            #修改更新地址
            old_url_list = re.findall(r'`(.*?)url/kw/',url_content)
            old_url = old_url_list[0]
            url_content = re.sub(old_url, api, url_content)
            #如果有key,更新key
            if api_key:
                old_key_list = re.findall(r'"X-Request-Key": "(.*?)"',url_content)
                if old_key_list:
                    old_key = old_key_list[0]
                    if old_key != '':
                        url_content = re.sub(old_key, api_key, url_content)
                    else:
                        url_content = re.sub(f'"X-Request-Key": ""', f'"X-Request-Key": "{api_key}"', url_content)
            #写入文件
            file = open("./musicDownloader/kw.js", "w")
            file.write(url_content)
            file.close()
            print("小蜗音乐 update 成功!")
        except Exception as e:#万能异常
            print(str(e) + 'Exception_出现异常')
            pass
    else:
        print('小蜗音乐 获取失败！')  
        
    #小芸音乐
    url_content = getUrlContent(wy_url)
    if url_content != None:
        #diy信息
        try:
            #修改更新地址,网易云中有2处需要替换
            old_url_list = re.findall(r'`(.*?)url/wy/',url_content)
            i=0
            while i<len(old_url_list):
                old_url = old_url_list[i]
                url_content = re.sub(old_url, api, url_content)
                i=i+1
            #如果有key,更新key
            if api_key:
                old_key_list = re.findall(r'"X-Request-Key": "(.*?)"',url_content)
                if old_key_list:
                    old_key = old_key_list[0]
                    if old_key != '':
                        url_content = re.sub(old_key, api_key, url_content)
                    else:
                        url_content = re.sub(f'"X-Request-Key": ""', f'"X-Request-Key": "{api_key}"', url_content)
            #写入文件
            file = open("./musicDownloader/wy.js", "w")
            file.write(url_content)
            file.close()
            print("小芸音乐 update 成功!")
        except Exception as e:#万能异常
            print(str(e) + 'Exception_出现异常')
            pass
    else:
        print('小芸音乐 获取失败！')  
        
    #小枸音乐
    url_content = getUrlContent(kg_url)
    if url_content != None:
        #diy信息
        try:
            #修改更新地址
            old_url_list = re.findall(r'`(.*?)url/kg/',url_content)
            old_url = old_url_list[0]
            url_content = re.sub(old_url, api, url_content)
            #如果有key,更新key
            if api_key:
                old_key_list = re.findall(r'"X-Request-Key": "(.*?)"',url_content)
                if old_key_list:
                    old_key = old_key_list[0]
                    if old_key != '':
                        url_content = re.sub(old_key, api_key, url_content)
                    else:
                        url_content = re.sub(f'"X-Request-Key": ""', f'"X-Request-Key": "{api_key}"', url_content)
            #写入文件
            file = open("./musicDownloader/kg.js", "w")
            file.write(url_content)
            file.close()
            print("小枸音乐 update 成功!")
        except Exception as e:#万能异常
            print(str(e) + 'Exception_出现异常')
            pass
    else:
        print('小枸音乐 获取失败！')    
        
    #小蜜音乐
    url_content = getUrlContent(mg_url)
    if url_content != None:
        #diy信息
        try:
            #修改更新地址
            old_url_list = re.findall(r'`(.*?)url/mg/',url_content)
            old_url = old_url_list[0]
            url_content = re.sub(old_url, api, url_content)
            #如果有key,更新key
            if api_key:
                old_key_list = re.findall(r'"X-Request-Key": "(.*?)"',url_content)
                if old_key_list:
                    old_key = old_key_list[0]
                    if old_key != '':
                        url_content = re.sub(old_key, api_key, url_content)
                    else:
                        url_content = re.sub(f'"X-Request-Key": ""', f'"X-Request-Key": "{api_key}"', url_content)
            #写入文件
            file = open("./musicDownloader/mg.js", "w")
            file.write(url_content)
            file.close()
            print("小蜜音乐 update 成功!")
        except Exception as e:#万能异常
            print(str(e) + 'Exception_出现异常')
            pass
    else:
        print('小蜜音乐 获取失败！')  

if "__name__==__main__":#主程序开始
    #获取最新数据
    configList=getConfigs(list)
    #更新Huibq源
    diy_Huibq(configList['Huibq'])
    #更新ikun0014源
    diy_ikun0014(configList['ikun0014'])
    #更新fish源
    diy_fish(configList['fish'])
    #更新musicDownloader源
    diy_musicDownloader(configList['musicDownloader'])
