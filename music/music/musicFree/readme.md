musicFree源目录

```
#测试落雪音源是否可用
import requests

def getUrlContent(url):  
    headers={
    "X-Request-Key": "LXMusic_dmsowplaeq"
    }
    print(url)
    try:
        r=requests.get(url,headers=headers, timeout=5.0)
        print(r.text)
        if r.status_code==200:
            r.encoding='utf-8'    #编码方式
            print(r.text)
            return r.text
    except requests.exceptions.RequestException as e:  
        print(e)
        print('getUrlContent()功能中出现的错误！获取js内容失败，或者打开网址错误!')
        return None
        
        
        
if "__name__==__main__":#主程序开始
    getUrlContent('https://ikun.laoguantx.top:19742/url/kw/228908/128k')
#kw,kg,wy,mg,tx
```

返回成功和错误的例子
```

https://ikun.laoguantx.top:19742/url/kw/228908/128k
{
  "code": 4,
  "msg": "内部服务器错误",
  "data": null
}

{
  "code": 2,
  "msg": "failed",
  "data": null
}
{
  "code": 2,
  "msg": "failed",
  "data": null
}
https://ikun.laoguantx.top:19742/url/kw/228908/128k
{
  "code": 0,
  "info": "酷我音乐_None_228908_标准音质 128K",
  "msg": "成功",
  "data": "http:\/\/lu.sycdn.kuwo.cn\/35641c843fa42139684cf73bb5b359b1\/674d1e1b\/resource\/a3\/62\/85\/1540075080.aac",
  "ip": "118.74.52.52",
  "time": {
    "start_time": 1733107390.6161783,
    "end_time": 1733107390.6166964,
    "use_time": 0.0005180835723876953
  },
  "extra": {
    "cache": true,
    "size": "3.14MB",
    "quality": {
      "target": "标准音质 128K",
      "result": "标准音质 128K"
    },
    "expire": {
      "time": 1733108127,
      "canExpire": true
    }
  }
}

```
