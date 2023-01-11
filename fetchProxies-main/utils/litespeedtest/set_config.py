#!/usr/bin/env python3

import json

#测速cofig文件: config_file_path
config_file_path = './utils/litespeedtest/lite_config.json'

#需要测速的文件位置: input_file_path



def set_config(input_file_path, output_file_path):  #必须输入2个参数：input_file_path, output_file_path，输出文件是base64格式

    #打开config.json文件
    with open(config_file_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
        f.close() 
    config['subscription'] = input_file_path
    config['outputPath'] = output_file_path
    updated_config = json.dumps(config)
    
    #将修改完成的config.json写入文件
    file = open(config_file_path, 'w', encoding='utf-8')
    file.write(updated_config)
    file.close()   


if __name__ == '__main__':
    set_config(input_file_path = './sub/sources/fetchShareClash.yml',output_file_path = './sub/sources/literx64')
