#!/usr/bin/env python3

# --------------------------------------------------------------------------------------
# 脚本第一行写上 #!/usr/bin/env python3 或者 #!/usr/bin/python3的区别：
# #!/usr/bin/python3 表示 python3 所处的绝对路径就是 /usr/bin/python3
# #!/usr/bin/env/ python3 表示从 "PATH 环境变量"中查找 python3 的位置, 更灵活更具有通用性, 推荐使用这种写法
# 详细介绍了`#!/usr/bin/env python3`这行命令https://www.jianshu.com/p/400c612381dd
# --------------------------------------------------------------------------------------
from ip_update import geoip_update  #更新IP位置数据库,将此行放入需要引用的文件里使用'geoip_update()'即可
from sub_convert import sub_convert # Python 之间互相调用文件https://blog.csdn.net/winycg/article/details/78512300
from list_update import update_url  # 调用list_update文件里的update_url类

import json, re, os                 # Python常用模块https://www.cnblogs.com/Mjonj/p/7499560.html
from urllib import request          # Urllib是python内置的HTTP请求库,urllib.request获取URL的Python模块


# 分析当前项目依赖,生成requirements.txt文件 https://blog.csdn.net/lovedingd/article/details/102522094


# 文件路径定义

# 爬取源列表文件
sub_list_json = './utils/fetch/config/sub_list.json'    

   
sub_merge_path = './sub/sources/'                   # 收集爬取的合集存放目录
sub_merge_url = './sub/sources/sub'   
sub_merge_base64 = './sub/sources/sub64'   
sub_merge_yaml = './sub/sources/all.yaml'
nocheck_yaml = './sub/sources/noCheckClash.yaml' 

sublist_content_path = './sub/sources/list/'               # 订阅列表备份路径

class sub_merge():
    def sub_merge(url_list): # 将转换后的所有 Url 链接内容合并转换 YAML or Base64, ，并输出文件，输入订阅列表。

        content_list = []
        for t in os.walk(sublist_content_path):    # 遍历文件夹
            for f in t[2]:
                f = t[0]+f
                os.remove(f)                # 删除所有的备份

        for index in range(len(url_list)):
            content = sub_convert.convert_remote(url_list[index]['url'],'url','http://127.0.0.1:25500') # 将爬取源url地址爬取的内容存放到content
            ids = url_list[index]['id']
            remarks = url_list[index]['remarks']
            if content == 'Url 解析错误':
                content = sub_convert.main(sub_merge.read_list(sub_list_json)[index]['url'],'url','url')
                if content != 'Url 解析错误':
                    content_list.append(content)
                    print(f'Writing content of {remarks} to {ids:0>2d}.txt\n')
                else:
                    print(f'Writing error of {remarks} to {ids:0>2d}.txt\n')
                file = open(f'{sublist_content_path}{ids:0>2d}.txt', 'w+', encoding= 'utf-8')
                file.write('Url 解析错误')
                file.close()
            elif content == 'Url 订阅内容无法解析':
                file = open(f'{sublist_content_path}{ids:0>2d}.txt', 'w+', encoding= 'utf-8')
                file.write('Url 订阅内容无法解析')
                file.close()
                print(f'Writing error of {remarks} to {ids:0>2d}.txt\n')
            elif content != None:
                content_list.append(content)
                file = open(f'{sublist_content_path}{ids:0>2d}.txt', 'w+', encoding= 'utf-8')
                file.write(content)
                file.close()
                print(f'Writing content of {remarks} to {ids:0>2d}.txt\n')
            else:
                file = open(f'{sublist_content_path}{ids:0>2d}.txt', 'w+', encoding= 'utf-8')
                file.write('Url 订阅内容无法解析')
                file.close()
                print(f'Writing error of {remarks} to {ids:0>2d}.txt\n')
                
        print('Merging nodes...\n')
        # 将列表内容，以行写入字符串？
        content_raw = ''.join(content_list) # https://python3-cookbook.readthedocs.io/zh_CN/latest/c02/p14_combine_and_concatenate_strings.html
        #去重
        content_yaml = sub_convert.main(content_raw,'content','YAML',{'dup_rm_enabled': True, 'format_name_enabled': False})
        # 写入YAML 文件
        with open(sub_merge_yaml, 'w+', encoding='utf-8') as f:
            f.write(content_yaml)
            f.close()
        #获取allyaml_path文件路径
        sub_merge_yaml_ptch = os.path.abspath(sub_merge_yaml)  #python获取绝对路径https://www.jianshu.com/p/1563374e279a
        # 写入url 订阅文件
        content_raw = sub_convert.convert_remote(sub_merge_yaml_ptch, output_type='url')
        file = open(f'{sub_merge_url}', 'w+', encoding= 'utf-8')
        file.write(content_raw)
        file.close()
        # 写入base64 订阅文件
        content_base64 = sub_convert.base64_encode(content_raw)
        with open(sub_merge_base64, 'w+', encoding='utf-8') as f:
            f.write(content_base64)
            f.close()
        # 写入Clash 订阅文件
        content_clash = sub_convert.convert_remote(sub_merge_yaml_ptch, output_type='clash')
        with open(nocheck_yaml, 'w+', encoding='utf-8') as f:
            f.write(content_clash)
            f.close()

    def read_list(json_file,remote=False):  # 将 sub_list.json    爬取源Url内容读取为列表
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



# if __name__ == '__main__'当模块被直接运行时以下代码块将被运行，当模块是被导入时，代码块不被运行
# 详细讲解：https://blog.konghy.cn/2017/04/24/python-entry-program/
if __name__ == '__main__':
# 准备工作
    update_url.update_main()                                    # 更新爬取源sub_list_json
    geoip_update()                                              # 更新IP位置数据库
# 开始正题
    sub_list = sub_merge.read_list(sub_list_json)               # 从sub_list_json读取爬取源的url放入sub_list
    sub_list_remote = sub_merge.read_list(sub_list_json,True)   # 多订阅地址的爬取源所有url都添加到sub_list_remote列表
    sub_merge.sub_merge(sub_list_remote)                        # 转换后的所有 Url 链接内容合并转换 YAML or Base64, 并输出文件sub_merge.txt，sub_merge_base64.txt，sub_merge_yaml.yml

