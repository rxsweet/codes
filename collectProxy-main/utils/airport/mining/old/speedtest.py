#调用自己的模块，先获取执行的目录，再import文件
import sys
sys.path.append(".") #执行目录地址
from utils.clashspeedtest import set_config

if __name__ == '__main__':
    set_config.set_config('./sub/sources/miningAll.yaml', './sub/mining64.txt', './sub/mining.yaml')
