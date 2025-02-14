import re
import requests
import json
import time
from datetime import datetime
import configparser

MUSIC_LOG = './music/log.txt'
#MUSIC_LOG = './log.txt'
md5_addr = "./music/musicFree/md5.ini"

#调用的API接口
api1 = 'https://lxmusicapi.onrender.com'
api2 = 'https://lxmusic.ikunshare.com'
api3 = 'https://ikun.laoguantx.top:19742/QAQ'
api4 = 'https://m-api.ceseet.me'

#musicfree音源
plugins1 = 'https://rxsub.eu.org/music/musicFree/Huibq/rx.json'
plugins2 = 'https://rxsub.eu.org/music/musicFree/ikun0014/rx.json'
plugins3 = 'https://rxsub.eu.org/music/musicFree/musicDownloader/rx.json'
plugins4 = 'https://rxsub.eu.org/music/musicFree/fish/rx.json'
my_plugins = 'https://rxsub.eu.org/music/musicFree/my/rx.json'

#落雪音源
lx_api1 = 'https://ghraw.eu.org/Huibq/keep-alive/master/render_api.js'
lx_api2 = 'https://lxmusic.ikunshare.com/script'
lx_api3 = 'https://ikun.laoguantx.top:19742/script?key=LXMusic_dmsowplaeq'
lx_api4 = 'https://m-api.ceseet.me/script'

#优先顺序
good_list = ['ikun0014','musicDownloader','fish','Huibq']

def getUrlContent(url):  
    headers={
    "X-Request-Key": "LXMusic_dmsowplaeq"
    #"X-Request-Key": "share-v2"
    }
    print(url)
    try:
        r=requests.get(url,headers=headers, timeout=5.0)
        #print(r.text)
        if r.status_code==200:
            r.encoding='utf-8'    #编码方式
            #print(r.text)
            try:
                jsontext=json.loads(r.text)
                if 'data' in jsontext and 'http' in jsontext['data']:
                    #print(jsontext['data'])
                    #print('可用')
                    return '可用'
            except Exception as e:  
                pass
        #print('不可用')
        return '不可用'
    except requests.exceptions.RequestException as e:  
        print(e)
        print('getUrlContent()功能中出现的错误！获取js内容失败，或者打开网址错误!')
        #print('不可用')
        return '不可用'

#Huibq大佬专用: headers_key不同,地址key也不是data,而是url
def getUrlContent1(url):  
    headers={
    "X-Request-Key": "share-v2"
    }
    print(url)
    try:
        r=requests.get(url,headers=headers, timeout=5.0)
        #print(r.text)
        if r.status_code==200:
            r.encoding='utf-8'    #编码方式
            #print(r.text)
            try:
                jsontext=json.loads(r.text)
                if 'url' in jsontext and 'http' in jsontext['url']:
                    #print(jsontext['data'])
                    return '可用'
            except Exception as e:  
                pass
        return '不可用'
    except requests.exceptions.RequestException as e:  
        print(e)
        print('getUrlContent()功能中出现的错误！获取js内容失败，或者打开网址错误!')
        return '不可用'

#将可用api汇总成rx
def diy_my(rx_api):
    #开始编辑文件

    #编辑kg音乐文件
    try:
        with open(f"./music/musicFree/{rx_api['kg']}/kg.js", 'r', encoding='utf-8') as file:
            file_content = file.read()
    except:
        print("open read File err..--> return")
        return
    try:
        #修改显示名字
        old_name_list = re.findall(r'platform: ".*?",',file_content)
        for old_name in old_name_list:
            new_name = f'platform: "酷狗",'
            file_content = re.sub(old_name, new_name, file_content)
        #修改更新地址
        old_url_list = re.findall(r'srcUrl: "(.*?).js"',file_content)
        old_url = old_url_list[0]
        new_url = 'https://rxsub.eu.org/music/musicFree/my/kg'
        file_content = re.sub(old_url, new_url, file_content)
        #写入文件
        file = open("./music/musicFree/my/kg.js", "w")
        file.write(file_content)
        file.close()
        print("酷狗音乐 update 成功!")
    except Exception as e:#万能异常
        print(str(e) + 'Exception_出现异常')
        pass
        
    #编辑kw音乐文件
    try:
        with open(f"./music/musicFree/{rx_api['kw']}/kw.js", 'r', encoding='utf-8') as file:
            file_content = file.read()
    except:
        print("open read File err..--> return")
        return
    try:
        #修改显示名字
        old_name_list = re.findall(r'platform: ".*?",',file_content)
        for old_name in old_name_list:
            new_name = f'platform: "酷我",'
            file_content = re.sub(old_name, new_name, file_content)
        #修改更新地址
        old_url_list = re.findall(r'srcUrl: "(.*?).js"',file_content)
        old_url = old_url_list[0]
        new_url = 'https://rxsub.eu.org/music/musicFree/my/kw'
        file_content = re.sub(old_url, new_url, file_content)
        #写入文件
        file = open("./music/musicFree/my/kw.js", "w")
        file.write(file_content)
        file.close()
        print("酷我音乐 update 成功!")
    except Exception as e:#万能异常
        print(str(e) + 'Exception_出现异常')
        pass
        
    #编辑wy音乐文件
    try:
        with open(f"./music/musicFree/{rx_api['wy']}/wy.js", 'r', encoding='utf-8') as file:
            file_content = file.read()
    except:
        print("open read File err..--> return")
        return
    try:
        #修改显示名字
        old_name_list = re.findall(r'platform: ".*?",',file_content)
        for old_name in old_name_list:
            new_name = f'platform: "网易云",'
            file_content = re.sub(old_name, new_name, file_content)
        #修改更新地址
        old_url_list = re.findall(r'srcUrl: "(.*?).js"',file_content)
        old_url = old_url_list[0]
        new_url = 'https://rxsub.eu.org/music/musicFree/my/wy'
        file_content = re.sub(old_url, new_url, file_content)
        #写入文件
        file = open("./music/musicFree/my/wy.js", "w")
        file.write(file_content)
        file.close()
        print("网易云音乐 update 成功!")
    except Exception as e:#万能异常
        print(str(e) + 'Exception_出现异常')
        pass
        
    #编辑QQ音乐文件
    try:
        with open(f"./music/musicFree/{rx_api['tx']}/qq.js", 'r', encoding='utf-8') as file:
            file_content = file.read()
    except:
        print("open read File err..--> return")
        return
    try:
        #修改显示名字
        old_name_list = re.findall(r'platform: ".*?",',file_content)
        for old_name in old_name_list:
            new_name = f'platform: "QQ",'
            file_content = re.sub(old_name, new_name, file_content)
        #修改更新地址
        old_url_list = re.findall(r'srcUrl: "(.*?).js"',file_content)
        old_url = old_url_list[0]
        new_url = 'https://rxsub.eu.org/music/musicFree/my/qq'
        file_content = re.sub(old_url, new_url, file_content)
        #写入文件
        file = open("./music/musicFree/my/qq.js", "w")
        file.write(file_content)
        file.close()
        print("qq音乐 update 成功!")
    except Exception as e:#万能异常
        print(str(e) + 'Exception_出现异常')
        pass
    
    print(f"{rx_api['kg']}, {rx_api['kw']}, {rx_api['wy']}, {rx_api['tx']}")

#按优先顺序查找可用api
def find_api(rx_api):
    for good in good_list:
        if rx_api['kg'] == '':
            if all_api[good]['kg'] == '可用':
                rx_api['kg'] = good
        if rx_api['kw'] == '':
            if all_api[good]['kw'] == '可用':
                rx_api['kw'] = good
        if rx_api['wy'] == '':
            if all_api[good]['wy'] == '可用':
                rx_api['wy'] = good
        if rx_api['tx'] == '':
            if all_api[good]['tx'] == '可用':
                rx_api['tx'] = good
    print(f"rx_kg ={rx_api['kg']} , rx_kw ={rx_api['kw']} , rx_wy ={rx_api['wy']} , rx_tx ={rx_api['tx']}")
    #如果都不可用，先随便设置一个
    if rx_api['kg'] == '':
        rx_api['kg'] = 'musicDownloader'
    if rx_api['kw'] == '':
        rx_api['kw'] = 'musicDownloader'
    if rx_api['wy'] == '':
        rx_api['wy'] = 'musicDownloader'
    if rx_api['tx'] == '':
        rx_api['tx'] = 'musicDownloader'
        
#测试API,将记录保存至all字典
def testMusicApi(all_api):
    #获取musicDownloader的最新API，他的API总是在变动
    config = configparser.ConfigParser()
    config.read(md5_addr)
    api3 = config.get("musicDown_md5", "api")
    
    #https://api.jkyai.top/API/hqyyid.php?name=传奇&type=qq&page=1&limit=10   #获取歌曲ID
    #1.心愿 王菲,  2.爱错 王力宏,  3.多远都要在一起  邓紫棋,  4.传奇  王菲,  5.爱我还是他   陶喆,  6.唯一  邓紫棋,  7.红豆  王菲
    kg_music = ['ec1a18bbd6b61cb203e656b91f5cf2d1','EC25602B56D5DAE36B27E82780FC6A22','A0AE93E5D475CBC7B52C6F45A7403F98','A72FE2B2521CE45FD632AC3E559F6691','004A93C3A157D825B92A91EEB17DA36A','AB05B8F658851282DCB2CBAD548AEB9B','AEF916A18BAAE9C8E7807179C8DA64D1']
    kw_music = ['193290598','102428','6307329','892063','103134','321260769','169744']
    wy_music = ['1888381008','1301736461','30612793','298838','150432','2083785152','299936']
    tx_music = ['001ufyHx10iWpg','004fneUm24gD2c','001fNHEf1SFEFN','002twZxX087cPx','003ofGzS3C23Ow','002d6m7k0xCbSv','0011nEwm2XPayS']
    #根据时间，确定使用哪首歌，怕源封IP检测
    #周几就用第几首
    nowtime = datetime.now()
    song_id = nowtime.weekday()
    kg_song = kg_music[song_id]
    kw_song = kw_music[song_id]
    wy_song = wy_music[song_id]
    tx_song = tx_music[song_id]
    #生成字典数据
    all_api['Huibq'] = {}
    all_api['ikun0014'] = {}
    all_api['musicDownloader'] = {}
    all_api['fish'] = {}
    #开始测试
    kg1 = getUrlContent1(f'{api1}/url/kg/{kg_song}/320k')#酷狗
    kg2 = getUrlContent(f'{api2}/url/kg/{kg_song}/320k')#酷狗
    kg3 = getUrlContent(f'{api3}/url/kg/{kg_song}/320k')#酷狗
    kg4 = getUrlContent(f'{api4}/url/kg/{kg_song}/320k')#酷狗
    time.sleep(6)
    kw1 = getUrlContent1(f'{api1}/url/kw/{kw_song}/320k')#酷我
    kw2 = getUrlContent(f'{api2}/url/kw/{kw_song}/320k')#酷我
    kw3 = getUrlContent(f'{api3}/url/kw/{kw_song}/320k')#酷我
    kw4 = getUrlContent(f'{api4}/url/kw/{kw_song}/320k')#酷我
    time.sleep(6)
    wy1 = getUrlContent1(f'{api1}/url/wy/{wy_song}/320k')#网易云
    wy2 = getUrlContent(f'{api2}/url/wy/{wy_song}/320k')#网易云
    wy3 = getUrlContent(f'{api3}/url/wy/{wy_song}/320k')#网易云
    wy4 = getUrlContent(f'{api4}/url/wy/{wy_song}/320k')#网易云
    time.sleep(6)
    tx1 = getUrlContent1(f'{api1}/url/tx/{tx_song}/128k')#QQ音乐
    tx2 = getUrlContent(f'{api2}/url/tx/{tx_song}/128k')#QQ音乐
    tx3 = getUrlContent(f'{api3}/url/tx/{tx_song}/128k')#QQ音乐
    tx4 = getUrlContent(f'{api4}/url/tx/{tx_song}/128k')#QQ音乐
    #赋值
    all_api['Huibq']['kg'] = kg1
    all_api['Huibq']['kw'] = kw1
    all_api['Huibq']['wy'] = wy1
    all_api['Huibq']['tx'] = tx1
    all_api['ikun0014']['kg'] = kg2
    all_api['ikun0014']['kw'] = kw2
    all_api['ikun0014']['wy'] = wy2
    all_api['ikun0014']['tx'] = tx2
    all_api['musicDownloader']['kg'] = kg3
    all_api['musicDownloader']['kw'] = kw3
    all_api['musicDownloader']['wy'] = wy3
    all_api['musicDownloader']['tx'] = tx3
    all_api['fish']['kg'] = kg4
    all_api['fish']['kw'] = kw4
    all_api['fish']['wy'] = wy4
    all_api['fish']['tx'] = tx4
    
if "__name__==__main__":#主程序开始

    #测试API,将记录保存至all_api字典
    all_api = {}
    testMusicApi(all_api)

    #按优先顺序查找可用api
    rx_api = {'kg':'','kw':'','wy':'','tx':''}
    find_api(rx_api)

    #将可用api汇总成可用的rx_api
    diy_my(rx_api)

    #添加日志
    alive1 = f" plugins: {plugins1}\n lxmusic: {lx_api1}\n api    : {api1}\n <音乐>   : kg[{all_api['Huibq']['kg']}],kw[{all_api['Huibq']['kw']}],wy[{all_api['Huibq']['wy']}],tx[{all_api['Huibq']['tx']}]"
    alive2 = f" plugins: {plugins2}\n lxmusic: {lx_api2}\n api    : {api2}\n -音乐- : kg[{all_api['ikun0014']['kg']}],kw[{all_api['ikun0014']['kw']}],wy[{all_api['ikun0014']['wy']}],tx[{all_api['ikun0014']['tx']}]"
    alive3 = f" plugins: {plugins3}\n lxmusic: {lx_api3}\n api    : {api3}\n [音乐] : kg[{all_api['musicDownloader']['kg']}],kw[{all_api['musicDownloader']['kw']}],wy[{all_api['musicDownloader']['wy']}],tx[{all_api['musicDownloader']['tx']}]"
    alive4 = f" plugins: {plugins4}\n lxmusic: {lx_api4}\n api    : {api4}\n =音乐= : kg[{all_api['fish']['kg']}],kw[{all_api['fish']['kw']}],wy[{all_api['fish']['wy']}],tx[{all_api['fish']['tx']}]"
    my_plug = f" plugins: {my_plugins}\n 音乐 : kg[{rx_api['kg']}], kw[{rx_api['kw']}], wy[{rx_api['wy']}], tx[{rx_api['tx']}]"
    output_list = []
    testtime = datetime.today().strftime('测试时间: %Y_%m_%d')
    output_list.append(testtime)
    output_list.append('---------')
    output_list.append(alive1)
    output_list.append('---------')
    output_list.append(alive2)
    output_list.append('---------')
    output_list.append(alive3)
    output_list.append('---------')
    output_list.append(alive4)
    output_list.append('---------')
    output_list.append(my_plug)
    output_list.append('---------')

    #写入log.txt
    output_list_str = '\n'.join(output_list)
    print('测试结果：')
    print(output_list_str)
    file = open(MUSIC_LOG, 'w', encoding='utf-8')
    file.write(output_list_str)
    file.close()

