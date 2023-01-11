import re, yaml
import time, os
from tqdm import tqdm   #进度条库
import threading  #线程
from ip_update import geoip_update  # 更新ip库Country.mmdb 
from sub_convert import sub_convert
import requests

#源文件
urllistfile = './utils/crawlNode/sublist'
urllistfile2 = './sub/sources/changeSubList.txt'
#输出订阅文件位置
outputAllyaml_path = './sub/sources/all.yaml'
outputUrlSub_path = './sub/sources/url'
outputBase64Sub_path =  './sub/sources/url64'
outputClashSub_path = './sub/sources/noCheckClash.yml'


#code begin
   
def sub_to_url(url,bar,allProxy):   #将url订阅内容append到allProxy列表，并完成进度bar
    if 'http' in url:
        subContent =sub_convert.convert_remote(url,'url')
        allProxy.append(subContent)
    bar.update(1)

# 写入文件模块
def write_file(file,content):
    f = open(file, 'w', encoding= 'utf-8')
    f.write(content)
    f.close()


def urlListToSub(urllistfile):  #将url订阅列表内容转换成url,base64,clash文件保存
    
    #打开url列表文件1
    file_urllist = open(urllistfile, 'r', encoding='utf-8')
    urllist_content = file_urllist.read()
    file_urllist.close()
    #打开url列表文件内容，以行为单位存放到line列表
    lines = re.split(r'\n+',urllist_content)

    #打开url列表文件2
    file_urllist = open(urllistfile2, 'r', encoding='utf-8')
    urllist_content = file_urllist.read()
    file_urllist.close()
    #打开url列表文件内容，以行为单位存放到line列表
    lines = lines + re.split(r'\n+',urllist_content)

    allProxy = []
    #计算打印url总数
    lenlines =len(lines)
    print('airport total == '+str(lenlines)+'\n')
    
    #Semaphore 是用于控制进入数量的锁，控制同时进行的线程，内部是基于Condition来进行实现的
    #https://www.cnblogs.com/callyblog/p/11147456.html
    #文件， 读、写， 写一般只是用于一个线程写，读可以允许有多个
    thread_max_num =threading.Semaphore(lenlines)
    
    #进度条添加
    bar = tqdm(total=lenlines, desc='订阅获取：')
    thread_list = []
    
    for line in lines:
        #为每个新URL创建线程
        t = threading.Thread(target=sub_to_url, args=(line,bar,allProxy))
        #加入线程池
        thread_list.append(t)
        #setDaemon()线程守护，配合下面的一组for...t.join(),实现所有线程执行结束后，才开始执行下面代码
        t.setDaemon(True)	#python多线程之t.setDaemon(True) 和 t.join()  https://www.cnblogs.com/my8100/p/7366567.html
		#启动
        t.start()
        
    #等待所有线程完成，配合上面的t.setDaemon(True)
    for t in thread_list:
        t.join()
    bar.close() #进度条结束
    
    # 将列表内容，以行写入字符串？
    allProxy = '\n'.join(allProxy)
	
    #去重
    allyaml = sub_convert.main(allProxy,'content','YAML',{'dup_rm_enabled': True, 'format_name_enabled': False})

    # 写入YAML 文件
    print('write ./sub/sources/all.yaml file content!')
    write_file(outputAllyaml_path,allyaml)

    #获取allyaml_path文件路径
    good_file_path = os.path.abspath(outputAllyaml_path)

    # 写入url 订阅文件 
    print('write ./sub/sources/url file content!')
    subContent = sub_convert.convert_remote(good_file_path,'url')
    write_file(outputUrlSub_path,subContent)

    # 写入base64 订阅文件
    print('write ./sub/sources/url64 file content!')
    subContent = sub_convert.base64_encode(subContent)
    write_file(outputBase64Sub_path,subContent)

    # 写入Clash 订阅文件
    print('write ./sub/sources/noCheckClash file content!')
    subContent = sub_convert.convert_remote(good_file_path,'clash')
    write_file(outputClashSub_path,subContent)



if __name__ == '__main__':
    #更新IP库
    geoip_update()
    urlListToSub(urllistfile)

"""	
    #网络获取
    res = requests.get('https://raw.githubusercontent.com/rxsweet/test/main/subList.txt', timeout=5)
    raw_content = res.text
    lines = lines + re.split(r'\n+',raw_content)
"""	


