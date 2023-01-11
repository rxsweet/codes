import requests
import json


def check(alive, proxy, apiurl, sema, timeout, testurl):
    try:
        url =apiurl + '/proxies/' + str(proxy['name']) + '/delay?url='+testurl+'&timeout=' + str(timeout)
        #print('\n测试地址'+url+'\n')
        r = requests.get(url, timeout=10)
        response = json.loads(r.text)
        #print('\n test done = '+str(proxy)+'\n')
        if response['delay'] > 0:
            alive.append(proxy)
    except:
        pass
    sema.release()
