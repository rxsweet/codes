#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# 脚本第一行写上 #!/usr/bin/env python3 或者 #!/usr/bin/python3的区别：
# #!/usr/bin/python3 表示 python3 所处的绝对路径就是 /usr/bin/python3
# #!/usr/bin/env/ python3 表示从 "PATH 环境变量"中查找 python3 的位置, 更灵活更具有通用性, 推荐使用这种写法
# 详细介绍了`#!/usr/bin/env python3`这行命令https://www.jianshu.com/p/400c612381dd
# --------------------------------------------------------------------------------------
from datetime import timedelta, datetime
import json, re
import requests
from requests.adapters import HTTPAdapter

# 文件路径定义
sub_list_json = './utils/fetch/config/sub_list.json'                   # 爬取源列表文件


with open(sub_list_json, 'r', encoding='utf-8') as f:   # 载入订阅链接
    raw_list = json.load(f)
    f.close()

def url_updated(url):                                   # 判断远程远程链接是否已经更新
    s = requests.Session()                              # 用requests.session()创建session对象，相当于创建了一个空的会话框，准备保持cookies。
    s.mount('http://', HTTPAdapter(max_retries=2))      # 重试次数为2
    s.mount('https://', HTTPAdapter(max_retries=2))     # 重试次数为2
    try:
        resp = s.get(url, timeout=2)                    # 超时时间为2s
        status = resp.status_code                       # 状态码赋值200？
    except Exception:
        status = 404
    if status == 200:
        url_updated = True
    else:
        url_updated = False
    return url_updated

class update_url():

    def update_main():
        for sub in raw_list:        # JS for in循环语句的用法 http://c.biancheng.net/view/9346.html
            id = sub['id']
            current_url = sub['url']
            try:
                if sub['update_method'] != 'auto' and sub['enabled'] == True:   # if根据update_method设置的值判断是否需要变化地址后缀（原地址是变化的地址）
                    print(f'Finding available update for ID{id}')
                    if sub['update_method'] == 'change_date':               # if如果update_method的值是change_date，执行change_date()功能功能模块
                        new_url = update_url.change_date(id,current_url)
                        if new_url == current_url:                      # 判断新旧地址是否相同
                            print(f'No available update for ID{id}\n')    # 相同，没有可用的更新\n
                        else:
                            sub['url'] = new_url                          # 不同，新地址替换原地址
                            print(f'ID{id} url updated to {new_url}\n') 
                    elif sub['update_method'] == 'page_release':            # if如果update_method的值是page_release，执行find_link()功能功能模块
                        new_url = update_url.find_link(id,current_url)
                        if new_url == current_url:                      # 判断新旧地址是否相同
                            print(f'No available update for ID{id}\n')    # 相同，没有可用的更新\n
                        else:
                            sub['url'] = new_url                          # 不同，新地址替换原地址
                            print(f'ID{id} url updated to {new_url}\n')
            except KeyError:
                print(f'{id} Url not changed! Please define update method.')    # Url没变化，请重新定义update_method的值
            
            updated_list = json.dumps(raw_list, sort_keys=False, indent=2, ensure_ascii=False)
            file = open(sub_list_json, 'w', encoding='utf-8')
            file.write(updated_list)
            file.close()

    def change_date(id,current_url):    # update_method:change_date 变化地址返回最新地址的功能模块
        if id == 2: #根据ID确定网站
            today = datetime.today().strftime('%Y%m%d')
            this_month = datetime.today().strftime('%Y%m')
            url_front = 'https://nodefree.org/dy/'
            url_end = '.txt'
            new_url = url_front + this_month + '/' + today + url_end
        if id == 1: #根据ID确定网站
            today = datetime.today().strftime('%m%d')
            url_front = 'https://raw.githubusercontent.com/pojiezhiyuanjun/freev2/master/'
            url_end = '.txt'
            new_url = url_front + today + url_end

        if url_updated(new_url):     # 判断url_updated 地址数据是否更新
            return new_url              #更新了，返回新地址new_url
        else:
            return current_url          #未更新，返回原地址current_url

    def find_link(id,current_url):   # update_method:page_release 变化地址返回最新地址的功能模块
        if id == 0:    #根据ID确定网站
            url_update = 'https://v2cross.com/archives/1884'

            if url_updated(url_update):  # 判断url_updated 地址数据是否更新
                try:
                    resp = requests.get(url_update, timeout=5)
                    raw_content = resp.text     # 得到网址内容

                    raw_content = raw_content.replace('amp;', '')
                    pattern = re.compile(r'https://shadowshare.v2cross.com/publicserver/servers/temp/\w{16}')
                    
                    new_url = re.findall(pattern, raw_content)[0]
                    return new_url
                except Exception:
                    return current_url
            else:
                return current_url
        if id == 3:
            try:
                res_json = requests.get('https://api.github.com/repos/mianfeifq/share/contents/').json()
                for file in res_json:
                    if file['name'].startswith('data'):
                        return file['download_url'] 
                else:
                    return current_url
            except Exception:
                return current_url

if __name__ == '__main__':
    update_url.update_main()
