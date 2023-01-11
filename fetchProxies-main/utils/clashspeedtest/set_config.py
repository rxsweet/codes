#!/usr/bin/env python3

import yaml

#测速cofig文件: config_file_path
config_file_path = './utils/clashspeedtest/config.yaml'

#需要测速的文件位置: input_file_path


def set_config(input_file_path, output_file_path):  #必须输入2个参数：input_file_path, output_file_path，输出文件是yaml格式

    #打开config.yaml文件
    with open(config_file_path,encoding="UTF-8") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    config.update({'source':input_file_path})
    config.update({'outfile':output_file_path})

    #将修改完成的config.yaml写入文件
    with open(config_file_path, 'w',encoding="utf-8") as f:
        data = yaml.dump(config, f,allow_unicode=True)


if __name__ == '__main__':
    set_config(input_file_path = './sub/sources/fetchShareAll.yaml',output_file_path = './sub/sources/TGcheck.yaml')
