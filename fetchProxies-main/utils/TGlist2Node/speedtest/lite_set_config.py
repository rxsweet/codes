#调用自己的模块，先获取执行的目录，再import文件
import sys
sys.path.append(".") #执行目录地址
from utils.litespeedtest import set_config

if __name__ == '__main__':
    set_config.set_config('./sub/sources/TGsubNodeAll.yaml','./sub/liteTG64','./sub/liteTG.yaml')
