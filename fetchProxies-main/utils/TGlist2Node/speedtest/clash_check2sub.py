import os

#调用自己的模块，先获取执行的目录，再import文件
import sys
sys.path.append(".") #执行目录地址
from utils.subConvert.sub_convert import sub_convert
from utils.subConvert import list_to_content
#文件位置
input_source_file = './TGcheck.yaml'
output_clash_file = './sub/TG.yaml'
output_base64_file = './sub/TG64'
if __name__ == '__main__':
  
    #转换为clash
    input_source_file = os.path.abspath(input_source_file)  # 获取文件路径
    content = sub_convert.convert_remote(input_source_file,'clash')   #转换
    list_to_content.write_file(output_clash_file,content)
    
    #转换为url
    content = sub_convert.convert_remote(input_source_file,'url')   #转换
    content = sub_convert.base64_encode(content)
    list_to_content.write_file(output_base64_file,content)

    print(f'Writing TG content done！\n')
