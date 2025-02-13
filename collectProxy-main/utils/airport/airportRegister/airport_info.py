#得到机场信息，删除不可用的机场
import re
import yaml

CECHE_PATH = './trial.cache'
CFG_PATH   = './trial.cfg'
AIRPORT_INFO_PATH = './sub_info.yaml'
def airport_info():
    print(f'get airport info and check airport in  {CFG_PATH}')
    try:
        with open(CECHE_PATH, 'r', encoding='utf-8') as file:
            cachelines = file.readlines()
        with open(CFG_PATH, 'r', encoding='utf-8') as file:
            cfglines = file.readlines()
    except FileNotFoundError:
        print("File not found..--> airport_info() return")
        return

    aiport_info = {}
    bads = []
    i = 0
    lens = len(cachelines)
    while i < lens:
        if cachelines[i].startswith("["):#定位机场网址
            info  = {}
            url = re.search(r'\[(.*?)\]', cachelines[i]).group(1)
            info['url'] = url
            #print(url)
            j = 1
            fail = False
            while i+j<lens:
                if 'name  ' in cachelines[i+j]:
                    name = re.search(r'name  (.*$)', cachelines[i+j]).group(1)
                    info['name'] = name
                if 'email  ' in cachelines[i+j]:
                    email = re.findall('email  (.*)', cachelines[i+j])
                    info['email'] = email[0]
                if 'node_n  ' in cachelines[i+j]:
                    node_n = re.search(r'node_n  (.*$)', cachelines[i+j]).group(1)
                    info['node_n'] = node_n
                if 'sub_info  ' in cachelines[i+j]:
                    sub_info = re.search(r'sub_info  (.*$)', cachelines[i+j]).group(1)
                    info['sub_info'] = sub_info
                if 'sub_url  ' in cachelines[i+j]:
                    api = re.search(r'sub_url  (.*$)', cachelines[i+j]).group(1)
                    info['api'] = api
                if 'type  ' in cachelines[i+j]:
                    air_type = re.search(r'type  (.*$)', cachelines[i+j]).group(1)
                    info['type'] = air_type
                if 'fail_n  ' in cachelines[i+j]:
                    fail = True
                    num = re.search(r'(\d+)', cachelines[i+j]).group(1)
                    if int(num) > 5:
                        bad = re.search(r'\[(.*?)\]', cachelines[i]).group(1)
                        bads.append(bad)#将失败5次以上的不可用机场记录
                if cachelines[i+j].startswith("["):#机场信息结束，下个机场位置
                    if fail == False:
                        aiport_info[url] = info
                    break
                j = j + 1
        i = i + j
    
    #将得到的机场信息保存
    with open(AIRPORT_INFO_PATH, 'w',encoding="utf-8") as f:
        data = yaml.dump(aiport_info, f,allow_unicode=True)
        
    #删除不可用的机场
    i = 20  #需要检测的机场开始的行数
    lens = len(cfglines)
    print(f'开始删除失败次数大于5的机场：')
    print(f'删除前机场数量：{lens - 20}')
    for bad in bads:
        while i < lens:
            if 'buy  period=' in cfglines[i]:
                url = re.search(r'(.*?)  buy  period=', cfglines[i]).group(1)
                if url in bad:
                    #print(cfglines[i])
                    cfglines.pop(i)
                    lens = lens -1
                    break
            elif bad in cfglines[i]:
                #print(cfglines[i])
                cfglines.pop(i)
                lens = lens -1
                break
            i = i + 1
    print(f'删除后机场数量：{lens - 20}')
    #将检测完的机场信息保存
    with open(CFG_PATH, 'w', encoding='utf-8') as file:
        for item in cfglines:
            file.write(item)

if "__name__==__main__":#主程序开始
    airport_info()
