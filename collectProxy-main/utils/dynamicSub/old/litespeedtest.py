#调用自己的模块，先获取执行的目录，再import文件
import sys
sys.path.append(".") #执行目录地址
from utils.litespeedtest import set_config
from utils import tools

if __name__ == '__main__':
    #安装工具
    tools.mmdb_install()
    tools.subconverter_install()
    #设置路径
    set_config.set_config('./sub/sources/dynamicAll.yaml', './sub/literx64.txt', './sub/literx.yaml')
    
