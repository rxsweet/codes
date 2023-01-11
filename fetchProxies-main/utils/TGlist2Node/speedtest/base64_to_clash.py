import os

#调用自己的模块，先获取执行的目录，再import文件
import sys
sys.path.append(".") #执行目录地址
from utils.subConvert.sub_convert import sub_convert

#文件位置
input_source_file = './sub/liteTG64'
output_file = './sub/liteTG.yaml'

if __name__ == '__main__':
    #转换
    input_source_file = os.path.abspath(input_source_file)  # 获取文件路径
    content = sub_convert.convert_remote(input_source_file,'clash')   #转换

    #写入
    file = open(output_file, 'w', encoding= 'utf-8')
    file.write(content)
    file.close()
    print(f'Writing content done！\n')
