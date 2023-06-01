# fork zsokami/sub
```
README.md
V10.7 (2023-04-25)
V10.7 第一次失败 100% 重试，0% 清缓存，连续失败次数越多，重试概率越低，清缓存概率越高
    subconverter.py - improve
    get_trial.py - fix
V10.6 (2023-04-22)
V10.6 本地订阅转换
    - get_trial.yml
V10.5 (2023-04-21)
V10.5 kgithub + ghraw   
V10.5 (2023-04-16)
V10.5 过简单的字符型图片验证码
V10.4 (2023-04-15)
V10.4 自动禁用不可匿名注册的/有人机验证的/无试用的
```
[https://github.com/zsokami/sub](https://github.com/zsokami/sub)

[https://github.com/BUGOAO/SUBTEST - 机场合集](https://github.com/BUGOAO/SUBTEST)

==========================================================================

**collectProxy修改的地方：**

1.get_trial.py注释掉了开始的部分代码和 修改剩余多少流量重新注册
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
修改剩余多少流量重新注册
```
should_turn()
	return  (1 << 32) #1<<32 是512MB    原大小(1 << 28)
	
cache_sub_info()
    if total < (1 << 32):
        raise SCError(f'流量少于{size2str((1 << 32))}')
```
2..gitignore
```
__*
!__*__.*
trials_providers/
trial_pp.yaml
Country.mmdb
subconverter.log
subconverter.tar.gz
subconverter/
```
~~3.subconverter.py~~
```
_get_sc_config_url()
#先用以前的方法，避免使用GITHUB_TOKEN
data = Session().get('https://api.github.com/repos/zsokami/ACL4SSR/git/refs/heads/main').json()
```
**注意:Ations，里面的代码'GITHUB_TOKEN'

==========================================================================

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
