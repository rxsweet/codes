import json, base64, os, time

out_json = './out.json'
config_file_path = './utils/litespeedtest/lite_config.json'

#output_file_path = './sub/sources/literx64'
def get_outputpath():
    #打开config.json文件
    with open(config_file_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
        f.close() 
    outputfile_path = config['outputPath']
    return outputfile_path
def read_json(file): # 将 out.json 内容读取为列表
    mysleeptime = 0
    while os.path.isfile(file)==False:
        print('Awaiting speedtest complete.................'+'\n')
        print('sleep time ='+ str(mysleeptime))
        mysleeptime = mysleeptime+30
        time.sleep(30)
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
        if list[index]['avg_speed'] != 0:   #速度不是0
            proxy = list[index]['Link']
            output_list.append(proxy)
    content = '\n'.join(output_list)
    content = base64.b64encode('\n'.join(output_list).encode('utf-8')).decode('ascii')
    output_file_path = get_outputpath()
    with open(output_file_path, 'w+', encoding='utf-8') as f:
        f.write(content)
        print('Write Success!')
        f.close()
    return content

if __name__ == '__main__':
    print('output out_json begin!')
    outlist=read_json(out_json)
    print('\n out.json 节点数：'+str(len(outlist))+'\n')
    if outlist != '测速超时':
        output(outlist,len(outlist))
