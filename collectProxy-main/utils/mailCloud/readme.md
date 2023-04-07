# fork zsokami/sub
[https://github.com/zsokami/sub](https://github.com/zsokami/sub)

[https://github.com/BUGOAO/SUBTEST - 机场合集](https://github.com/BUGOAO/SUBTEST)


**collectProxy修改的地方：**
get_trial.py注释掉了开始的部分代码
```
if __name__ == '__main__':
    """
    pre_repo = read('.github/repo_get_trial')
    cur_repo = os.getenv('GITHUB_REPOSITORY')
    if pre_repo != cur_repo:
        remove('trial.cache')
        write('.github/repo_get_trial', cur_repo)
    """
```
api.py添加了class MailTm(TempEmailSession):
```
class MailTm(TempEmailSession):
    def __init__(self):
        super().__init__('api.mail.tm')

    def get_domains(self) -> list[str]:
        r = self.get('domains')
        if r.status_code != 200:
            raise Exception(f'获取 {self.host} 邮箱域名失败: {r}')
        return [item['domain'] for item in r.json()['hydra:member']]

    def set_email_address(self, address: str):
        account = {'address': address, 'password': address.split('@')[0]}
        r = self.post('accounts', json=account)
        if r.status_code != 201:
            raise Exception(f'创建 {self.host} 账户失败: {r}')
        r = self.post('token', json=account)
        if r.status_code != 200:
            raise Exception(f'获取 {self.host} token 失败: {r}')
        self.headers['Authorization'] = f'Bearer {r.json()["token"]}'

    def get_messages(self) -> list[str]:
        r = self.get('messages')
        return [
            r.json()['text']
            for r in parallel_map(self.get, (f'messages/{item["id"]}' for item in r.json()['hydra:member']))
            if r.status_code == 200
        ] if r.status_code == 200 else []

```

==============================

个人使用单个仓库使用修改的地方:
1.get_trial.py
```
base64_path='./sub/v.txt',
clash_path='./sub/v.yaml',
```
2.api.py
```
#sessions = MailGW(), Snapmail(), Emailnator(), Rootsh(), Linshiyou(), MailCX(), GuerrillaMail(), Moakt()
#sessions = MailGW(), Snapmail(), Emailnator(), Rootsh(), Linshiyou()
#下面这2个临时邮箱，注册多数黑名单
```
3.subconverter.py
```
_get_sc_config_url()
#先用以前的方法，避免使用GITHUB_TOKEN
data = Session().get('https://api.github.com/repos/zsokami/ACL4SSR/git/refs/heads/main').json()

_gen_clash_config()

 #先注释掉，不写_pp
    #prefix, ext = os.path.splitext(clash_path)
    #write(f'{prefix}_pp{ext}', lambda f: y.dump(cfg, f))
```

结构图
```
sub.main
├── .github──workflows──get_trial.yml	#actions Deploy
│   └── repo_get_trial	#存放的github目录 rxsweet/sub 
│
├── trials_providers	#每个机场的节点分组 
│   ├── mrli.me
│   │   ├── All.yml
│   │   └── CN.yml
│   ├── All.yml
│   └── CN.yml
│
├── trials	#每个机场的订阅文件
│   ├── mrli.me
│   ├── mrli.me.yaml
│   └── mrli.me_pp.yaml
│
├── .gitignore #Git忽略文件: 忽略了__*
├── apis.py	#自建API库
├── subconverter.py	#自建subconverter库
├── utils.py	#自建utils库
├── get_trial.py	#actions main()
├── get_trial_update_url.py
└── README.md	#文档结构
```
