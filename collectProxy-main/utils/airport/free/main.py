import freev2
import qqfreev2
import freess
import getafreenode_com

out_list_file_path = './sub/sources/sublist_free.txt'

if __name__=='__main__':
    
    # 获取 V2board 类网站的，需用Gmail邮箱注册的订阅信息
    freev2.get_conf()
    # 获取 V2board 类网站的，需用QQ邮箱注册的订阅信息
    #qqfreev2.get_conf() 
    
    freess.get_conf()
    
    #获取getafreenode.com订阅地址，添加进去
    getafreenode = getafreenode_com.getafreenodeUpdate()
    with open(out_list_file_path, 'a') as f:
        f.write(getafreenode+'\n') 
