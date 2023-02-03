from datetime import datetime
#日志文件位置
log_path = './sub/log.txt'

def log_update_time(str):

    today = datetime.today().strftime(': %Y-%m-%d %H:%M:%S')
    f=open(log_path, 'r', encoding='utf-8')    # r只读，w可写，a追加
    updatetime = f.readlines()
    f.close()
    for index in range(len(updatetime)):
        if str in updatetime[index]:
            updatetime[index] = str + today + '\n'
    updatetime = ''.join(updatetime)
    file = open(log_path, 'w', encoding= 'utf-8')
    file.write(updatetime)
    file.close()
if __name__ == '__main__':
    import sys
    info = sys.argv[1]  #带参数执行.py文件 https://blog.csdn.net/zx77588023/article/details/126422295
    log_update_time(info)
