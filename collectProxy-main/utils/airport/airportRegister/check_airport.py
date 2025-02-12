import re
from datetime import datetime   #时间

CECHE_PATH = './trial.cache'
CFG_PATH   = './trial.cfg'
def check_airport():
    print(f'check airport in  {CFG_PATH}')
    try:
        with open(CECHE_PATH, 'r', encoding='utf-8') as file:
            cachelines = file.readlines()
        with open(CFG_PATH, 'r', encoding='utf-8') as file:
            cfglines = file.readlines()
    except FileNotFoundError:
        print("File not found.")

    bads = []
    i = 0
    lens = len(cachelines)
    while i < lens:
        if cachelines[i].startswith("["):#定位机场网址
            #print(cachelines[i])
            j = 1
            while i+j<lens:
                if 'fail_n' in cachelines[i+j]:
                    #print(cachelines[i+j])
                    num = re.search(r'(\d+)', cachelines[i+j]).group(1)
                    #print(num)
                    if int(num) >= 5:
                        bad = re.search(r'\[(.*?)\]', cachelines[i]).group(1)
                        bads.append(bad)
                if cachelines[i+j].startswith("["):#定位机场网址
                    break
                j = j + 1
        i = i + j
    #print('\n'.join(bads))
    i = 20  #需要检测的机场开始的行数
    lens = len(cfglines)
    print(f'检测前机场数量：{lens - 20}')
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
    print(f'检测后机场数量：{lens - 20}')
    with open(CFG_PATH, 'w', encoding='utf-8') as file:
        for item in cfglines:
            file.write(item)

if "__name__==__main__":#主程序开始
    nowtime = datetime.now()
    if nowtime.weekday() == 4 and nowtime.hour < 12:#每周五早12点前检测
        print("检测删除不可用机场！")
        check_airport()
    else:
        print("本次不检测删除！")
