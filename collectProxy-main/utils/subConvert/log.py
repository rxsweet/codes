from datetime import datetime

def log(msg):
    time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    print('[' + time + ']:' + msg + '\n')
#设置默认log文件位置   
def log_update_time(msg,log_path = './sub/log.txt'):

    time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    filetime = '[' + time + ']: ' + msg + '\n'
    f=open(log_path, 'r', encoding='utf-8')    # r只读，w可写，a追加
    updatetime = f.readlines()
    f.close()
    #查找上次更新，删除，添加新time到最后
    for index in updatetime:
        if msg in index:
            updatetime.remove(index)
    updatetime = ''.join(updatetime)
    updatetime = updatetime + filetime
    """
    #定位str位置，修改
    for index in range(len(updatetime)):
        if msg in updatetime[index]:
            updatetime[index] = filetime
    updatetime = ''.join(updatetime)
    #如str不在文件，添加到后面
    if msg not in updatetime:
        updatetime = updatetime + filetime
    """
    file = open(log_path, 'w', encoding= 'utf-8')
    file.write(updatetime)
    file.close()
if __name__ == '__main__':
    import sys
    msg = sys.argv[1]  #带参数执行.py文件 https://blog.csdn.net/zx77588023/article/details/126422295
    log_update_time(msg)
