# Workflow的具体实现

## CDN具体实现
首先常规步骤，然后用Linux系统的curl命令访问jsdelivr的更新CDN地址（脚本里有）
然后用cron命令定时,我定时每天从每小时的第5分钟开始每20分钟执行一次

在线crontab执行时间计算
```
https://tool.lu/crontab/
https://tooltt.com/crontab/
https://cron.qqe2.com/
https://www.matools.com/crontab
https://crontab.guru/
```
然后添加一个触发按钮`workflow_dispatch`用于调试

```
name: CDN
on: 
   schedule:
      - cron: "5/20 * * * *"
   workflow_dispatch:
jobs:
  my-job:
    name: jsdelivr
    runs-on: ubuntu-latest
    steps:
    - name: long
      run: curl https://purge.jsdelivr.net/gh/git-yusteven/openit@main/long
    - name: Clash.yaml
      run: curl https://purge.jsdelivr.net/gh/git-yusteven/openit@main/Clash.yaml
```

### 首先设定环境
1. 设定触发条件，特定几个文件（写在paths下方xxx处）或者某些文件，不要定时运行(后文给出原因),最好加上手动触发`workflow_dispatch:`放在xxx的下一行与push对齐以备调试所用

```
name: xxx
on: 
  push:
    paths:
      - 'xxx'
  workflow_dispatch:
```
2. ubuntu系统即可，代码给出的是持续最新版ubuntu
```
jobs:
  my-job:
    name: xxx
    runs-on: ubuntu-latest
```
3. 使用官方`actions/checkout@v3`命令检出代码(v1的改良版，v1用到了指针的概念，不易懂)
```
    - uses: actions/checkout@v3
```
4. 配置git，注意把邮箱和名字改成自己GitHub的邮箱和名字，引号内添加（此处默认GitHub action）
```
    # 配置 git
    - name: config git
      run: git config --global user.email "actions@github.com"
           git config --global user.name "GitHub Action"
```
### 其次修改仓库文件
**只需使用Linux上的命令修改文件即可，不用去考虑cd到仓库文件夹**

```
    - name: xxxx
      run: 具体的命令,也可以是脚本
```
### 最后上传文件
这里有两种方式，分为手动推送或者运行一个bash脚本，下面给出详细解释

#### 其一，手动推送
<br>①检查change了什么文件
<br>②将文件提交到缓存区
<br>③给要上传的文件一个备注(不是名字)
<br>④push上传

```
    - name: check for changes
      run: git status
    - name: stage changed files
      run: git add .
    - name: commit changed files
      run: git commit -m "By Github actions"
    - name: push code to main
      run: git push
````
#### 其二 运行一个bash脚本
理想情况是修改、提交、推送，但是或许存在一些情况，导致其实文件没有发生变化。如果这时执行`git commit`，会提示`nothing to commit, working tree clean`
<br>注意了，这是一个报错，意味着 action 执行失败，会出现一个红叉❌,注意避免分支运行此Action,会报错`error: src refspec main does not match any`
<br>这里提供了一个bash脚本，需要放在仓库中，建议命名为`update-repo.sh`

```
#!/bin/bash
status_log=$(git status -sb)
# 这里使用的是 main 分支，根据需求自行修改
if [ "$status_log" == "## main...origin/main" ];then
  echo "nothing to commit, working tree clean"
else
  git add .&&git commit -m "By GitHub Action"&&git push origin main
fi
```
然后action脚本里这样写
```
    - name: <!--上方的四件套或者下方命令运行bash脚本两者选其一,update-repo.sh为上述bash文件名-->run script
      run: chmod +x ./update-repo.sh&&./update-repo.sh
```
#### 具体实现

```
name: xxx
on: 
  push:
    paths:
      - 'xxx'
  workflow_dispatch:
jobs:
  my-job:
    name: xxx
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: config git
      run: git config --global user.email "actions@github.com"
           git config --global user.name "GitHub Action"
    - name: xxxx
      run: 具体的命令
    - name: <!--下方是四件套-->check for changes
      run: git status
    - name: stage changed files
      run: git add .
    - name: commit changed files
      run: git commit -m "By GitHub Action"
    - name: push code
      run: git push
    - name: <!--上方的四件套或者下方命令运行bash脚本两者选其一,update-repo.sh为上述bash文件名-->run script
      run: chmod +x ./update-repo.sh&&./update-repo.sh
```
官方actions/checkout说明文档https://github.com/actions/checkout

参考：https://juejin.cn/post/6875857705282568200

著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。
## 如何创建密钥
新建一个Token(workflows权限,其他权限自行斟酌)添加到仓库密钥区

在这里新建一个Token，指路链接：https://github.com/settings/tokens

在这里添加到仓库密钥区，指路链接：https://github.com/您的名字/您的仓库名/settings/secrets/actions/new


##### [返回到CDN](#cdn具体实现) /// [返回到Base64](#base64-encode-具体实现)


# 自用环境模块添加

## 设置name和运行时间,运行条件
```
name: TG Node

# 触发条件
on:
  workflow_dispatch:
#  workflow_run:
#    workflows: ["collect TG"]
#    types: [completed]
  #schedule:
   #- cron: '15 4,9 * * *'
  #  实际时间： 12:15，17:15
  # 表达式生成  https://crontab.guru/
```
## 基本系统配置
```

jobs:
  deploy:
# 基本系统配置
    runs-on: ubuntu-latest
    steps:
    - name: 迁出代码
      uses: actions/checkout@v3
    - name: 安装Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10' 
    - name: 加载缓存
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/run_in_Actions/requirements.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-
    - name: 设置时区
      run: sudo timedatectl set-timezone 'Asia/Shanghai'

```
## 安装依赖和工具
```
# 安装依赖和工具
    - name: 安装依赖
      run: |
        pip install -r ./utils/requirements.txt
    - name: 安装Country.mmdb - ip库
      run: |        
        wget -O Country.mmdb https://github.com/Dreamacro/maxmind-geoip/releases/latest/download/Country.mmdb
    - name: 安装订阅转换工具-subconverter
      run: |
        wget -O subconverter.tar.gz https://github.com/tindy2013/subconverter/releases/latest/download/subconverter_linux64.tar.gz
        tar -zxvf subconverter.tar.gz -C ./
        chmod +x ./subconverter/subconverter && nohup ./subconverter/subconverter >./subconverter.log 2>&1 &
    - name: 安装测速工具-clash
      run: |
        wget -O clash-linuxamd64.gz https://github.com/Dreamacro/clash/releases/download/v1.11.8/clash-linux-amd64-v1.11.8.gz
        gunzip clash-linuxamd64.gz
        chmod +x ./clash-linuxamd64 && ./clash-linuxamd64 & 
```
## 执行任务 
```
# 执行任务 
    - name: 执行任务 - 1.测速
      run:
       python ./utils/speedtest.py
       sudo chmod 777 clash-linuxamd64 && python ./utils/clashspeedtest/main.py
```	   
## 提交 - commit
```
# 提交           
    - name: 提交更改
      run: |                 
        git config --local user.email "actions@github.com"
        git config --local user.name "GitHub Actions"
        git pull origin main
        git add ./sub
        git commit -m "$(date '+%Y-%m-%d %H:%M:%S') TG node update "
    - name: 推送更改
      uses:  ad-m/github-push-action@master
      with:
        branch: main
```
## Pushes to another repo

**注意：push 到 public repo 需要在 repo -- Settings -- Actions -- General -- Workflow permissions 中选择 read and write permissions**
**repo -- settings 不是 user -- settings**
```
# 提交到其他repo
    - name: Pushes to another repo
      uses: rxsweet/copy_file_to_another_repo_action@main
      env:
        API_TOKEN_GITHUB: ${{ secrets.UPDATE_REPO }}
      with:
        source_file: 'sub/'
        destination_repo: 'rxsweet/proxies'
        user_email: 'sweetrx@pm.me'
        user_name: 'rxsweet'
        commit_message: 'update message'
```
