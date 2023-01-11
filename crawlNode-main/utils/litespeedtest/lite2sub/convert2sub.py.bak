import re, yaml
import time, os

from sub_convert import sub_convert

input_source_file = './sub/literx'
output_nocheck_file = './sub/literxClash.yml'

#转clash用的provider
config_file = './config/provider/config.yml'
 

class NoAliasDumper(yaml.SafeDumper): # https://ttl255.com/yaml-anchors-and-aliases-and-how-to-disable-them/
    def ignore_aliases(self, data):
        return True

def eternity_convert(file, config, output, provider_file_enabled=True):
    
    file_eternity = open(file, 'r', encoding='utf-8')
    sub_content = file_eternity.read()
    file_eternity.close()
    all_provider = sub_convert.main(sub_content,'content','YAML',custom_set={'dup_rm_enabled': False,'format_name_enabled': False})
    # 创建并写入 provider 
    lines = re.split(r'\n+', all_provider)
     
    proxy_all = []
    cn_proxy = []
    jp_proxy = []
    sg_proxy = []
    us_proxy = []
    other_proxy = []

    for line in lines:
        if line != 'proxies:' and 'plugin' not in line:
            line = '  ' + line
            proxy_all.append(line)    

            if 'HK' in line or '香港' in line or 'CN' in line or '中国' in line or 'TW' in line or '台湾' in line:
                cn_proxy.append(line)
            elif 'JP' in line or '日本' in line:
                jp_proxy.append(line)
            elif 'SG' in line or '新加坡' in line:
                sg_proxy.append(line)
            elif 'US' in line or '美国' in line:
                us_proxy.append(line)
            else:
                other_proxy.append(line)
                
    allproxy_provider = 'proxies:\n' + '\n'.join(proxy_all)
    cn_provider = 'proxies:\n' + '\n'.join(cn_proxy)
    jp_provider = 'proxies:\n' + '\n'.join(jp_proxy)
    sg_provider = 'proxies:\n' + '\n'.join(sg_proxy)
    us_provider = 'proxies:\n' + '\n'.join(us_proxy)
    other_provider = 'proxies:\n' + '\n'.join(other_proxy)
    
    if provider_file_enabled:
        eternity_providers = {
            'all': allproxy_provider,
            'cn': cn_provider,
            'jp': jp_provider,
            'sg': sg_provider,
            'us': us_provider,
            'other': other_provider
        }


    # 创建完全配置的Eternity.yml
    config_f = open(config_file, 'r', encoding='utf-8')
    config_raw = config_f.read()
    config_f.close()
    
    config = yaml.safe_load(config_raw)

    all_provider_dic = {'proxies': []}
    cn_provider_dic = {'proxies': []}
    jp_provider_dic = {'proxies': []}
    sg_provider_dic = {'proxies': []}
    us_provider_dic = {'proxies': []}
    other_provider_dic = {'proxies': []}
    
    provider_dic = {
        'all': all_provider_dic,
        'cn': cn_provider_dic,
        'jp': jp_provider_dic,
        'sg': sg_provider_dic,
        'us': us_provider_dic,
        'other': other_provider_dic
    }
    for key in eternity_providers.keys(): # 将节点转换为字典形式
        provider_load = yaml.safe_load(eternity_providers[key])
        provider_dic[key].update(provider_load)

    # 创建节点名列表
    all_name = []   
    cn_name = [] 
    jp_name = [] 
    sg_name = []
    us_name = []
    other_name = []
    
    name_dict = {
        'all': all_name,
        'cn': cn_name,
        'jp': jp_name,
        'sg': sg_name,
        'us': us_name,
        'other': other_name
    }
    for key in provider_dic.keys():
        if not provider_dic[key]['proxies'] is None:
            for proxy in provider_dic[key]['proxies']:
                name_dict[key].append(proxy['name'])
        if provider_dic[key]['proxies'] is None:
            name_dict[key].append('DIRECT')
    # 策略分组添加节点名
    proxy_groups = config['proxy-groups']
    proxy_group_fill = []
    for rule in proxy_groups:
        if rule['proxies'] is None: # 不是空集加入待加入名称列表
            proxy_group_fill.append(rule['name'])
    for rule_name in proxy_group_fill:
        for rule in proxy_groups:
            if rule['name'] == rule_name:
                rule.update({'proxies': all_name})
                
                if '香港' in rule_name or  '中国' in rule_name or '台湾' in rule_name:
                    rule.update({'proxies': cn_name})
                elif '日本' in rule_name:
                    rule.update({'proxies': jp_name})
                elif '狮城' in rule_name or '新加坡' in rule_name:
                    rule.update({'proxies': sg_name})
                elif '美国' in rule_name:
                    rule.update({'proxies': us_name})
                elif '其他' in rule_name:
                    rule.update({'proxies': other_name})
    config.update(all_provider_dic)
    config.update({'proxy-groups': proxy_groups})

    config_yaml = yaml.dump(config, default_flow_style=False, sort_keys=False, allow_unicode=True, width=750, indent=2, Dumper=NoAliasDumper)
    
    Eternity_yml = open(output, 'w+', encoding='utf-8')
    Eternity_yml.write(config_yaml)
    Eternity_yml.close()

def backup(file):
    t = time.localtime()
    date = time.strftime('%y%m', t)
    date_day = time.strftime('%y%m%d', t)

    file_eternity = open(file, 'r', encoding='utf-8')
    sub_content = file_eternity.read()
    file_eternity.close()

    try:
        os.mkdir(f'{bakup_path}{date}')
    except FileExistsError:
        pass
    txt_dir = bakup_path + date + '/' + date_day + '.txt' # 生成$MM$DD.txt文件名
    file = open(txt_dir, 'w', encoding= 'utf-8')
    file.write(sub_convert.base64_decode(sub_content))
    file.close()

if __name__ == '__main__':
    #将节点直接转成yaml订阅
    print('write literxClash begin!')
    eternity_convert(input_source_file, config_file, output=output_nocheck_file)
    print('write literxClash Over!')
