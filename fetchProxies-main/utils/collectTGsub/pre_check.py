import sys
import os
import datetime
from loguru import logger

sub_path = 'sub' #默认存放订阅源的文件夹名称
today = datetime.datetime.today()
path_year = sub_path+'/'+str(today.year)
path_mon  = path_year+'/'+str(today.month)
path_yaml = path_mon+'/'+str(today.month)+'-'+str(today.day)+'.yaml'

@logger.catch
def pre_check():
    folder = os.path.exists(sub_path)
    if not folder:                   #判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs(sub_path) 

    folder = os.path.exists(path_year)
    if not folder:                   #判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs(path_year) 

    folder = os.path.exists(path_mon)
    if not folder:                   #判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs(path_mon)

    logger.info('初始化完成')
    return path_yaml


        
# pre_check()
  



