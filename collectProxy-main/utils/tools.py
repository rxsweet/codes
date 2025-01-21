##############################
# 安装工具
# from utils import tools
# tools.all()
##############################
import gzip         #https://www.cnblogs.com/eliwang/p/14591861.html
import os
import shutil   #主要：拷贝文件https://blog.csdn.net/weixin_41261833/article/details/108050152
import requests #python中requests库使用方法详解 https://zhuanlan.zhihu.com/p/137649301  https://www.runoob.com/python3/python-requests.html

#下载模块
def download(url, file, unpack_gzip=False):
    os.makedirs(os.path.normpath(os.path.dirname(file)), exist_ok=True)
    #os.path.dirname(path)功能：去掉文件名，返回目录 ,此处clash_path='/usr/local/bin/clash'，返回'/usr/local/bin/'
    #os.path.normpath(path)，规范路径path字符串 https://blog.csdn.net/jn10010537/article/details/122769205
    #os.makedirs(path,mode) 用于递归创建目录，path -- 需要递归创建的目录，可以是相对或者绝对路径，mode -- 权限模式
    with (
        #python中requests库使用方法详解 https://zhuanlan.zhihu.com/p/137649301  https://www.runoob.com/python3/python-requests.html
        requests.get(url, headers={'Accept-Encoding': 'gzip'}, stream=True) as resp,
        open(file, 'wb') as _out
    ):
        _in = resp.raw
        if unpack_gzip or resp.headers.get('Content-Encoding') == 'gzip':
            _in = gzip.open(_in)    #解压文件https://www.cnblogs.com/eliwang/p/14591861.html
        shutil.copyfileobj(_in, _out)   #拷贝文件https://zhuanlan.zhihu.com/p/213919757 和 https://www.cnblogs.com/xiangsikai/p/7787101.html
        
#下载 mmdb
def mmdb_install():
    if not os.path.exists('./Country.mmdb'):
        os.system("wget -q -O Country.mmdb https://github.com/Dreamacro/maxmind-geoip/releases/latest/download/Country.mmdb")       
        print('======Country.mmdb 下载结束！======')
    else:
        print('======Country.mmdb已经安装过了，不用重复安装！======')

#下载clash
#现用版https://github.com/Dreamacro/clash/releases/download/v1.11.8/clash-linux-amd64-v1.18.0.gz
def clash_install(
    #clash_url='https://raw.githubusercontent.com/rxsweet/all/main/githubTools/clash-linux-amd64-v1.18.0.gz',
    #clash_url='https://github.com/MetaCubeX/mihomo/releases/download/v1.19.1/mihomo-linux-amd64-v1.19.1.gz',#变成meta
    clash_url='https://raw.githubusercontent.com/rxsweet/all/refs/heads/main/githubTools/mihomo-linux-amd64-v1.19.1.gz',#变成meta
    clash_path='./clash-linuxamd64',
):
    if not os.path.exists(clash_path):   #os.path.exists()就是判断括号里的文件是否存在，括号内的可以是文件路径
        download(clash_url, clash_path, unpack_gzip=True)#下载clash
        os.chmod(clash_path, 0o755)#os.chmod() 方法用于更改文件或目录的权限。
        #print('======clash-v1.18.0 下载安装结束！======')
        print('======meta-v1.19.1 下载安装结束！======')
    else:
        #print('======clash-v1.18.0 已经安装过了，不用重复安装！======') 
        print('======meta-v1.19.1已经安装过了，不用重复安装！======') 

#下载subconverter
def subconverter_install():    
    try:
        #os.system()
        if not os.path.exists('./subconverter.tar.gz'):
            r=requests.get('https://github.com/lonelam/subconverter/releases/latest/download/subconverter_linux64.tar.gz')
            if r.status_code==200:
                os.system("wget -q -O subconverter.tar.gz https://github.com/lonelam/subconverter/releases/latest/download/subconverter_linux64.tar.gz")    #支持hy2
            else:
                os.system("wget -q -O subconverter.tar.gz https://github.com/tindy2013/subconverter/releases/latest/download/subconverter_linux64.tar.gz")  #-q安静模式(没有输出)
            os.system("tar -zxf subconverter.tar.gz -C ./")
            os.system("chmod +x ./subconverter/subconverter && nohup ./subconverter/subconverter >./subconverter.log 2>&1 &")
            print('=subconverter已经启动=')
        #if config_url and (config_cover or not os.path.exists(config_path)):
            #download(config_url, config_path)#下载config.yaml（实际就是节点文件）
        #os.system("docker run -d --restart always -p 25500:25500 tindy2013/subconverter")
        else:
            print('======subconverter已经下载过了，不用重复下载！======')
    except Exception as err:
        print(err)
        print('subconverter安装失败')



#安装全部功能，新功能添加至此    
def all():
    mmdb_install()
    clash_install()
    subconverter_install()
    print('######所有依赖的工具已安装完成######\n')



if __name__ == '__main__':
    all()
    
    
