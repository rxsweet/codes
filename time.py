from datetime import datetime

if __name__ == '__main__':
    today = datetime.today().strftime(': %Y-%m-%d %H:%M:%S')
    file = open('time.txt', 'w', encoding= 'utf-8')
    file.write(today)
    file.close()

"""    
    name: time

# 触发条件
on:
  workflow_dispatch:
  # 定时触发
  #schedule:
    # 每三天获取一次
    #- cron: '26 2 */7 * *'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - name: 迁出代码
      uses: actions/checkout@v2
    - name: 安装Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.x'
    - name: 加载缓存
      uses: actions/cache@v2
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/run_in_Actions/requirements.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-
    - name: 设置时区
      run: sudo timedatectl set-timezone 'Asia/Shanghai'
    #- name: 安装依赖
      #run: |
        #pip install -r requirements.txt
    - name: 执行任务
      run: |
        python time.py
    - name: 提交更改
      run: |
         #git config core.ignorecase false
         git config --global user.name "GitHub Actions"
         git config --global user.email "actions@github.com"
         git add .
         git commit -m "$(date '+%Y-%m-%d %H:%M:%S') time update"
         git push
"""
