# fork zsokami/sub
[https://github.com/zsokami/sub](https://github.com/zsokami/sub)

个人使用修改的地方:
1.subconverter.py
```
_get_sc_config_url()
#先用以前的方法，避免使用GITHUB_TOKEN
data = Session().get('https://api.github.com/repos/zsokami/ACL4SSR/git/refs/heads/main').json()

_gen_clash_config()

 #先注释掉，不写_pp
    #prefix, ext = os.path.splitext(clash_path)
    #write(f'{prefix}_pp{ext}', lambda f: y.dump(cfg, f))
```


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
