import json, re, os


# 文件路径定义
readme_file_path = './README.md'              # 说明文件
# 爬取源列表文件，需要获取订阅源信息
sub_list_json = './utils/fetch/config/sub_list.json'
# 节点文件
sublist_content_path = './sub/sources/list/'  
sub_merge_url = './sub/sources/sub'
check_url = './sub/rx' 
#----------定义文件结束----------

def read_list(json_file =sub_list_json,remote=False):  # 将 sub_list.json    爬取源Url内容读取为列表
    with open(json_file, 'r', encoding='utf-8') as f:
        raw_list = json.load(f)         # json格式获取list内容，暂时存放到raw_list
    input_list = []
    for index in range(len(raw_list)):
        if raw_list[index]['enabled']:  # 如果enabled启用 == true （根据节点源的好坏，决定是否启用）
            if remote == False:         # 如果 remote偏僻，遥远 == False
                urls = re.split('\|',raw_list[index]['url'])    # 多订阅地址的爬取源，只取第一个地址？
            else:
                urls = raw_list[index]['url']                   # 多订阅地址的爬取源所有地址都添加
            raw_list[index]['url'] = urls
            input_list.append(raw_list[index])
    return input_list                   # 将sub_list.json里面的所有url存放到input_list返回

def readme_update(readme_file=readme_file_path, sub_list=[]): # 更新 README 节点信息

    print('更新 README.md 中...')
    
    #现将readme文件按行读取成lines
    with open(readme_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        f.close()
      
     # 已测速节点打印
    for index in range(len(lines)):
        if lines[index] == '### 已测速节点\n':  #找到目标行
        #if '### 已测速节点' in lines[index]:   
            # 清除旧内容
            lines.pop(index+1) # 删除节点数量
            
            #打开已测速文件算总数
            with open(check_url, 'r', encoding='utf-8') as f:
                proxies = f.read()
                proxies = proxies.split('\n')
                top_amount = len(proxies) - 1
                f.close()
             
            #写入节点数量行
            lines.insert(index+1, f'已测速节点数量: `{top_amount}`\n')
            """
            #不将节点信息写入readme文件，需要写入时，去掉
            #先清除以前旧内容
            while lines[index+4] != '\n':
                lines.pop(index+4)
            #调整格式
            proxies = ['    '+proxy+'\n' for proxy in proxies]
            #proxies = [proxy+'\n' for proxy in proxies]
            # 将已测速节点信息打印出来
            index += 4
            for i in proxies:
                index += 1
                lines.insert(index, i)
            if '</details>' not in lines[index+1]:  #怕行丢失，隐藏下面所有内容
                lines.insert(index+1, f'</details>\n')     
            """ 
            break   # 写完退出循环
                 
    # 所有节点总数打印
    for index in range(len(lines)):
        if lines[index] == '### 所有节点\n': 
        #if '### 所有节点' in lines[index]:
            # 清除旧内容
            lines.pop(index+1) 
            # 获取节点总数
            with open(sub_merge_url, 'r', encoding='utf-8') as f:  
                top_amount = len(f.readlines())
                f.close()
            #写入所有节点总数
            lines.insert(index+1, f'合并节点总数: `{top_amount}`\n')
            break   # 写完退出循环
            
    # 获得当前sublist名单及各仓库节点数量
    #repo_amount_dic = {}	#不知道什么作用先注释掉，关联下面的 repo_amount_dic.setdefault(id, amount) 
    thanks = []
    for repo in sub_list:
        line = ''
        if repo['enabled'] == True:
            id = repo['id']
            remarks = repo['remarks']
            repo_site = repo['site']           
            sub_file = f'{sublist_content_path}{id:0>2d}.txt'
            with open(sub_file, 'r', encoding='utf-8') as f:
                proxies = f.readlines()
                if proxies == ['Url 解析错误'] or proxies == ['订阅内容解析错误']:
                    amount = 0
                else:
                    amount = len(proxies)
                f.close()
        #    repo_amount_dic.setdefault(id, amount)    #不知道什么作用先注释掉，关联上面的 repo_amount_dic = {}
            line = f'- [{remarks}]({repo_site}), 节点数量: `{amount}`\n'
        thanks.append(line)
     
    # 节点来源打印
    for index in range(len(lines)):
        if lines[index] == '### 节点来源\n':
        #if '## 节点来源' in lines[index]:
            # 清除旧内容
            while lines[index + 1] != '\n':
                lines.pop(index + 1)
            for i in thanks:
                index += 1
                lines.insert(index, i)
            break

    # 写入 README 内容
    with open(readme_file, 'w', encoding='utf-8') as f:
        data = ''.join(lines)
        print('README.md write 完成!\n')
        f.write(data)
     # 写入 README 内容
    with open('./README1.md' , 'w', encoding='utf-8') as f:
        data = ''.join(lines)
        print('README.md write 完成!\n')
        f.write(data)
                                   
# if __name__ == '__main__'当模块被直接运行时以下代码块将被运行，当模块是被导入时，代码块不被运行
# 详细讲解：https://blog.konghy.cn/2017/04/24/python-entry-program/            
if __name__ == '__main__':
    readme_update(readme_file_path,read_list(sub_list_json))        #更新README.md信息
