#使用方法，直接import此文件，调用set_config(3个参数)

import yaml

#测速cofig文件: config_file_path
config_file_path = './utils/clashspeedtest/config.yaml'

def set_config(input_file_path, output_base64_path, output_clash_Path):  
    #3个参数：
    #input_file_path需要测速的文件位置, 
    #output_base64_path，输出文件是base64格式,
    #outputClashPath是clash格式

    #打开config.yaml文件
    with open(config_file_path,encoding="UTF-8") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        f.close()
    config.update({'source' : input_file_path})
    config.update({'outfile' : output_clash_Path})
    config.update({'outfile_base64' : output_base64_path})

    #将修改完成的config.yaml写入文件
    with open(config_file_path, 'w',encoding="utf-8") as f:
        data = yaml.dump(config, f,allow_unicode=True)


if __name__ == '__main__':
    set_config(input_file_path = './sub/sources/fetchShareAll.yaml', output_base64_path = './sub/rx64', output_clash_Path = './sub/rx.yaml')


    
