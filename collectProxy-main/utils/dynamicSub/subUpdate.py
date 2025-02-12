#!/usr/bin/env python3

from datetime import datetime
import json, re
import requests
import traceback
import yaml

config_path = './utils/dynamicSub/dynamic_config.yaml'
list_file_path = './utils/dynamicSub/subList_dynamic.json'
txt_list_file_path  = './sub/sources/subList_dynamic.txt'
headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.53"}

class update():
    def __init__(self,list_file_path):
        with open(list_file_path, 'r', encoding='utf-8') as f: # 载入订阅链接
            raw_list = json.load(f)
            self.raw_list = raw_list
        self.update_main()
    
    # 判断远程远程链接是否已经更新
    def url_updated(self,url): 
        s = requests.Session()
        try:
            resp = s.get(url, timeout=2)
            status = resp.status_code
        except Exception:
            status = 404
        if status == 200:
            url_updated = True
        else:
            url_updated = False
        return url_updated
    
    # 更新订阅列表
    def update_main(self):
        for sub in self.raw_list:
            current_remarks = sub ['remarks']
            try:  
                if current_remarks == 'timeUpdate':
                    new_url = self.timeUpdate(sub ['url'])
                    if new_url == sub ['url']:
                        print(f'No available update for ID {current_remarks}\n')
                    else:
                        sub['url'] = new_url
                        print(f'ID {current_remarks} url updated to {new_url}\n')       
                elif current_remarks == 'www.cfmem.com':
                    new_url = self.cfmemUpdate(sub ['url'])
                    if new_url == sub ['url']:
                        print(f'No available update for ID {current_remarks}\n')
                    else:
                        sub['url'] = new_url
                        print(f'ID {current_remarks} url updated to {new_url}\n')          
                elif current_remarks == 'mibei77':
                    new_url = self.mibei77Update(sub ['url'])
                    if new_url == sub ['url']:
                        print(f'No available update for ID {current_remarks}\n')
                    else:
                        sub['url'] = new_url
                        print(f'ID {current_remarks} url updated to {new_url}\n')   
                elif current_remarks == 'changfengoss':
                    new_url = self.changfenggossUpdate(sub ['url'])
                    if new_url == sub ['url']:
                        print(f'No available update for ID {current_remarks}\n')
                    else:
                        sub['url'] = new_url
                        print(f'ID {current_remarks} url updated to {new_url}\n')          
            except KeyError:
                print(f'{current_remarks} Url not changed! Please define update method.')
            #将更新完成的列表写入文件
            updated_list = json.dumps(self.raw_list, sort_keys=False, indent=2, ensure_ascii=False)
            file = open(list_file_path, 'w', encoding='utf-8')
            file.write(updated_list)
            file.close()
            
            #将更新完的订阅列表写入txt版文件
            with open(list_file_path, 'r', encoding='utf-8') as f:
                raw_list = json.load(f)
            output_list = []
            for index in raw_list:
                if '|' in index['url']:
                    urls= re.split(r'\|',index['url'])
                    if urls:
                        for url in urls:
                            output_list.append(url)
                else:
                    output_list.append(index['url'])
            
            #写入list.txt
            output_list_str = '\n'.join(output_list)        
            file = open(txt_list_file_path, 'w', encoding='utf-8')
            file.write(output_list_str)
            file.close()
            #更新config.yaml
            #打开读取 config.yaml    
            with open(config_path,encoding="UTF-8") as f:
                dict_url = yaml.load(f, Loader=yaml.FullLoader)
            for url in dict_url['sources']:
                if url['name'] == 'subs':
                    url['options']['urls'] = output_list
            #save  config.yaml
            with open(config_path, 'w',encoding="utf-8") as f:
                data = yaml.dump(dict_url, f,allow_unicode=True)

##########################################################################################
    def timeUpdate(self,current_url):
        #url = f'https://clashgithub.com/wp-content/uploads/rss/{today}.txt'
        #nowtime = datetime.now()
        #year = nowtime.year
        #month = nowtime.month
        #today = datetime.today().strftime('%Y%m%d') # 获取当天日期，格式为 YYYYMMDD,或者('%Y/%m/%Y%m%d')
        #s = str(year) + '/' + str(month) + '/' + str(today)
        
        newlist = []
        
        #github.com/pojiezhiyuanjun
        today = datetime.today().strftime('%m%d')
        new_url = 'https://raw.githubusercontent.com/pojiezhiyuanjun/freev2/master/' + today + '.txt'
        #链接是否已经更新
        if self.url_updated(new_url):
            newlist.append(new_url)

        #clashgithub.com
        today = datetime.today().strftime('%Y%m%d')# 获取当天日期，格式为 YYYYMMDD
        # 动态生成 URL，替换日期部分
        new_url = f'https://clashgithub.com/wp-content/uploads/rss/{today}.txt'
        #链接是否已经更新
        if self.url_updated(new_url):
            newlist.append(new_url)

        #nodefree.org
        new_url = datetime.today().strftime('https://nodefree.githubrowcontent.com/%Y/%m/%Y%m%d.yaml')
        #链接是否已经更新
        if self.url_updated(new_url):
            newlist.append(new_url)
        
        #v2rayshare.com
        new_url = datetime.today().strftime('https://v2rayshare.githubrowcontent.com/%Y/%m/%Y%m%d.yaml')
        #链接是否已经更新
        if self.url_updated(new_url):
            newlist.append(new_url)
        
        #oneclash.cc
        new_url = datetime.today().strftime('https://oneclash.githubrowcontent.com/%Y/%m/%Y%m%d.yaml')
        #链接是否已经更新
        if self.url_updated(new_url):
            newlist.append(new_url)
            
        #wenode.cc
        new_url = datetime.today().strftime('https://wenode.githubrowcontent.com/%Y/%m/%Y%m%d.yaml')
        #链接是否已经更新
        if self.url_updated(new_url):
            newlist.append(new_url)
        
        #www.naidounode.com
        new_url = datetime.today().strftime('https://www.naidounode.com/node/%Y%m%d-clash.yaml')
        #链接是否已经更新
        if self.url_updated(new_url):
            newlist.append(new_url)
        
        #free.datiya.com
        new_url = datetime.today().strftime('https://free.datiya.com/uploads/%Y%m%d-clash.yaml')
        #链接是否已经更新
        if self.url_updated(new_url):
            newlist.append(new_url)
            
        #a.nodeshare.xyz
        new_url = datetime.today().strftime('https://a.nodeshare.xyz/uploads/%Y/%-m/%Y%m%d.txt')
        #链接是否已经更新
        if self.url_updated(new_url):
            newlist.append(new_url)
        
        #nodev2ray.com
        #https://nodev2ray.com/uploads/2025/01/4-20250115.txt
        new_url0 = datetime.today().strftime('https://nodev2ray.com/uploads/%Y/%m/0-%Y%m%d.yaml')
        new_url1 = datetime.today().strftime('https://nodev2ray.com/uploads/%Y/%m/1-%Y%m%d.yaml')
        new_url2 = datetime.today().strftime('https://nodev2ray.com/uploads/%Y/%m/2-%Y%m%d.yaml')
        new_url3 = datetime.today().strftime('https://nodev2ray.com/uploads/%Y/%m/3-%Y%m%d.yaml')
        new_url4 = datetime.today().strftime('https://nodev2ray.com/uploads/%Y/%m/4-%Y%m%d.yml')
        #链接是否已经更新
        if self.url_updated(new_url0):
            newlist.append(new_url0)
        if self.url_updated(new_url1):
            newlist.append(new_url1)
        if self.url_updated(new_url2):
            newlist.append(new_url2)
        if self.url_updated(new_url3):
            newlist.append(new_url3)
        if self.url_updated(new_url4):
            newlist.append(new_url4)

        #clash-meta.github.io
        #https://clash-meta.github.io/uploads/2025/01/4-20250117.yaml
        new_url0 = datetime.today().strftime('https://clash-meta.github.io/uploads/%Y/%m/0-%Y%m%d.txt')
        new_url1 = datetime.today().strftime('https://clash-meta.github.io/uploads/%Y/%m/1-%Y%m%d.txt')
        new_url2 = datetime.today().strftime('https://clash-meta.github.io/uploads/%Y/%m/2-%Y%m%d.txt')
        new_url3 = datetime.today().strftime('https://clash-meta.github.io/uploads/%Y/%m/3-%Y%m%d.txt')
        new_url4 = datetime.today().strftime('https://clash-meta.github.io/uploads/%Y/%m/4-%Y%m%d.txt')
        #链接是否已经更新
        if self.url_updated(new_url0):
            newlist.append(new_url0)
        if self.url_updated(new_url1):
            newlist.append(new_url1)
        if self.url_updated(new_url2):
            newlist.append(new_url2)
        if self.url_updated(new_url3):
            newlist.append(new_url3)
        if self.url_updated(new_url4):
            newlist.append(new_url4)

        #https://clashfree.github.io/
        new_url0 = datetime.today().strftime('https://clashfree.github.io/uploads/%Y/%m/0-%Y%m%d.txt')
        new_url1 = datetime.today().strftime('https://clashfree.github.io/uploads/%Y/%m/1-%Y%m%d.txt')
        new_url2 = datetime.today().strftime('https://clashfree.github.io/uploads/%Y/%m/2-%Y%m%d.txt')
        new_url3 = datetime.today().strftime('https://clashfree.github.io/uploads/%Y/%m/3-%Y%m%d.txt')
        new_url4 = datetime.today().strftime('https://clashfree.github.io/uploads/%Y/%m/4-%Y%m%d.txt')
        #链接是否已经更新
        if self.url_updated(new_url0):
            newlist.append(new_url0)
        if self.url_updated(new_url1):
            newlist.append(new_url1)
        if self.url_updated(new_url2):
            newlist.append(new_url2)
        if self.url_updated(new_url3):
            newlist.append(new_url3)
        if self.url_updated(new_url4):
            newlist.append(new_url4)

        #再有此类网站添加至这里
        
        #返回带格式的字符串，订阅转换可用解析
        newlist = '|'.join(newlist)#带'|'格式的地址组，订阅能解析
        return newlist

    def mibei77Update(self,current_url):
        try:
            r=requests.get('https://www.mibei77.com', headers=headers, timeout=5.0)
            if r.status_code==200:
                r.encoding='utf-8'    #编码方式
                node_url = re.search("(https://www.mibei77.com/(.*).html)", r.text).group(0)#匹配第一个相同的网址
                r1=requests.get(node_url,headers=headers, timeout=5.0)
                if r.status_code==200:
                    r.encoding='utf-8'    #编码方式
                    new_url = re.search("(http://mm.mibei77.com(.*).yaml)", r1.text).group(0)#http://mm.mibei77.com/202501/01.11Clashopl.yaml
                else:
                    return current_url
            else:
                return current_url
        except requests.exceptions.RequestException as e:  
            return current_url
        #链接是否已经更新
        if new_url:
            if self.url_updated(new_url):
                return new_url
            else:
                return current_url 
        return current_url

    # ========== 抓取 https://www.cfmem.com/search/label/free 的订阅地址 ========== 
    def cfmemUpdate(self,current_url):  
        try:
            res = requests.get("https://www.cfmem.com/search/label/free",headers=headers)
    
            #搜索可以借鉴下面这个
            article_url = re.findall("https://www.cfmem.com/[^<>\\r\\n]+vpn.html",res.text)[0]
            res = requests.get(article_url,headers=headers)
            sub_url = sub_url = re.findall("https://fs.v2rayse.com[^<>\\r\\n]+yaml",res.text)[0]
        except:
            traceback.print_exc()
        #链接是否已经更新
        if self.url_updated(sub_url):
            return sub_url
        else:
            return current_url  

    # ========== 抓取 https://github.com/changfengoss/pub 的订阅列表 长风网站：https://v2rayse.com ==========  
    def changfenggossUpdate(self,current_url):
        try:
            today = datetime.today().strftime("%Y_%m_%d") #e.g: 2022_12_17
            cfurl = 'https://api.github.com/repos/changfengoss/pub/contents/data/'+today+'?ref=main'
            print('\n changfengoss/pub = ' + cfurl + '\n')
            urlList = requests.get(cfurl).json()
            subList = []
            for index in urlList:
                #print('\n' + index['download_url'] + '\n')
                subList.append(index['download_url'])
            #下面代码是将订阅地址写入文件的，暂时注释掉
            #subList = '\n'.join(subList)
            #with open("cfList.txt",'w') as f:
            #    f.write(subList)
        except:
            traceback.print_exc()
        subList = '|'.join(subList)#带'|'格式的地址组，订阅能解析
        return subList

if __name__ == '__main__':
    update(list_file_path)
