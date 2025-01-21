import os, requests, urllib.parse, base64

source_file = './utils/airport/airportRegister/trial'
output_file = './sub/free1.yaml'
config_url = 'https://raw.githubusercontent.com/rxsweet/all/main/githubTools/clashConfig.ini'

def read_file(file):
    rfile = open(file, 'r', encoding='utf-8')
    file_content = rfile.read()
    rfile.close()
    return file_content

def write_file(file,content):
    wfile = open(file, 'w', encoding='utf-8')
    wfile.write(content)
    wfile.close()

def base64_decode(url_content): # Base64 转换为 URL 链接内容
    if '-' in url_content:
        url_content = url_content.replace('-', '+')
    if '_' in url_content:
        url_content = url_content.replace('_', '/')
    #print(len(url_content))
    missing_padding = len(url_content) % 4
    if missing_padding != 0:
        url_content += '='*(4 - missing_padding) # 不是4的倍数后加= https://www.cnblogs.com/wswang/p/7717997.html
    try:
        base64_content = base64.b64decode(url_content.encode('utf-8')).decode('utf-8','ignore') # https://www.codenong.com/42339876/
        base64_content_format = base64_content
        return base64_content_format
    except UnicodeDecodeError:
        base64_content = base64.b64decode(url_content)
        base64_content_format = base64_content
        return str(base64_content)
			
def convert(url='', output_type='clash', host='http://127.0.0.1:25500',configUrl = config_url):
    sever_host = host
    url = url.replace('\n','|') #节点转换需要用 ‘|’ 隔开
    url = urllib.parse.quote(url, safe='') # https://docs.python.org/zh-cn/3/library/urllib.parse.html
    if output_type == 'clash':
        converted_url = sever_host+'/sub?target=clash&url='+url+'&insert=false&config='+configUrl+'&emoji=false'
        try:
            resp = requests.get(converted_url)
        except Exception as err:
            print(err)
            return 'Url 解析错误'
        if resp.text == 'No nodes were found!':
            sub_content = 'Url 解析错误'
            print('Url 解析错误: No nodes were found! -->' + url + '\n')
        else:
            sub_content = resp.text
    return sub_content

if __name__ == '__main__':
    #测试
    url = read_file(source_file)
    url = base64_decode(url)
    subContent = convert(url,'clash')
    write_file(output_file,subContent)
    os.system("cp ./utils/airport/airportRegister/trial ./sub/free1.txt")
    #os.system("cp ./utils/airport/mailCloud/trial.cache ./sub/sources/mail_cloud.txt")
