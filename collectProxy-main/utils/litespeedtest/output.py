import json, base64, os, time

#调用自己的模块，先获取执行的目录，再import文件
import sys
sys.path.append(".") #执行目录地址
from utils.subConvert.sub_convert import sub_convert

out_json = './out.json'
#配置文件路径
config_file_path = './utils/litespeedtest/lite_config.json'

def get_outputpath():
    #打开config.json文件
    with open(config_file_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
        f.close() 
    outputfile_path = config['outputPath']
    output_clash_file = config['outputClashPath']
    return outputfile_path,output_clash_file

def read_json(file): # 将 out.json 内容读取为列表
    mysleeptime = 0
    print('Awaiting speedtest complete.................'+'\n')
    while os.path.isfile(file)==False:
        print('sleep time ='+ str(mysleeptime)+'\n')
        mysleeptime = mysleeptime+10
        time.sleep(10)
        #判断时间是否超过1200秒，超时20分钟
        if mysleeptime >= 1200:
            return '测速超时'
    with open(file, 'r', encoding='utf-8') as f:
        print('Reading out.json')
        proxies_all = json.load(f)
        f.close()
    return proxies_all

def output(list,num):
    output_list = []
    for index in range(num):
        #节点类型 "protocol":  "vmess","trojan","ss","ssr"
        #ping速度"ping":"0"
        #下载速度(平均/max)"avg_speed":0,"max_speed":0 
        #print('\n node '+str(index)+'ping ='+str(list[index]['ping'])+'\n')
        #print('\n node '+str(index)+'avg_speed ='+str(list[index]['avg_speed'])+'\n')
        if int(list[index]['ping']) > 0 and int(list[index]['ping']) <= 500:   
            proxy = list[index]['Link']
            output_list.append(proxy)
    print('\n out.json 可用节点数：'+str(len(output_list))+'\n')
    content = '\n'.join(output_list)
    content = base64.b64encode('\n'.join(output_list).encode('utf-8')).decode('ascii')
    output_file_path,output_clash_file = get_outputpath()
    print('\n output_file_path  =' + output_file_path + '\n')
    print('\n output_clash_file = ' + output_clash_file + '\n')
    #写入base64
    with open(output_file_path, 'w+', encoding='utf-8') as f:
        f.write(content)
        print('base64 Write Success!')
        f.close()
    input_source_file = os.path.abspath(output_file_path)  # 获取文件路径
    content = sub_convert.convert_remote(input_source_file,'clash')   #转换
    #写入clash文件
    with open(output_clash_file, 'w+', encoding='utf-8') as f:
        f.write(content)
        print('clash Write Success!')
        f.close()

if __name__ == '__main__':
    print('output out_json begin!')
    outlist=read_json(out_json)
    print('\n out.json 节点总数：'+str(len(outlist))+'\n')
    if outlist != '测速超时':
        output(outlist,len(outlist))
