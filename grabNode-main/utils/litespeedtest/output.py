import json, base64, os, time

out_json = './out.json'
output_file_path = './sub/literx64'

def read_json(file): # 将 out.json 内容读取为列表
    mysleeptime = 0
    while os.path.isfile(file)==False:
        print('Awaiting speedtest complete.................'+'\n')
        print('sleep time ='+ str(mysleeptime))
        mysleeptime = mysleeptime+30
        time.sleep(30)
    with open(file, 'r', encoding='utf-8') as f:
        print('Reading out.json')
        proxies_all = json.load(f)
        f.close()
    return proxies_all

def output(list,num):
    output_list = []
    for index in range(num):
        proxy = list[index]['Link']
        output_list.append(proxy)
        content = '\n'.join(output_list)
    content = base64.b64encode('\n'.join(output_list).encode('utf-8')).decode('ascii')
    with open(output_file_path, 'w+', encoding='utf-8') as f:
        f.write(content)
        print('Write Success!')
        f.close()
    return content

if __name__ == '__main__':
    print('output out_json begin!')
    outlistfile=read_json(out_json)
    output(outlistfile,200)
