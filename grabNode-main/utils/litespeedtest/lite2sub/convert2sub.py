import os
from sub_convert import sub_convert

#文件位置
input_source_file = './sub/literx64'
output_file = './sub/literxClash.yml'

if __name__ == '__main__':
    #转换
    input_source_file = os.path.abspath(input_source_file)  # 获取文件路径
    content = sub_convert.convert_remote(input_source_file,'clash')   #转换

    #写入
    file = open(output_file, 'w', encoding= 'utf-8')
    file.write(content)
    file.close()
    print(f'Writing content done！\n')
