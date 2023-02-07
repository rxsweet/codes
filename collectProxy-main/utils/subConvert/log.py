from datetime import datetime
#日志文件位置
log_path = './sub/log.txt'

def log(msg):
    time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    print('[' + time + ']:' + msg + '\n')
    
def log_update_time(msg):

    time = datetime.today().strftime(': %Y-%m-%d %H:%M:%S')
    filetime = msg + time + '\n'
    f=open(log_path, 'r', encoding='utf-8')    # r只读，w可写，a追加
    updatetime = f.readlines()
    f.close()
    #定位str位置，修改
    for index in range(len(updatetime)):
        if msg in updatetime[index]:
            updatetime[index] = filetime
    updatetime = ''.join(updatetime)
    #如str不在文件，添加到后面
    if msg not in updatetime:
        updatetime = updatetime + filetime
    file = open(log_path, 'w', encoding= 'utf-8')
    file.write(updatetime)
    file.close()
if __name__ == '__main__':
    import sys
    msg = sys.argv[1]  #带参数执行.py文件 https://blog.csdn.net/zx77588023/article/details/126422295
    log_update_time(msg)
