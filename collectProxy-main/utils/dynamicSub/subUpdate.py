#!/usr/bin/env python3

from datetime import datetime
import json, re
import requests
import traceback

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
                if current_remarks == 'pojiezhiyuanjun':
                    new_url = self.pojiezhiyuanjunUpdate(sub ['url'])
                    if new_url == sub ['url']:
                        print(f'No available update for ID {current_remarks}\n')
                    else:
                        sub['url'] = new_url
                        print(f'ID {current_remarks} url updated to {new_url}\n')    
                elif current_remarks == 'ClashNode':
                    new_url = self.clashNodeUpdate(sub ['url'])
                    if new_url == sub ['url']:
                        print(f'No available update for ID {current_remarks}\n')
                    else:
                        sub['url'] = new_url
                        print(f'ID {current_remarks} url updated to {new_url}\n') 
                elif current_remarks == 'v2rayShare':
                    new_url = self.v2rayshareUpdate(sub ['url'])
                    if new_url == sub ['url']:
                        print(f'No available update for ID {current_remarks}\n')
                    else:
                        sub['url'] = new_url
                        print(f'ID {current_remarks} url updated to {new_url}\n') 
                elif current_remarks == 'oneclash.cc':
                    new_url = self.oneclashUpdate(sub ['url'])
                    if new_url == sub ['url']:
                        print(f'No available update for ID {current_remarks}\n')
                    else:
                        sub['url'] = new_url
                        print(f'ID {current_remarks} url updated to {new_url}\n') 
                elif current_remarks == 'wefound.cc':
                    new_url = self.wefoundUpdate(sub ['url'])
                    if new_url == sub ['url']:
                        print(f'No available update for ID {current_remarks}\n')
                    else:
                        sub['url'] = new_url
                        print(f'ID {current_remarks} url updated to {new_url}\n')                         
                elif current_remarks == 'Nodefree.org':
                    new_url = self.nodeFreeUpdate(sub ['url'])
                    if new_url == sub ['url']:
                        print(f'No available update for ID {current_remarks}\n')
                    else:
                        sub['url'] = new_url
                        print(f'ID {current_remarks} url updated to {new_url}\n')    
                elif current_remarks == 'kkzui.com':
                    new_url = self.kkzuiUpdate(sub ['url'])
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
                elif current_remarks == 'v2cross.com':
                    new_url = self.v2crossUpdate(sub ['url'])
                    if new_url == sub ['url']:
                        print(f'No available update for ID {current_remarks}\n')
                    else:
                        sub['url'] = new_url
                        print(f'ID {current_remarks} url updated to {new_url}\n')   
                elif current_remarks == 'mianfeifq':
                    new_url = self.mianfeifqUpdate(sub ['url'])
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
                output_list.append(index['url'])
            output_list = '\n'.join(output_list)        
            file = open(txt_list_file_path, 'w', encoding='utf-8')
            file.write(output_list)
            file.close()
                
    # ========== 抓取 https://github.com/pojiezhiyuanjun/freev2 的订阅地址 ==========
    def pojiezhiyuanjunUpdate(self,current_url):
        today = datetime.today().strftime('%m%d')
        new_url = 'https://raw.githubusercontent.com/pojiezhiyuanjun/freev2/master/' + today + '.txt'
        #链接是否已经更新
        if self.url_updated(new_url):
            return new_url
        else:
            return current_url
            
    # ========== 抓取 https://clashnode.com 的订阅地址 ==========
    def clashNodeUpdate(self,current_url):   
        new_url = datetime.today().strftime('https://clashnode.com/wp-content/uploads/%Y/%m/%Y%m%d.txt')
        #链接是否已经更新
        if self.url_updated(new_url):
            return new_url
        else:
            return current_url
					
	# ========== 抓取 https://v2rayshare.com 的订阅地址 ==========		
    def v2rayshareUpdate(self,current_url):   
        new_url = datetime.today().strftime('https://v2rayshare.com/wp-content/uploads/%Y/%m/%Y%m%d.txt')
        #链接是否已经更新
        if self.url_updated(new_url):
            return new_url
        else:
            return current_url 
            
	# ========== 抓取 https://oneclash.cc 的订阅地址 ==========		
    def oneclashUpdate(self,current_url):   
        new_url = datetime.today().strftime('https://oneclash.cc/wp-content/uploads/%Y/%m/%Y%m%d.txt')
        #链接是否已经更新
        if self.url_updated(new_url):
            return new_url
        else:
            return current_url
            
    # ========== 抓取 https://wefound.cc 的订阅地址 ==========        
    def wefoundUpdate(self,current_url):   
        new_url = datetime.today().strftime('https://wefound.cc/freenode/%Y/%m/%Y%m%d.txt')
        #链接是否已经更新
        if self.url_updated(new_url):
            return new_url
        else:
            return current_url 
				
    # ========== 抓取 https://nodefree.org/ 的订阅地址 ==========
    def nodeFreeUpdate(self,current_url):
        today = datetime.today().strftime('%Y/%m/%Y%m%d')
        url_front = 'https://nodefree.org/dy/'
        url_end = '.txt'
        new_url = url_front + today + url_end
        #链接是否已经更新
        if self.url_updated(new_url):
            return new_url
        else:
            return current_url  
    
    # ========== 抓取 kkzui.com 的节点 ==========
    def kkzuiUpdate(self,current_url):
        try:
            res = requests.get("https://kkzui.com/jd?orderby=modified",headers=headers)
            #搜索可以借鉴下面这个
            #article_url = re.search(r'<h2 class="item-heading"><a href="(https://kkzui.com/(.*?)\.html)(.*?)个高速免费节点(.*?)</a></h2>',res.text).groups()[0]
            article_url = re.search(r'<a href="(https://kkzui.com/(.*?)\.html)(.*?)个高速免费节点(.*?)</a>',res.text).groups()[0]
            res = requests.get(article_url,headers=headers)
            #new_url = re.search(r'<p><strong>这是v2订阅地址</strong>：(.*?)</p>',res.text).groups()[0]
            new_url = re.search(r'这是v2订阅地址：(https://(.*?))</p>',res.text).groups()[0]
            #下面代码是获取订阅节点内容的，并且需要import base64
            #res = requests.get(sub_url,headers=headers)
            #merge += str(base64.b64decode(res.text.encode()),'utf-8').strip().replace('\r\n','\n').split('\n')
        except:
            traceback.print_exc()
            return current_url
        #链接是否已经更新
        if self.url_updated(new_url):
            return new_url
        else:
            return current_url   

    # ========== 抓取 https://www.cfmem.com/search/label/free 的订阅地址 ========== 
    def cfmemUpdate(self,current_url):  
        try:
            res = requests.get("https://www.cfmem.com/search/label/free",headers=headers)
    
            #搜索可以借鉴下面这个
            article_url = re.findall("https://www.cfmem.com/(.*?)-v2rayclash-vpn.html",res.text)[0]
            article_url = 'https://www.cfmem.com/'+ article_url +'-v2rayclash-vpn.html'
            res = requests.get(article_url,headers=headers)
            #sub_url = re.findall("https://oss.v2rayse.com/proxies/data/(.*?).yaml",res.text)[0]
            #sub_url = 'https://oss.v2rayse.com/proxies/data/'+ sub_url + '.yaml'
            sub_url = re.findall("v2ray订阅链接&#65306;https://(.*?)</span>",res.text)[0]
            sub_url = 'https://'+ sub_url
        except:
            traceback.print_exc()
            try:
                #sub_url = re.findall("https://oss.v2rayse.com/proxies/data/(.*?).txt",res.text)[0]
                #sub_url = 'https://oss.v2rayse.com/proxies/data/'+ sub_url + '.txt'
                sub_url = re.findall("v2ray订阅链接&#65306;https://(.*?)</span>",res.text)[0]
                sub_url = 'https://'+ sub_url
            except:
                traceback.print_exc()
                sub_url = current_url
        #链接是否已经更新
        if self.url_updated(sub_url):
            return sub_url
        else:
            return current_url  

    # ========== 抓取 https://v2cross.com/archives/1884 的订阅地址 ==========  
    def v2crossUpdate(self,current_url):  
        try:
            res = requests.get("https://v2cross.com/archives/1884",headers=headers)
    
            #搜索可以借鉴下面这个,https://blog.csdn.net/weixin_44799217/article/details/122069415
            article_url = re.search(r'<h5>本次节点订阅地址：(http(.*?))</h5>',res.text).groups()[0]
        except:
            traceback.print_exc()
            return article_url
        #链接是否已经更新
        if self.url_updated(article_url):
            return article_url
        else:
            return current_url  

    # ========== 抓取 https://github.com/mianfeifq/share 的订阅地址 ==========
    def mianfeifqUpdate(self,current_url):
        try:
            res_json = requests.get('https://api.github.com/repos/mianfeifq/share/contents/').json()
            for file in res_json:
                if file['name'].startswith('data'):
                    return file['download_url'] 
            return current_url
        except Exception:
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
                print('\n' + index['download_url'] + '\n')
                subList.append(index['download_url'])
            #下面代码是将订阅地址写入文件的，暂时注释掉
            #subList = '\n'.join(subList)
            #with open("cfList.txt",'w') as f:
            #    f.write(subList)
        except:
            traceback.print_exc()
        subList = '|'.join(subList)#带'|'格式的地址组，订阅能解析
        return subList
"""
            id = sub['id']
            current_url = sub['url']
            try:
                if sub['update_method'] != 'auto' and sub['enabled'] == True:
                    print(f'Finding available update for ID{id}')
                    if sub['update_method'] == 'change_date':
                        new_url = self.change_date(id,current_url)
                        if new_url == current_url:
                            print(f'No available update for ID{id}\n')
                        else:
                            sub['url'] = new_url
                            print(f'ID{id} url updated to {new_url}\n')
                    elif sub['update_method'] == 'page_release':
                        new_url = self.find_link(id,current_url)
                        if new_url == current_url:
                            print(f'No available update for ID{id}\n')
                        else:
                            sub['url'] = new_url
                            print(f'ID{id} url updated to {new_url}\n')
            except KeyError:
                print(f'{id} Url not changed! Please define update method.')
            
            updated_list = json.dumps(self.raw_list, sort_keys=False, indent=2, ensure_ascii=False)
            file = open(self.list_file, 'w', encoding='utf-8')
            file.write(updated_list)
            file.close()

    def change_date(self,id,current_url):
        if id == 40:
            
        if id == 36:
            today = datetime.today().strftime('%Y%m%d')
            this_month = datetime.today().strftime('%Y%m')
            url_front = 'https://nodefree.org/dy/'
            url_end = '.txt'
            new_url = url_front + this_month + '/' + today + url_end
        if id == 0:
            today = datetime.today().strftime('%m%d')
            url_front = 'https://raw.githubusercontent.com/pojiezhiyuanjun/freev2/master/'
            url_end = '.txt'
            new_url = url_front + today + url_end

        if self.url_updated(new_url):
            return new_url
        else:
            return current_url

    def find_link(self,id,current_url):
        if id == 38:
            try:
                res_json = requests.get('https://api.github.com/repos/mianfeifq/share/contents/').json()
                for file in res_json:
                    if file['name'].startswith('data'):
                        return file['download_url'] 
                else:
                    return current_url
            except Exception:
                return current_url
        if id == 33:
            url_update = 'https://v2cross.com/archives/1884'

            if self.url_updated(url_update):
                try:
                    resp = requests.get(url_update, timeout=5)
                    raw_content = resp.text

                    raw_content = raw_content.replace('amp;', '')
                    pattern = re.compile(r'https://shadowshare.v2cross.com/publicserver/servers/temp/\w{16}')
                    
                    new_url = re.findall(pattern, raw_content)[0]
                    return new_url
                except Exception:
                    return current_url
            else:
                return current_url
"""
if __name__ == '__main__':
    update(list_file_path)




