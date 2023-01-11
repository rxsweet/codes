# CollectProxySource

copy https://github.com/RenaLio/proxy-minging/

## 说明

Config.yaml	--- 爬取源

main.py --- 主程序

pre_check.py --- 运行前检查，主要检测输出的路径文件夹是否存在，(不存在->创建)

requirements.txt --- 依赖包

## 设置

在main.py :
```
#爬取源
TGconfigListPath = './utils/collectTGsub/config.yaml'
#输出位置
path_yaml = './sub/sources/TGsubSources.yaml'
```
