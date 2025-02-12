大佬仓库 - https://github.com/wzdnzd/aggregator

collect.py --文件，主程序入口，修改较多

```
1.
#生成完整配置的clash,"generate full configuration for clash",，开启了
default=True,
#覆盖域名"overwrite domains"，开启了
default=True,
#抓取电报时的 ax 页码，"max page number when crawling telegram"，改成了30页
default=30,
#跳过可用性检查，"skip usability checks",开启了
default=True,
#生成文件，改了
default=["clash", "v2ray"],

2. 主main(),aggregate(args=parser.parse_args())#主程序开始，在他下面添加的
    #自己添加保存日志文件
    WORKFLOW_LOG = PATH + '/workflow.log'
    LOG_TXT = PATH + '/data/log.txt'
    os.system(f"cp {WORKFLOW_LOG} {LOG_TXT}")

3.  禁用了#选择clash和subconverter程序，改成自己的了
    #clash_bin, subconverter_bin = executable.which_bin()    #选择clash和subconverter程序
    
    #没有clash和subconverter程序时,下面的安装起作用,注意下面的地址是否还可以访问
    #安装subconverter
    SUB_PATH = os.path.join(PATH, "subconverter.tar.gz")
    if not os.path.exists(SUB_PATH):
        #os.system(f"wget -O {SUB_PATH} https://github.com/tindy2013/subconverter/releases/latest/download/subconverter_linux64.tar.gz")
        os.system(f"wget -O {SUB_PATH} https://github.com/lonelam/subconverter/releases/latest/download/subconverter_linux64.tar.gz")
    os.system(f"tar -zxvf {SUB_PATH} -C {PATH}")
    subconverter_bin = 'subconverter'
    #安装clash
    CLASH_BASE = os.path.join(PATH, "clash")
    CLASH_PATH = os.path.join(CLASH_BASE, "clash-linux-amd")
    if not os.path.exists(CLASH_BASE):
        os.makedirs(CLASH_BASE)
        if not os.path.exists(CLASH_PATH):
            os.system(F"wget -O {CLASH_PATH} https://raw.githubusercontent.com/wzdnzd/aggregator/refs/heads/main/clash/clash-linux-amd")
        #安装Country.mmdb
        Country_PATH = os.path.join(CLASH_BASE, "Country.mmdb")
        if not os.path.exists(Country_PATH):
            os.system(F"wget -O {Country_PATH} https://raw.githubusercontent.com/wzdnzd/aggregator/refs/heads/main/clash/Country.mmdb")
    clash_bin = 'clash-linux-amd'

4.自己添加了不少说明

```

crawl.py --文件，collect_airport()抓取TG，和网站的免费机场，内部函数比较多

workflow.py --文件，修改了execute()

```
#自己添加的if，去掉不能用的信息,不显示
    if obj.username == '' or len(proxies) == 0:
        return []

#log添加了显示邮箱
logger.info(
        #f"finished fetch proxy: name=[{task_conf.name}]\tid=[{task_conf.index}]\tdomain=[{obj.ref}]\tcount=[{len(proxies)}]"
        f"finished fetch proxy: name=[{task_conf.name}]\tusername=[{obj.username}]\tdomain=[{obj.ref}]\tcount=[{len(proxies)}]"
    )
```

airport.py --文件，
```
1.修改了get_subscribe()
#自己重新编辑注册信息,
#email = utils.random_chars(length=random.randint(6, 10), punctuation=False)
#password = utils.random_chars(length=random.randint(8, 16), punctuation=True)#最小8位，最多16位，punctuation=True是可用标点符号
email = utils.random_chars(length=random.randint(8, 16), punctuation=False)
password = email

2.修改了parse()
去掉了几个错误的显示
#logger.error(f"[ParseError] cannot found any proxies because subscribe url is empty, domain: {self.ref}")
#logger.error(f"[ParseError] cannot found any proxies, subscribe: {utils.mask(url=self.sub)}")
#logger.info(f"cannot found any proxy, domain: {self.ref}")
```

utils.py --文件，mask()

```
#去掉不显示token
        if "token=" in parse_result.query:
            token = "".join(re.findall("token=([a-zA-Z0-9]+)", parse_result.query))
            #去掉不显示token
            #if len(token) >= 6:
                #token = token[:3] + "***" + token[-3:]
            url = f"{parse_result.scheme}://{parse_result.netloc}{parse_result.path}?token={token}"
        else:
            path, token = parse_result.path.rsplit("/", maxsplit=1)
            #if len(token) >= 6:
                #token = token[:3] + "***" + token[-3:]
            url = f"{parse_result.scheme}://{parse_result.netloc}{path}/{token}"
```
subconverter.py --文件，generate_conf()

```
        lines.append(f"target={goal}")#这行下面添加的配置
        #添加config配置文件
        lines.append(f"config=https://raw.githubusercontent.com/rxsweet/all/main/githubTools/clashConfig.ini")
```
