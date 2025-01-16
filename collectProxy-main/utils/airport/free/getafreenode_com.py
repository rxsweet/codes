#!/usr/bin/env python3

import re
import requests
import traceback

headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.53"}

# ========== 获取 https://getafreenode.com/ 的订阅地址 ==========  
def getafreenodeUpdate():  
    try:
        res = requests.get("https://getafreenode.com/",headers=headers)
        uuid = re.search('uuid=(.*?)"', res.text).group(1)
        
    except:
        traceback.print_exc()
        sub_url = 'https://getafreenode.com/获取失败'
        print(sub_url)
        return sub_url
    sub_url = 'https://getafreenode.com/subscribe/?uuid=' + str(uuid)
    print(sub_url)
    return  sub_url
    
    
if __name__ == '__main__':
    getafreenodeUpdate()
