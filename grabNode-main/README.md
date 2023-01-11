# grad node

## copy source
> fetch code copy [alanbobs999/TopFreeProxies](https://github.com/alanbobs999/TopFreeProxies)
>
>testspeed code copy [daycat/clashcheck/](https://github.com/daycat/clashcheck/)
>
>转码功能用的的工具[tindy2013/subconverter](https://github.com/tindy2013/subconverter/)
>
>借鉴了这个大哥的好多代码 [/yu-steven/openit](https://github.com/yu-steven/openit)
>
>大佬的测速工具[xxf098/LiteSpeedTest](https://github.com/xxf098/LiteSpeedTest)
>
>ACL4SSR转换规则[ACL4SSR](https://github.com/ACL4SSR/ACL4SSR/tree/master)

虽然是测速筛选过后的节点，但仍然会出现部分节点不可用的情况，遇到这种情况
建议选择`Clash`, `Shadowrocket`之类能自动切换低延迟节点的客户端。

## 节点信息

### 已测速节点
已测速节点数量: `156`

### 所有节点
合并节点总数: `1561`
### 节点来源
- [freefq/free](https://github.com/freefq/free), 节点数量: `39`
- [learnhard-cn/free_proxy_ss](https://github.com/learnhard-cn/free_proxy_ss), 节点数量: `90`
- [vpei/Free-Node-Merge](https://github.com/vpei/Free-Node-Merge), 节点数量: `747`
- [huwo.club](https://github.com/colatiger/v2ray-nodes), 节点数量: `71`
- [kxswa/k](https://github.com/kxswa/k), 节点数量: `73`
- [ermaozi/get_subscribe](https://github.com/ermaozi/get_subscribe), 节点数量: `52`
- [changfengoss](https://github.com/ronghuaxueleng/get_v2), 节点数量: `0`
- [anaer/Sub](https://github.com/anaer/Sub), 节点数量: `138`
- [Pawdroid/Free-servers](https://github.com/Pawdroid/Free-servers), 节点数量: `5`
- [Rokate/Proxy-Sub](https://github.com/Rokate/Proxy-Sub), 节点数量: `399`
- [aiboboxx/v2rayfree](https://github.com/aiboboxx/v2rayfree), 节点数量: `42`
- [tbbatbb/Proxy](https://github.com/tbbatbb/Proxy), 节点数量: `376`
- [1808.ga](https://1808.ga/), 节点数量: `156`
- [gitlab.com/univstar1](https://gitlab.com/univstar1/v2ray/), 节点数量: `100`
- [xiyaowong/freeFQ](https://github.com/xiyaowong/freeFQ), 节点数量: `152`
- [ripaojiedian/freenode](https://github.com/ripaojiedian/freenode), 节点数量: `15`
- [Junely/clash](https://github.com/Junely/clash), 节点数量: `309`

## 仓库文档
<details>
  <summary>展开查看仓库文档</summary>

```
fetchPorxy.main
├── .github──workflows──fetchProxy.yml(actions Deploy)
├── config
│   ├── provider
│   │   ├── config.yml(转clash订阅用的配置)
│   │   └── rxconfig.ini(转clash订阅用的ACL4SSR配置)
│   └── sub_list.json(订阅列表)   
├── sub
│   ├── source(收集到的源节点文件)
│   │   ├── list──(存放着订阅列表里每个源的节点数据)
│   │   ├── check.yaml(测速后的节点数据，靠此文件转换成订阅文件)
│   │   ├── sub_merge.txt(爬取到的节点合集url格式)
│   │   ├── sub_merge_base64.txt(爬取到的节点合集base64格式)
│   │   └── sub_merge_yaml.yml(爬取到的节点合集YAML格式)
│   ├── checkBakup(lite测速结果备份)
│   │   ├── out.json(lite测速结果)
│   │   └── speedtest.log(lite测速结果日志)
│   ├── nocheckClash.yml(未测速clash订阅文件)
│   ├── rx(url订阅文件)
│   ├── rx64(base64订阅文件)
│   ├── rxClash.yml(测速后订阅文件)
│   ├── literx(lite测速后订阅文件)
│   └── literxClash.yml(lite测速后订阅文件)
├── utils(程序功能模块)
│   ├── fetch(获取)
│   │   ├── ip_update.py(下载country.mmdb文件，默认output->'./country.mmdb')
│   │   ├── list_update.py(更新订阅列表sub_list.json，'有变换订阅地址的需更新')
│   │   ├── list_merge.py(主程序，获取订阅存放到'./sub/source/'里面的3种格式，更新README.md里面的订阅源信息)
│   │   └── sub_convert.py(转换订阅格式的功能模块，用到了'tindy2013/subconverter')
│   ├── checkclash(测速)
│   │   ├── config.yaml(配置文件，里面设置，源文件位置，输出文件位置)
│   │   ├── init.py(里面设置config.yaml文件位置)
│   │   ├── main.py(多线程测速)
│   │   ├── clash.py(main调用模块)
│   │   ├── check.py(main调用模块)
│   │   └── requirements.txt(此模块依赖库)
│   ├── convert2sub(转换成订阅)
│   │   ├── ip_update.py(下载country.mmdb文件，默认output->'./country.mmdb')
│   │   ├── convert2sub.py(转换节点文件到'./sub/'目录下的订阅文件)
│   │   └── sub_convert.py(转换订阅格式的功能模块，用到了'tindy2013/subconverter')
│   ├── litespeedtest(lite测速模块)
│   │   ├── lite2sub -测速完成后转clash订阅
│   │ 	│	├── convert2sub.py(转换节点文件到'./sub/'目录下的订阅文件)
│   │ 	│	└── sub_convert.py(转换订阅格式的功能模块，用到了'tindy2013/subconverter')
│   │   ├── clash_config.yml(clash配置文件，测速要用到)
│   │   ├── lite_config.json(测速lite配置文件，设置测速文件位置等)
│   │   ├── proxychains.conf(Action要用此代理打开lite测速才不会卡住不动)
│   │   ├── speedtest.sh(lite测速运行,输出out.json,speedtest.log)
│   │   └── output.py(将测速结果out.json，转换成url订阅'./sub/literx')
│   └── requirements.txt(依赖库)
└── README.md
```
</details>

### 使用注意
>转码功能用到的`subconverter工具`
>
>测速功能用到的`clash工具`
>
>IP库`country.mmdb`,
>
>测速工具`LiteSpeedTest`
>
>已备份到'rx/all/githubTools'

## 仓库声明
订阅节点仅作学习交流使用，只是对网络上节点的优选排序，用于查找资料，学习知识，不做任何违法行为。所有资源均来自互联网，仅供大家交流学习使用，出现违法问题概不负责。
