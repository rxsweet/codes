import os, yaml

#调用自己的模块，先获取执行的目录，再import文件
import sys
sys.path.append(".") #执行目录地址
from utils.subConvert.sub_convert import sub_convert

#cofig文件: config_file_path
config_file_path = './utils/clashspeedtest/config.yaml'

def get_outputpath():
    #打开config.yaml文件
    with open(config_file_path,encoding="UTF-8") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    output_file_path = config['outfile_base64']
    output_clash_file = config['outfile']
    return output_file_path,output_clash_file
    
def write_file(file,content):
    f = open(file, 'w',encoding="UTF-8")
    f.write(content)
    f.close()    
    
def output():
    #得到输出路径
    print("\n==============begin output clash speedtest file================\n")
    output_file_path,output_clash_file = get_outputpath()
    print('\n output_file_path  =' + output_file_path + '\n')
    print('\n output_clash_file = ' + output_clash_file + '\n')
    #获取allyaml_path文件路径
    clashpath = os.path.abspath(output_clash_file)
    
    # 写入base64 订阅文件
    print('\n--------------write file begin!--------------\n')
    subContent = sub_convert.convert_remote(clashpath,'url')
    if subContent != 'Url 解析错误' :
        subContent = sub_convert.base64_encode(subContent)
        print('write Base64 file content!')
        write_file(output_file_path,subContent)
        # 写入clash 订阅文件
        subContent = sub_convert.convert_remote(clashpath,'clash')
        print('write clash file content!')
        write_file(output_clash_file,subContent)
    print('\n--------------write file done!--------------\n')
    
