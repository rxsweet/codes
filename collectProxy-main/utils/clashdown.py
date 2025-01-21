import gzip         #https://www.cnblogs.com/eliwang/p/14591861.html
import os
import shutil   #主要：拷贝文件https://blog.csdn.net/weixin_41261833/article/details/108050152
import requests #python中requests库使用方法详解 https://zhuanlan.zhihu.com/p/137649301  https://www.runoob.com/python3/python-requests.html

def clash_android_down():    
    #os.system("wget -O Clash_Android.apk http://download.kstore.space/download/4901/Clash_Android.apk")
    os.system("wget -O ClashMeta_Android.apk https://github.com/MetaCubeX/ClashMetaForAndroid/releases/download/v2.11.5/cmfa-2.11.5-meta-universal-release.apk")

#安装全部功能，新功能添加至此    
def all():
    clash_android_down()
    print('######所有工具已下载完成######\n')



if __name__ == '__main__':
    all()
