#参考
#https://github.com/yub168/myTvbox/tree/master
#https://github.com/loopool/fan/tree/main
#最全的常用正则表达式大全https://blog.csdn.net/weixin_40583388/article/details/78458610
# -*- coding: utf-8 -*-
import requests
import json
import re
import os
import json5
import base64
from Crypto.Cipher import AES
from tqdm import tqdm
import threading
from datetime import datetime   #时间
import hashlib
import configparser		#https://blog.csdn.net/happyjacob/article/details/109346625

#rx = {"key":"儿童乐园","name":"儿童乐园","type":3,"api":"csp_Bili","searchable":0,"quickSearch":0,"changeable":0,"ext":"http://d.kstore.dev/download/4901/tvbox/json/儿童乐园.json"}
rx = {"key":"儿童乐园","name":"儿童乐园","type":3,"api":"csp_Bili","searchable":0,"quickSearch":0,"changeable":0,"ext": "./json/儿童乐园.json"}

#https://github.moeyy.xyz/
#将json数据转成字符串，https://blog.csdn.net/qq_46293423/article/details/105785007
#content = json.dumps(config,ensure_ascii=False)
#config = re.sub(r'"https://raw.githubusercontent.com/n3rddd/N3RD/master/JN/','"./',content)
#将字符串转成json数据，https://blog.csdn.net/qq_46293423/article/details/105785007
#config = json.loads(config)


list={
    'feimao':'http://www.饭太硬.com/jm/jiemi.php?url=http://肥猫.com',
    'fan':"http://www.饭太硬.com/tv",
    'n3rddd_lem':'https://raw.githubusercontent.com/n3rddd/N3RD/refs/heads/master/JN/lem.json',
    'n3rddd_js':'https://raw.githubusercontent.com/n3rddd/N3RD/master/JN/lemj.json',
    'n3rddd_vod':'https://raw.githubusercontent.com/n3rddd/N3RD/master/JN/lemvod.json',
    'PowerTechott2':'https://raw.githubusercontent.com/PowerTechott/baotv/refs/heads/main/bh2',
    "月光线路1":"https://raw.githubusercontent.com/guot55/yg/main/box原.json",
    "潇洒线路":"https://raw.githubusercontent.com/PizazzGY/TVBox/main/api.json",
    '小而美':'https://raw.githubusercontent.com/xixifree/xxbox/master/0821.json',
    "dxawi":"https://raw.githubusercontent.com/dxawi/0/refs/heads/main/0.json",
    '香雅情':'https://raw.githubusercontent.com/xyq254245/xyqonlinerule/main/XYQTVBox.json',
    "qq1719248506":"https://raw.githubusercontent.com/qq1719248506/Video-interface/refs/heads/main/config.json",
    "anaer":"https://raw.githubusercontent.com/anaer/Meow/refs/heads/main/meow.json",
    "aaabbbxu1":"https://raw.githubusercontent.com/aaabbbxu/tvboxs/refs/heads/main/boxs.json",
    "莫名的悲伤":"https://raw.githubusercontent.com/Dong-learn9/TVBox-zyjk/refs/heads/main/tvbox2.json",
    "欧歌":"https://raw.githubusercontent.com/ls125781003/tvboxtg/refs/heads/main/欧歌/api.json",
    "摸鱼儿":"https://raw.githubusercontent.com/ls125781003/tvboxtg/refs/heads/main/摸鱼儿/api.json",
    "天天开心":"https://raw.githubusercontent.com/ls125781003/tvboxtg/refs/heads/main/天天开心/api.json",
    "drpy_t3":"https://raw.githubusercontent.com/ls125781003/tvboxtg/refs/heads/main/drpy_t3/api.json",
    "PG_api":"https://raw.githubusercontent.com/ls125781003/tvboxtg/refs/heads/main/PG/api.json",
    "PG_jsm":"https://raw.githubusercontent.com/ls125781003/tvboxtg/refs/heads/main/PG/jsm.json",
    'gao':'https://raw.githubusercontent.com/gaotianliuyun/gao/master/js.json',
    'bobyang3':'https://raw.githubusercontent.com/bobyang3/tvbox/refs/heads/own/jsm.json',
    '运输车':'https://weixine.net/ysc.json',
    "喵影视":"http://meowtv.top/tv",
    "FongMi_fish2018":"http://www.fish2018.us.kg/z/FongMi.json",
    "liucn":"https://raw.liucn.cc/box/m.json",
    'rx_js':'https://rxsub.eu.org/tvbox/js.json',
  }

def list_rm(urlList):#列表去重
    begin = 0
    rm = 0
    length = len(urlList)
    print(f'\n-----去重开始-----\n')
    while begin < length:
        proxy_compared = urlList[begin]
        begin_2 = begin + 1
        while begin_2 <= (length - 1):
            if proxy_compared == urlList[begin_2]:
                urlList.pop(begin_2)
                length -= 1
                begin_2 -= 1
                rm += 1
            begin_2 += 1
        begin += 1
    print(f'重复数量 {rm}\n-----去重结束-----\n')
    print(f'剩余总数 {str(len(urlList))}\n')
    return urlList
    
def saveList(configList,file_addr):#保存文件
  
    if configList:
        print('保存' + file_addr + '文件')
        file=open(file_addr,"w")
        file.write('\n'.join(configList))
        file.close()
        print('抓取时间：\t',datetime.now())

def saveConfig(customConfig,json_addr):#保存json文件
    if customConfig:
    # 配置customConfig及写入文件
        print('保存配置' + json_addr)
        with open(json_addr, "w",encoding='utf-8') as file:
        # 使用json.dump将数据写入文件
            json.dump(customConfig,file,indent=2,ensure_ascii=False)
            print('抓取时间：\t',datetime.now())

def getUrl_200(url): #检测网站是否可用（可在其中添加电影网的特征码）,可用返回False
    try:
        r=requests.get(url, timeout=3.0)
        if r.status_code==200:
            return False
        else:
            return True
    except Exception as e: 
        return True

class Js:#get js

    def down_libs(libs_addr):#下载js库文件
        nowtime = datetime.now()
        if nowtime.day%2 == 0:#配合每周更新tvbox，就相当于半月更新一次
            #下载库文件
            drpy_libs = requests.get('https://api.github.com/repos/n3rddd/N3RD/contents/JN/dr_py/libs/?ref=master').json()
            for lib in drpy_libs:
                libfile_addr = libs_addr + lib['name']
                response = requests.get(lib['download_url'])
                with open(libfile_addr, "wb") as f:
                    f.write(response.content)

    def getUrl_signJs(url): #检测网站是否可用（可在其中添加电影网的特征码）,可用返回False
        signs = ['电影','电视剧','连续剧','剧场','韩剧','综艺','动漫','美剧','热播','上映','国产','港台','電影','電視劇','綜藝','動漫']
        try:
            r=requests.get(url, timeout=5.0)
            if r.status_code==200:
                #return False
                for sign in signs:
                    if sign in r.text:
                        return False
                return True
            else:
                return True
        except Exception as e: 
            return True

    def get_ilive_js(site,jsList,bar,goodlist,bad):#在js的文件中，找到电影网站
        ilive ={'name':'','url':''}
        try:
            r=requests.get(site['ext'], timeout=5.0)
            if r.status_code==200:
                content = r.text
                host = None
                if content:
                    if 'quickSearch: 0' not in content and 'quickSearch:0' not in content:
                        content1 = re.sub('// host:','del content',content)
                        host = re.findall(r"host:'(.*?)',", content1)
                        if host:
                            if Js.getUrl_signJs(host[0]):
                                #print('移除：'+str(host[0]))
                                jsList.remove(site)
                                bad.append(site)
                            else:
                                ilive['name'] = site['name']
                                ilive['url']= host[0]
                                goodlist.append(ilive)
                        else:
                            host = re.findall(r"host: '(.*?)',", content1)
                            if host:
                                if Js.getUrl_signJs(host[0]):
                                    #print('移除：'+str(host[0]))
                                    jsList.remove(site)
                                    bad.append(site)
                                else:
                                    ilive['name'] = site['name']
                                    ilive['url']= host[0]
                                    goodlist.append(ilive)
                            else:
                                host = re.findall(r'host: "(.*?)",', content1)
                                if host:
                                    if Js.getUrl_signJs(host[0]):
                                        #print('移除：'+str(host[0]))
                                        jsList.remove(site)
                                        bad.append(site)
                                    else:
                                        ilive['name'] = site['name']
                                        ilive['url']= host[0]
                                        goodlist.append(ilive)
                                        
                                else:
                                    host = re.findall(r'"host": "(.*?)",', content1)
                                    if host:
                                        if Js.getUrl_signJs(host[0]):
                                            #print('移除：'+str(host[0]))
                                            jsList.remove(site)
                                            bad.append(site)
                                        else:
                                            ilive['name'] = site['name']
                                            ilive['url']= host[0]
                                            goodlist.append(ilive)
                                    else:
                                        #print('未搜索到js文件中的url地址,移除：'+str(site['ext']))
                                        jsList.remove(site)
                                        bad.append(site)
                    elif 'filterable:1' in content or 'filterable: 1' in content:
                        content1 = re.sub('// host:','del content',content)
                        host = re.findall(r"host:'(.*?)',", content1)
                        if host:
                            if Js.getUrl_signJs(host[0]):
                                #print('移除：'+str(host[0]))
                                jsList.remove(site)
                                bad.append(site)
                            else:
                                ilive['name'] = site['name']
                                ilive['url']= host[0]
                                goodlist.append(ilive)
                        else:
                            host = re.findall(r"host: '(.*?)',", content1)
                            if host:
                                if Js.getUrl_signJs(host[0]):
                                    #print('移除：'+str(host[0]))
                                    jsList.remove(site)
                                    bad.append(site)
                                else:
                                    ilive['name'] = site['name']
                                    ilive['url']= host[0]
                                    goodlist.append(ilive)
                            else:
                                host = re.findall(r'host: "(.*?)",', content1)
                                if host:
                                    if Js.getUrl_signJs(host[0]):
                                        #print('移除：'+str(host[0]))
                                        jsList.remove(site)
                                        bad.append(site)
                                    else:
                                        ilive['name'] = site['name']
                                        ilive['url']= host[0]
                                        goodlist.append(ilive)
                                        
                                else:
                                    host = re.findall(r'"host": "(.*?)",', content1)
                                    if host:
                                        if Js.getUrl_signJs(host[0]):
                                            #print('移除：'+str(host[0]))
                                            jsList.remove(site)
                                            bad.append(site)
                                        else:
                                            ilive['name'] = site['name']
                                            ilive['url']= host[0]
                                            goodlist.append(ilive)
                                    else:
                                        #print('未搜索到js文件中的url地址,移除：'+str(site['ext']))
                                        jsList.remove(site)
                                        bad.append(site)
                    else:
                        #print('未搜索到js文件中的url地址,移除：'+str(site['ext']))
                        jsList.remove(site)
                        bad.append(site)
            else:
                #print('获取js文件中的url时,js文件返回的不是code==200 : '+ str(site['ext']))
                jsList.remove(site)
                bad.append(site)
        except Exception as e:  
            #print('获取js文件中的url时,出错了（可能是没有ext段） = ' + str(site))
            bad.append(site)
            jsList.remove(site)
        bar.update(1)
    
    def check_url_js(jsList):#检测js影视网站是否可用,返回可用的数据
        print("check_url_js begin！")
        goodlist = []
        bad = []
        
        #进度条添加
        url_list_len = len(jsList)
        print("需要检测的sites个数：" + str(url_list_len))
        thread_max_num = threading.Semaphore(64)
        bar = tqdm(total=url_list_len, desc='get ilive：')
        thread_list = []

        for site in jsList[:]:
            try:
                #为每个URL创建线程
                t = threading.Thread(target=Js.get_ilive_js, args=(site,jsList,bar,goodlist,bad))
                #加入线程池
                # 加入线程池并启动
                thread_list.append(t)
                t.daemon=True
                t.start()
            except Exception as e: 
                pass
        #等待所有线程完成，配合上面的t.daemon
        for t in thread_list:
            t.join()
        bar.close() #进度条结束
        
        url_list_len = len(jsList)
        print('检测完成后sites总数：'+str(url_list_len))
        
        print('good总数：'+str(len(goodlist)))
        print('bad总数：'+str(len(bad)))
        
        #清理重复
        begin = 0
        rm = 0
        length = len(goodlist)
        print(f'\n-----清理重复JS开始-----\n')
        while begin < length:
            begin_2 = begin + 1
            while begin_2 <= (length - 1):
                if goodlist[begin]['url'] == goodlist[begin_2]['url']:
                    goodlist.pop(begin_2)
                    length -= 1
                    begin_2 -= 1
                    rm += 1
                begin_2 += 1
            begin += 1
        print(f'重复数量 {rm}\n-----清理重复JS结束-----\n')
        #print(f'剩余总数 {str(len(goodlist))}\n')
        for site in jsList[:]:
            live = False
            for ilive in goodlist:
                if ilive['name']  == site['name']:
                    live = True
            if live == False:
                jsList.remove(site)
        print(f'jsList剩余总数 {str(len(jsList))}\n')
        #saveConfig(goodlist,'good.txt')
        return jsList
        
    def get_url_js(key,jsonText):
        newlist =[]
        try:
            #用json格式载入数据
            config=json5.loads(jsonText)
            #删除数据，只留下自己想要的电影网
            i = 0
            for site in config['sites']:
                #print(site)
                try:
                    if '.js' in site['api'] and '.js' in site['ext']:
                        newlist.append(site)
                        i = i + 1
                except Exception as e: 
                    pass
            print(f"{key}收集到{ str(i) }个js site")
            return newlist
        except Exception as e:  
            print(e)
            return None    

    def fetch_all_js(configList):
        #用到的目录地址
        api_file = './js.json'
        jar_addr = './jar/js.jar'
        js_addr = './js/'
        js_log_addr = './log/log_js.json'
        libs_addr = './libs/'
        lib_addr = './libs/drpy2.min.js'
        
        #更新lib库
        Js.down_libs(libs_addr)
        #收集js
        jsList = []
        for key,value in configList.items():
            sites=Js.get_url_js(key,value)
            if sites:
                jsList.extend(sites)#将sites内容逐个加入列表
        print(f'总共收集到{str(len(jsList))}个js site点')
        
        #过滤N3rddd网站里不想要的JS
        #删除数据，只留下自己想要的电影网
        signs = ['[书]','[听]','[盘]','[球]','[儿]','[漫]','[画]','[密]','[飞]','[画密飞]','[央]','[资]','[搜]','[自动]','📀','直播','听书','音乐','MV','动漫','DJ','MV','XVIDEOS','纸条','黑料','蜻蜓FM','电视 |','夸克 |','少儿 |','弹幕 |','直播 |','体育 |','相声 |','评书 |','格斗 |','网盘 |','动漫 |','音频 |','广播 |','听书 |','聚合 |','MV |']
        i = 0
        lens = len(jsList)
        print('原数据sites个数：'+ str(lens))
        for site in jsList[:]:
            for sign in signs:
                if sign in site["name"]:
                    jsList.remove(site)
                    break
        print('过滤后sites个数：'+ str(len(jsList)))
        #检测可用的JS
        jsList = Js.check_url_js(jsList)
        
        #修改配置开始
        #先找到json模板
        try:
            allConfig = json5.loads(configList['n3rddd_js'])
        except KeyError as e:
            print('n3rddd_js no content')
            try:
                allConfig = json5.loads(configList['rx_js'])
            except KeyError as e:
                print('rx no content')
                print('本次抓取失败js，原因是最终配置时，找不到可用的json文件当模板')
                return 
        #修改jar地址
        #allConfig['spider'] = './n3rddd/js.jar'#使用js的jar，vod原jar文件大
        #下载jar文件，并改地址为本地地址
        if 'md5' not in allConfig['spider']:
            response = requests.get(allConfig['spider'])
        else:
            url = re.search(r'(.*);md5;', config['spider']).group(1)
            response = requests.get(url)
        with open(jar_addr, "wb") as f:
            f.write(response.content)
        allConfig['spider'] = jar_addr
        """
        #下载jar文件，并改地址为本地地址
        url = re.search(r'(.*);md5;', config['spider']).group(1)
        response = requests.get(url)
        #jarname = config['spider'].split("/")[-1]
        #jar_addr = all_addr + jarname 
        with open(jar_addr, "wb") as f:
            f.write(response.content)
        config['spider'] = jar_addr
        
        response = requests.get(config['spider'])
        jarname = config['spider'].split("/")[-1]
        jarname = jarname.split(";")[0]
        jar_addr = all_addr + jarname 
        with open(jar_addr, "wb") as f:
            f.write(response.content)
        config['spider'] = './' + jarname
        """
        #改名和设置可以搜索,下载js文件
        now = datetime.now()
        nowtime = now.timestamp()
        with open(js_log_addr, "r",encoding='utf-8') as file:
            log_str = file.read()
        log_json = json.loads(log_str)  
        allConfig["sites"] = []#清空模板sites内容
        xuhao = 1
        for site in jsList:#将检测完成的list添加到sites
            #改名
            site['name'] = re.sub(r'雷蒙|DRPY|影视 [|]','',site['name'])#https://blog.csdn.net/Dontla/article/details/134602233
            site['name'] = re.sub(r'\u00a9|\u00ae|[\u2000-\u3300]|[\ud83c-\ud83e][\ud000-\udfff]|[\s]|[(]|[)]|[|]|-|[0-9]','',site['name'])#emoji 对应的编码区间用正则表达https://blog.csdn.net/wzy0623/article/details/130579863
            site['name'] = str(xuhao)+ '-' + site['name']
            xuhao = xuhao + 1
            #设置可以搜索
            site["searchable"] = 1
            site["quickSearch"] = 1
            
            #库文件地址改成本地地址
            site['api'] = lib_addr
            #下载JS文件，并把地址改成本地地址    
            #用法详解https://blog.csdn.net/jialibang/article/details/84989279
            ## 以/为分隔符，从后面切1刀
            jsname = site['ext'].split("/")[-1]
            if jsname:
                jsfile_addr = js_addr + jsname
                response = requests.get(site['ext'])
                with open(jsfile_addr, "wb") as f:
                    f.write(response.content)
                site['ext'] = jsfile_addr
                #把未添加到log的js网站添加进去
                i = False
                new_dict = {"name":"","更新时间":'',"时间戳":'',"最后更新时间":''}
                for ys in log_json:
                    if jsname in ys['name']:
                        i = True
                        break
                if i ==True:
                    ys['最后更新时间'] = str(now)
                    ys['时间戳'] = nowtime
                else:#不在log中    
                    new_dict['name'] = jsname
                    new_dict['更新时间'] = str(now)
                    new_dict['时间戳'] = nowtime
                    log_json.append(new_dict)
            #添加到新sites
            allConfig['sites'].append(site)
        #查找长时间不能用的js文件，删除
        for ys in log_json:
            sign = False
            for site in allConfig['sites']:
                if ys['name'] in site['ext']:
                    sign = True
                    break
            if sign == False:
                if int(nowtime) - int(ys['时间戳']) > 5270400:#文件2个月未使用,5270400是时间戳中的2个月
                    old_file = js_addr + ys['name']
                    log_json.remove(ys)
                    try:
                        os.remove(old_file)
                    except Exception as e:
                        pass
        #保存js日志
        saveConfig(log_json,js_log_addr)

        #添加更新日期
        allConfig['sites'][0]['name'] = '[js]' + datetime.today().strftime('%y-%m-%d')
        #保存json文件
        saveConfig(allConfig,api_file)
        return jsList
        
class Xbpq:#get XBPQ
    def getUrl_signXbpq(url): #检测网站是否可用（可在其中添加电影网的特征码）,可用返回False
        signs = ['电影','电视剧','连续剧','剧场','韩剧','综艺','动漫','美剧','热播','上映','国产','港台','電影','電視劇','綜藝','動漫']
        try:
            r=requests.get(url, timeout=5.0)
            if r.status_code==200:
                #return False
                for sign in signs:
                    if sign in r.text:
                        return False
                return True
            else:
                return True
        except Exception as e: 
            return True

    def get_ailve_XBPQ(site,config,bar):
        try:
            if Xbpq.getUrl_signXbpq(site['ext']['主页url']):
                config.remove(site)
        #except Exception as e:#万能异常
        except KeyError as e:#没有关键字
            #print('no url' + site['name'])
            config.remove(site)
        except Exception as e:
            config.remove(site)
        bar.update(1)

    def check_url_XBPQ(xbpqList):  
        #用json格式载入数据
        #xbpqList=json5.loads(xbpqList)   #本地不用打开,github上 打开
        url_list_len = len(xbpqList)
        print("需要检测的XBPQ sites个数：" + str(url_list_len))
        thread_max_num = threading.Semaphore(64)
        bar = tqdm(total=url_list_len, desc='get ilive：')
        thread_list = []

        for site in xbpqList[:]:
            try:
                #为每个URL创建线程
                t = threading.Thread(target=Xbpq.get_ailve_XBPQ, args=(site,xbpqList,bar))
                #加入线程池
                # 加入线程池并启动
                thread_list.append(t)
                t.daemon=True
                t.start()
            except Exception as e: 
                #bar.update(1)
                pass
        #等待所有线程完成，配合上面的t.daemon
        for t in thread_list:
            t.join()
        bar.close() #进度条结束
        
        url_list_len = len(xbpqList)
        print("检测完成的XBPQ sites个数：" + str(url_list_len))
        return xbpqList
    
    def get_url_xbpq(key,jsonText):
        newlist =[]
        try:
            #用json格式载入数据
            config=json5.loads(jsonText)
            #删除数据，只留下自己想要的电影网
            i = 0
            for site in config['sites']:
                #print(site)
                if 'XBPQ' in site['api'] or 'xbpq' in site['api']:
                    newlist.append(site)
                    i = i + 1
            print(f"{key}收集到{ str(i) }个xbpq site")
            return newlist
        except Exception as e:  
            print(e)
            return None    
            
    def fetch_all_xbpq(configList):
        xbpqList = []
        for key,value in configList.items():
            sites=Xbpq.get_url_xbpq(key,value)
            if sites:
                xbpqList.extend(sites)#将url_vod内容逐个加入列表
        print(f'总共收集到{str(len(xbpqList))}个xbpq site点')
        #检测是否可用
        xbpqList = Xbpq.check_url_XBPQ(xbpqList)
        #修改配置开始
        #先找到json模板
        try:
            allConfig = json5.loads(configList['n3rddd_js'])
        except KeyError as e:
            print('n3rddd_js no content')
            try:
                allConfig = json5.loads(configList['rx_js'])
            except KeyError as e:
                print('rx no content')
                print('本次抓取失败xbpq，原因是最终配置时，找不到可用的json文件当模板')
                return 
        #修改jar地址
        allConfig['spider'] = './jar/js.jar'#使用js的jar，vod原jar文件大
        #改名和设置可以搜索
        allConfig["sites"] = []#清空模板sites内容
        xuhao = 1
        for site in xbpqList:#将检测完成的list添加到sites
            #改名
            site['name'] = re.sub(r'雷蒙|DRPY|影视 [|]','',site['name'])#https://blog.csdn.net/Dontla/article/details/134602233
            site['name'] = re.sub(r'\u00a9|\u00ae|[\u2000-\u3300]|[\ud83c-\ud83e][\ud000-\udfff]|[\s]|[(]|[)]|[|]|-|[0-9]','',site['name'])#emoji 对应的编码区间用正则表达https://blog.csdn.net/wzy0623/article/details/130579863
            site['name'] = str(xuhao)+ '-' + site['name']
            xuhao = xuhao + 1
            #设置可以搜索
            site["searchable"] = 1
            site["quickSearch"] = 1
            allConfig['sites'].append(site)

        #添加更新日期
        allConfig['sites'][0]['name'] = '[xbpq]' + datetime.today().strftime('%y-%m-%d')
        #保存json文件
        saveConfig(allConfig,'xbpq.json')
        return xbpqList

class Vod: #get vod
    def getUrl_signVod(url): #检测网站是否可用（可在其中添加电影网的特征码）,可用返回False
        try:
            r=requests.get(url, timeout=3.0)
            if r.status_code==200:
                #provide/vod
                if 'provide/vod' in url:
                    host = re.findall("(.*?)/provide/vod", url)
                    if host:
                        newurl = host[0] + '/provide/vod/' + '?wd=1'  #添加搜索代码
                        r1=requests.get(newurl, timeout=3.0)
                        if r != r1:
                            try:
                                r1json = json5.loads(r1.text)
                                if '1' in r1json['list'][0]['vod_name']:
                                    return False
                            except Exception as e:  
                                pass
                elif 'api.php' in url:#不是标准的provide/vod
                    newurl = url + '?wd=1'  #添加搜索代码
                    r1=requests.get(newurl, timeout=3.0)
                    if r != r1:
                        try:
                            r1json = json5.loads(r1.text)
                            if '1' in r1json['list'][0]['vod_name']:
                                return False
                        except Exception as e:  
                            pass
                elif '.php' in url.split("/")[-1]:#T4可用站
                    signs = ['{"code":1','影视','电影','连续剧','综艺','动漫']
                    for sign in signs:
                        if sign in r.text:
                            return False
            return True
        except Exception as e: 
            return True
            
    def get_ilive_vod(site,jsconfig,bar,goodlist,bad):
        if Vod.getUrl_signVod(site['api']):
            jsconfig.remove(site)
        bar.update(1)
            
    def check_url_vod(vodList):
        print("check_vod_url begin！")
        goodlist = []
        bad = []
        
        #可用测试,进度条添加
        #jsconfig=json5.loads(vodList)
        url_list_len = len(vodList)
        print("vod需要检测的sites个数：" + str(url_list_len))
        thread_max_num = threading.Semaphore(64)
        bar = tqdm(total=url_list_len, desc='get ilive：')
        thread_list = []
        for site in vodList[:]:
            try:
                #为每个URL创建线程
                t = threading.Thread(target=Vod.get_ilive_vod, args=(site,vodList,bar,goodlist,bad))
                #加入线程池
                # 加入线程池并启动
                thread_list.append(t)
                t.daemon=True
                t.start()
            except Exception as e: 
                #bar.update(1)
                pass
        #等待所有线程完成，配合上面的t.daemon
        for t in thread_list:
            t.join()
        bar.close() #进度条结束
        
        url_list_len = len(vodList)
        print('vod检测完成后sites总数：'+str(url_list_len))
        
        #print('good总数：'+str(len(goodlist)))
        #print('bad总数：'+str(len(bad)))
        #saveList(goodlist,'good.txt')
        return vodList

    def get_url_vod(key,jsonText):
        newlist =[]
        try:
            #用json格式载入数据
            config=json5.loads(jsonText)
            #删除数据，只留下自己想要的电影网
            i = 0
            for site in config['sites']:
                #print(site)
                if '/vod' in site['api'] or '.php' in site['api']:
                    newlist.append(site)
                    #print(site['api'])
                    i = i + 1
            print(f"{key}收集到{ str(i) }个vod site")
            return newlist
        except Exception as e:  
            print(e)
            return None     
            
    def fetch_all_vod(configList):
        vodList = []
        for key,value in configList.items():
            sites=Vod.get_url_vod(key,value)
            if sites:
                vodList.extend(sites)#将sites内容逐个加入列表
        
        #获取hiker抓到的list，添加到列表中
        r = requests.get('https://rxsub.eu.org/hiker/api/api_good.txt')
        vodurllist = re.split(r'\n+',r.text)
        print("hiker vod list 原个数：" + str(len(vodurllist)))
        for site in vodList:
            i = 0
            l = len(vodurllist)
            while i<l:
                if vodurllist[i] in site['api']:
                    #site['api'] = vodurllist[i]
                    vodurllist.pop(i)
                    l -= 1
                    i -= 1
                i += 1    
        print("hiker vod list 删除完后个数：" + str(len(vodurllist)))
        #把剩余的添加到列表中
        i=1
        for url in vodurllist:
            newurl = {"key": "","name": "","type": 1,"api": "","searchable": 1,"quickSearch": 1}
            newurl['key'] = 'hiker-'+ str(i)
            newurl['name'] = 'hiker-'+ str(i)
            newurl['api'] = url
            vodList.append(newurl)
            i += 1
        print(f'总共收集到{str(len(vodList))}个vod site点')
        
        #去重开始
        begin = 0
        rm = 0
        length = len(vodList)
        print(f'\n-----api去重开始-----\n')
        while begin < length:
            proxy_compared = vodList[begin]
            begin_2 = begin + 1
            while begin_2 <= (length - 1):
                if proxy_compared['api'] == vodList[begin_2]['api']:
                    vodList.pop(begin_2)
                    length -= 1
                    begin_2 -= 1
                    rm += 1
                begin_2 += 1
            begin += 1
        print(f'vod_api重复数量 {rm}\n-----去重结束-----\n')
        print(f'去重后总数 {str(len(vodList))}\n')
        
        #检测vod网站
        vodList = Vod.check_url_vod(vodList)
        
        #查找重复网址+重复key重命名
        begin = 0
        rm = 0
        length = len(vodList)
        print(f'\n-----查找重复网址-----\n')
        while begin < length:
            proxy_compared = vodList[begin]
            begin_2 = begin + 1
            rmname = 1
            while begin_2 <= (length - 1):
                if proxy_compared['api'] in vodList[begin_2]['api'] or vodList[begin_2]['api'] in proxy_compared['api']:
                    vodList.pop(begin_2)
                    length -= 1
                    begin_2 -= 1
                    rm += 1
                #elif proxy_compared['key'] == vodList[begin_2]['key'] or proxy_compared['key'] in vodList[begin_2]['key'] or vodList[begin_2]['key'] in proxy_compared['key']:
                elif proxy_compared['key'] == vodList[begin_2]['key']:
                    vodList[begin_2]['key'] = vodList[begin_2]['key'] + str(rmname)
                    rmname = rmname + 1
                begin_2 += 1
            begin += 1
        print(f'vod重复网址数量 {rm}\n-----去重结束-----\n')
        print(f'去重后总数 {str(len(vodList))}\n')

        
        #修改配置开始
        #先找到json模板
        try:
            allConfig = json5.loads(configList['n3rddd_js'])
        except KeyError as e:
            print('n3rddd no content')
            try:
                allConfig = json5.loads(configList['rx_js'])
            except KeyError as e:
                print('rx no content')
                print('本次抓取失败vod，原因是最终配置是，找不到可用的json文件当模板')
                return 
        
        #改名和设置可以搜索
        allConfig["sites"] = []#清空模板sites内容
        xuhao = 1
        for site in vodList:#将检测完成的list添加到sites
            #改名
            site['name'] = re.sub(r'雷蒙|DRPY|影视 [|]','',site['name'])#https://blog.csdn.net/Dontla/article/details/134602233
            site['name'] = re.sub(r'\u00a9|\u00ae|[\u2000-\u3300]|[\ud83c-\ud83e][\ud000-\udfff]|[\s]|[(]|[)]|[|]|-|[0-9]','',site['name'])#emoji 对应的编码区间用正则表达https://blog.csdn.net/wzy0623/article/details/130579863
            site['name'] = str(xuhao)+ '-' + site['name']
            xuhao = xuhao + 1
            #设置可以搜索
            site["searchable"] = 1
            site["quickSearch"] = 1
            allConfig['sites'].append(site)
        
        #修改jar地址
        #allConfig['spider'] = './jar/js.jar'#使用js的jar，vod原jar文件大
        allConfig['spider'] = './jar/bili.jar'#bili.jar只有90kb
        #添加更新日期
        allConfig['sites'][0]['name'] = '[vod]' + datetime.today().strftime('%y-%m-%d')
        #保存json文件
        saveConfig(allConfig,'vod.json')
        
        #添加儿童乐园
        babyConfig = {}
        babyConfig['spider'] = './jar/bilibili.jar'#儿童乐园使用
        babyConfig["logo"] = allConfig["logo"]
        babyConfig["wallpaper"] = allConfig["wallpaper"]
        babyConfig["sites"] = allConfig['sites']
        babyConfig["sites"].insert(1,rx)#在任意位置添加数据
        babyConfig["lives"] = allConfig["lives"]
        saveConfig(babyConfig,'baby.json')
        
        #更新到网盘


        return vodList

class GUC:#get url config
    def setParise(customConfig,configList):#diy 解析未开发
        print('设置解析开始')
        # if customConfig :
        #   # 提取解析parses
        #   parses=[]
        #   if '香雅情' in configList and not parses:
        #     parses=configList['香雅情']['parses']
        #     customConfig['parses']=parses
        #   if 'OK佬' in configList and not parses:
        #     parses=configList['OK佬']['parses']
        #     customConfig['parses']=parses
        print('设置解析结束')
     
    def encodeBase64(content):#diy lives 里面使用的
        content='**'+base64.b64encode(content.encode('utf-8')).decode('utf-8')
        print(content)
        return content 

    def supplementAddr(url,config):# 补充相对地址
        
        host =url[:url.rfind('/')]
        #print('host:',host)
        pattern=r'"\./.*?"'
        config=re.sub(pattern,lambda x:"\""+host+x.group(0)[2:],config)
        #result=re.findall(pattern,config)
        #print(config)
        return config

    def isJson(content):#检测是否是Json5数据内容
        try:
            data=json5.loads(content)
            return True
        except Exception as e:  
            return False
      
    def FindResult(content,key=None):#找到json文件内容

      # 解析加密 以8个字母加**的内容
      pattern = re.compile(r"[A-Za-z0]{8}\*\*")
      result = pattern.search(content) 
      if result:
        try:
            #print(result.group())
            #print(content.index(result.group()))
            content = content[content.index(result.group()) + 10:]
            data=base64.b64decode(content).decode('utf-8')
            #print(data)
            return data
        except Exception as e:
          return None
        
      # 解析 以**开头的内容 主要在lives配置加密中
      if content.startswith('**'):
        try:
            #print(result.group())
            #print(content.index(result.group()))
            content = content[2:]
            data=base64.b64decode(content).decode('utf-8')
            #print(data)
            return data
        except Exception as e:
          return None
        
      # 解析 以2423开头的内容
      if content.startswith('2423'):
            return '2423开头内容尚末解析'
      
      # 放后面主要防止不是json的为判断为json
      if GUC.isJson(content):
        #print('========= is json5')
        return content
      
      elif key and GUC.isJson(content):
        try:
          aes = AES.new(key,AES.MODE_ECB)
          data=aes.decrypt(content)
          return data
        except Exception as e:
          return None
      
      else:
        #return '无法解析内容'
        return None

    def getConfig(key,value,configList,bar):#获取网站的json内容，将获取的config返回
        headers={
        "User-Agent":"okhttp/3.15",
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
        }
        try:
            r=requests.get(value,headers=headers, timeout=3.0)
            if r.status_code==200:
                r.encoding='utf-8'    #编码方式
                jsonText=GUC.FindResult(r.text,'')
                #print(jsonText)
            if jsonText:
                jsonText = GUC.supplementAddr(value,jsonText)#添加文件的相对地址
                #return jsonText
                configList[key]=jsonText
        except requests.exceptions.RequestException as e:  
            print(e)
        except Exception as e: 
            pass
            print(f'获取内容失败：{value}')
        bar.update(1)
        
    def getConfigs(list):#获取列表网站的json内容，将获取的内容存入列表configList返回
        print('开始收集网站json：' + str(datetime.now()))
        configList={}
        """
        for key,value in list.items():
            config=GUC.getConfig(value)
            if config:
                configList[key]=config
        return configList
        """
        #进度条添加
        list1=list
        url_list_len = len(list1.items())
        thread_max_num = threading.Semaphore(64)
        bar = tqdm(total=url_list_len, desc='fetch json:')
        thread_list = []
        for key,value in list.items():
            try:
                #为每个URL创建线程
                t = threading.Thread(target=GUC.getConfig, args=(key,value,configList,bar))
                #加入线程池
                # 加入线程池并启动
                thread_list.append(t)
                t.daemon=True
                t.start()
            except Exception as e: 
                #bar.update(1)
                pass
        #等待所有线程完成，配合上面的t.daemon
        for t in thread_list:
            t.join()
        bar.close() #进度条结束
        print('收集网站json结束：' + str(datetime.now()))
        return configList
        

def diy_fan(configList):
    #饭太硬配置
    md5_addr = "./log/md5.ini"
    #my_fan_url = r'http://4901.kstore.space/fan.txt'
    my_fan_url = r'http://d.kstore.dev/download/4901/tvbox/jar/fan.jar'
    fan_json_addr = './fan.json'
    fan_jar_addr = './jar/fan.jar'
    #rx = {"key": "儿童乐园","name": "儿童乐园","type":3,"api":"csp_Bili","playerType":1,"ext": "http://4901.kstore.space/儿童乐园.json"}
    #rx = {"key": "儿童乐园","name": "儿童乐园","type": 3,"api": "csp_Bili","playerType": 1,"ext": {"json": "http://4901.kstore.space/儿童乐园.json"}}
    rx_fan = {"key": "儿童乐园","name": "儿童乐园","type": 3,"api": "csp_Bili","searchable":0,"quickSearch":0,"filterable":1,"ext": {"json": "http://d.kstore.dev/download/4901/tvbox/json/儿童乐园fan.json"}}
    #rx = {"key":"儿童乐园","name":"儿童乐园","type":3,"api":"csp_Bili","style":{"type":"rect","ratio":1.597},"searchable":0,"quickSearch":0,"changeable":0,"filterable":1,"ext":{"json":"http://d.kstore.dev/download/4901/儿童乐园fan.json"}}
    #rx = {"key": "儿童乐园","name": "儿童乐园","type": 3,"api": "csp_Bili","searchable":0,"quickSearch":0,"filterable":1,"ext": {"json": "http://4901.kstore.space/儿童乐园.json"}}
    #使用上面简化的电视上才能播放

    #如果未获取到fan的内容
    if 'fan' not in configList:
        print('fan' + ' : KeyError_应该是网址变了，没获取到最新的json数据,去找最新接口地址！')
        #写入错误日志
        file = open("./log/log.txt", "a")
        file.write('\n' + str(datetime.now()) + ' : ' + 'fan' + ' : KeyError_应该是网址变了，没获取到最新的json数据,去找最新接口地址！')
        file.close()
        return
    #开始DIY
    print('hello,饭太硬!')
    config = configparser.ConfigParser()
    config.read(md5_addr)
    m = hashlib.md5()
    str_json = str(configList['fan'])
    m.update(str_json.encode('utf-8'))
    md5 = m.hexdigest()

    try:
        old_md5 = config.get("fan_md5", "conf")
        if md5 == old_md5:
            print("No update needed")
            return
    except:
        pass
    
    # Update md5.conf
    config.set("fan_md5", "conf", md5)
    with open(md5_addr, "w") as f:
        config.write(f)
 
    #将数据转成json5格式
    json_format = json5.loads(configList['fan'])
    #获取jar地址和md5
    content = json_format["spider"]
    url = re.search(r'(.*);md5;', content).group(1)
    jmd5 = re.search(r';md5;(\w+)', content).group(1)
    #对比jar的md5，不同就将更新md5和jar
    current_md5 = config.get("fan_md5", "jar").strip()
    if jmd5 != current_md5:
        # Update md5
        config.set("fan_md5", "jar", jmd5)
        with open(md5_addr, "w") as f:
            config.write(f)
        # Update jar
        response = requests.get(url)
        with open(fan_jar_addr, "wb") as f:
            f.write(response.content)
    
    ####diy修改json内容#############：
    
    #修改jar的新地址
    content = re.sub(url, my_fan_url, content)
    json_format["spider"] = content
    
    #增加修改时间,添加儿童乐园
    json_format["sites"][0]['name'] = '[饭]' + datetime.today().strftime('%y-%m-%d')
    json_format["sites"].insert(1,rx_fan)#在任意位置添加数据
    #json_format["sites"].append(rx)#在末尾追加数据
    """
    try:
        with open('vod.json', "r",encoding='utf-8') as file:
            vod_str = file.read()
            vod_json = json.loads(vod_str)
        #pop可用删除列表第一条带日期的
        #vod_json["sites"].pop(0)
        json_format["sites"].extend(vod_json["sites"])
    except Exception as e:
        print(e)
        print("添加vod sites时，出现的错误！")
        pass
    """
    #保存json文件
    saveConfig(json_format,fan_json_addr)
    #更新到网盘


def diy_feimao(configList):
    #肥猫配置
    md5_addr = "./log/md5.ini"
    my_feimao_url = r'http://d.kstore.dev/download/4901/tvbox/jar/feimao.jar'
    feimao_json_addr = './feimao.json'
    feimao_jar_addr = './jar/feimao.jar'  
    #rx = {"key": "儿童乐园","name": "儿童乐园","type":3,"api":"csp_Bili","playerType":1,"ext": "http://4901.kstore.space/儿童乐园.json"}
    rx_feimao = {"key":"儿童乐园","name":"儿童乐园","type":3,"api":"csp_Bili","searchable":0,"quickSearch":0,"changeable":0,"ext": "./json/儿童乐园.json"}
    #使用上面简化的电视上才能播放
    #rx = {"key":"儿童乐园","name":"儿童乐园","type":3,"api":"csp_Bili","searchable":0,"quickSearch":0,"filterable":1,"ext":"http://4901.kstore.space/儿童乐园.json"}

    #如果未获取到feimao的内容
    if 'feimao' not in configList:
        print('feimao' + ' : KeyError_应该是网址变了，没获取到最新的json数据,去找最新接口地址！')
        #写入错误日志
        file = open("./log/log.txt", "a")
        file.write('\n' + str(datetime.now()) + ' : ' + 'feimao' + ' : KeyError_应该是网址变了，没获取到最新的json数据,去找最新接口地址！')
        file.close()
        return
    #开始DIY
    print('hello,肥猫!')
    config = configparser.ConfigParser()
    config.read(md5_addr)
    m = hashlib.md5()
    str_json = str(configList['feimao'])
    m.update(str_json.encode('utf-8'))
    md5 = m.hexdigest()

    try:
        old_md5 = config.get("feimao_md5", "conf")
        if md5 == old_md5:
            print("No update needed")
            return
    except:
        pass
    # Update md5.conf
    config.set("feimao_md5", "conf", md5)
    with open(md5_addr, "w") as f:
        config.write(f)
 
    #将数据转成json5格式
    json_format = json5.loads(configList['feimao'])
    #获取jar地址和md5
    content = json_format["spider"]
    url = re.search(r'(.*);md5;', content).group(1)
    jmd5 = re.search(r';md5;(\w+)', content).group(1)
    #对比jar的md5，不同就将更新md5和jar
    current_md5 = config.get("feimao_md5", "jar").strip()
    if jmd5 != current_md5:
        # Update md5
        config.set("feimao_md5", "jar", jmd5)
        with open(md5_addr, "w") as f:
            config.write(f)
        # Update jar
        response = requests.get(url)
        with open(feimao_jar_addr, "wb") as f:
            f.write(response.content)
    
    ####diy修改json内容#############：
    
    #修改jar的新地址 - 肥猫的修改后出现影视接口问题，先不修改
    content = re.sub(url, my_feimao_url, content)
    json_format["spider"] = content
    
    #增加修改时间,添加儿童乐园
    json_format["sites"][0]['name'] = '[肥猫]' + datetime.today().strftime('%y-%m-%d')
    json_format["sites"].insert(1,rx_feimao)#在任意位置添加数据
    #json_format["sites"].append(rx)#在末尾追加数据
    """
    try:
        with open('vod.json', "r",encoding='utf-8') as file:
            vod_str = file.read()
            vod_json = json.loads(vod_str)  
        json_format["sites"].extend(vod_json["sites"])
    except Exception as e:
        print(e)
        print("添加vod sites时，出现的错误！")
        pass
    """
    #保存json文件
    saveConfig(json_format,feimao_json_addr)

if "__name__==__main__":#主程序开始
    configList=GUC.getConfigs(list)
    #customConfig=setConfig(configList)
    #setLives(customConfig,configList)
    #setParise还未开发
    #setParise(customConfig,configList)

    #获取数据
    Vod.fetch_all_vod(configList)
    Js.fetch_all_js(configList)
    #Xbpq.fetch_all_xbpq(configList)
    diy_fan(configList)
    diy_feimao(configList)

    """
    #获取n3rddd网址数据
    if configList['n3rddd']:
        get_github_n3rddd(configList['n3rddd'])
    else:
        print("未获取到网址json数据:" + list['n3rddd'])
    #获取gaotianliuyun网址数据
    if configList['gao']:
        get_github_gao(configList['gao'])
    else:
        print("未获取到网址json数据:" + list['gaotianliuyun'])
    """
    
    
