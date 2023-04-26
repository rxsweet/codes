#!/usr/bin/env python3

#使用方法，直接import此文件，调用set_config(3个参数)
import json

#测速cofig文件: config_file_path
config_file_path = './utils/litespeedtest/lite_config.json'

def set_config(input_file_path, output_base64_path, output_clash_Path):  
    #3个参数：
    #input_file_path需要测速的文件位置, 
    #output_file_path，输出文件是base64格式,
    #outputClashPath是clash格式

    #打开config.json文件
    with open(config_file_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
        f.close() 
    config['subscription'] = input_file_path
    config['outputPath'] = output_base64_path
    config['outputClashPath'] = output_clash_Path
    updated_config = json.dumps(config)
    
    #将修改完成的config.json写入文件
    file = open(config_file_path, 'w', encoding='utf-8')
    file.write(updated_config)
    file.close()   


if __name__ == '__main__':
    set_config(input_file_path = './sub/sources/fetchShareClash.yml', output_base64_path = './sub/literx64', output_clash_Path = './sub/literx.yaml')
