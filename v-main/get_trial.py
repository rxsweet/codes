import os
from concurrent.futures import ThreadPoolExecutor   #python线程池ThreadPoolExecutor用法及实战 https://zhuanlan.zhihu.com/p/65638744
from datetime import timedelta  #timedelta类主要用于做时间加减的 详解https://blog.csdn.net/weixin_41261833/article/details/103909724
from itertools import chain #在不同的列表中进行循环？ 用法详解 https://www2.jianshu.com/p/8da58593aa55
from random import choice, randint  #choice随机抽样，randint随机范围整数 https://zhuanlan.zhihu.com/p/98298060
from time import time   #time.time() 功能：获取当前本地的时间戳      time模块 https://blog.csdn.net/jamfiy/article/details/88195846

from apis import (HkspeedupSession, Session, SSPanelSession, TempEmail, V2BoardSession) #自建API库 apis.py
from subconverter import gen_base64_and_clash_config, get                               #自建subconverter库 subconverter.py
from utils import (clear_files, get_id, list_file_paths, list_folder_paths,
                   read, read_cfg, remove, size2str, str2timestamp,
                   timestamp2str, to_zero, write, write_cfg)                            #自建utils库 utils.py

PanelSession = V2BoardSession | SSPanelSession | HkspeedupSession

panel_class_map = {
    'v2board': V2BoardSession,
    'sspanel': SSPanelSession,
    'hkspeedup': HkspeedupSession,
}

temp_email = TempEmail()


# 注册/登录/解析/下载


def get_sub(session: PanelSession, opt: dict, cache: dict[str, list[str]]):
    url = cache['sub_url'][0]
    suffix = ' - ' + opt['name']
    if 'speed_limit' in opt:
        suffix += ' ⚠️限速 ' + opt['speed_limit']
    info, *rest = get(url, suffix)
    if not info and hasattr(session, 'get_sub_info'):
        session.login(cache['email'][0])
        info = session.get_sub_info()
    return info, *rest


def should_turn(session: PanelSession, opt: dict, cache: dict[str, list[str]]):
    if 'sub_url' not in cache:
        return True,

    now = time()
    info, *rest = get_sub(session, opt, cache)

    return (
        not info
        or opt.get('turn') == 'always'
        or float(info['total']) - (float(info['upload']) + float(info['download'])) < (1 << 28)
        or (opt.get('expire') != 'never' and info.get('expire') and str2timestamp(info.get('expire')) - now < ((now - str2timestamp(cache['time'][0])) / 7 if 'reg_limit' in opt else 2400))
    ), info, *rest


def _register(session: PanelSession, email, *args, **kwargs):
    try:
        return session.register(email, *args, **kwargs)
    except Exception as e:
        raise Exception(f'注册失败({email}): {e}')


def register(session: PanelSession, opt: dict, cache: dict[str, list[str]], log: list) -> bool:
    kwargs = {k: opt[k] for k in opt.keys() & ('name_eq_email', 'reg_fmt', 'aff')}

    if opt.get('auto_invite') == 'T':
        if 'invite_code' in cache:
            kwargs['invite_code'] = cache['invite_code'][0]
    else:
        cache.pop('invite_code', None)

    if 'invite_code' not in kwargs and 'invite_code' in opt:
        kwargs['invite_code'] = choice(opt['invite_code'].split())

    email = kwargs['email'] = f'{get_id()}@gmail.com'
    while True:
        if not (msg := _register(session, **kwargs)):
            if opt.get('auto_invite') == 'T':
                if 'invite_code' not in kwargs:
                    session.login()
                    cache['invite_code'] = [*session.get_invite_info()]
                    kwargs['invite_code'] = cache['invite_code'][0]

                    session.reset()

                    id, domain = email.split('@')
                    r = str(randint(0, 8))
                    if r == id[-1]:
                        r = '9'
                    id = id[:-1] + r
                    email = kwargs['email'] = f'{id}@{domain}'

                    if 'email_code' in kwargs:
                        try:
                            _temp_email = temp_email.replace(id)
                            _email = _temp_email.get_email()
                            if _email != email:
                                raise Exception(f'email = {repr(email)}, _temp_email.get_email() = {repr(_email)}')
                            session.send_email_code(email)
                        except Exception as e:
                            raise Exception(f'第二次发送邮箱验证码失败({email}): {e}')
                        email_code = _temp_email.get_email_code(opt['name'])
                        if not email_code:
                            raise Exception(f'第二次获取邮箱验证码超时({email})')
                        kwargs['email_code'] = email_code

                    if (msg := _register(session, **kwargs)):
                        break
                if 'invite_code' not in cache or int(cache['invite_code'][1]) == 1 or randint(0, 1):
                    session.login()
                    try_buy(session, opt, log)
                    cache['invite_code'] = [*session.get_invite_info()]
                    return True
                else:
                    n = int(cache['invite_code'][1])
                    if n > 0:
                        cache['invite_code'][1] = n - 1
            return False
        if '后缀' in msg:
            id, domain = email.split('@')
            if domain != 'gmail.com':
                break
            email = kwargs['email'] = f'{id}@qq.com'
        elif '验证码' in msg:
            try:
                email = kwargs['email'] = temp_email.get_email(email.split('@')[0])
                session.send_email_code(email)
            except Exception as e:
                raise Exception(f'发送邮箱验证码失败({email}): {e}')
            email_code = temp_email.get_email_code(opt['name'])
            if not email_code:
                raise Exception(f'获取邮箱验证码超时({email})')
            kwargs['email_code'] = email_code
        elif '联' in msg:
            kwargs['im_type'] = True
        elif (
            '邀请人' in msg
            and opt.get('auto_invite') == 'T'
            and 'invite_code' in cache
            and cache['invite_code'][0] == kwargs.get('invite_code')
        ):
            del cache['invite_code']
            if 'invite_code' in opt:
                kwargs['invite_code'] = choice(opt['invite_code'].split())
            else:
                del kwargs['invite_code']
        else:
            break
    raise Exception(f'注册失败({email}): {msg}{" " + kwargs.get("invite_code") if "邀" in msg else ""}')


def is_checkin(session, opt: dict):
    return hasattr(session, 'checkin') and opt.get('checkin') != 'F'


def try_checkin(session: PanelSession, opt: dict, cache: dict[str, list[str]], log: list):
    if is_checkin(session, opt) and cache.get('email'):
        if len(cache['last_checkin']) < len(cache['email']):
            cache['last_checkin'] += ['0'] * (len(cache['email']) - len(cache['last_checkin']))
        last_checkin = to_zero(str2timestamp(cache['last_checkin'][0]))
        now = time()
        if now - last_checkin > 24.5 * 3600:
            try:
                session.login(cache['email'][0])
                session.checkin()
                cache['last_checkin'][0] = timestamp2str(now)
                cache.pop('尝试签到失败', None)
            except Exception as e:
                cache['尝试签到失败'] = [e]
                log.append(f'尝试签到失败({session.host}): {e}')
    else:
        cache.pop('last_checkin', None)


def try_buy(session: PanelSession, opt: dict, log: list):
    if 'buy' in opt:
        try:
            session.buy(opt['buy'])
        except Exception as e:
            log.append(f'购买失败({session.host}): {e}')


def do_turn(session: PanelSession, opt: dict, cache: dict[str, list[str]], log: list) -> bool:
    is_new_reg = False
    login_and_buy_ok = False
    reg_limit = opt.get('reg_limit')
    if not reg_limit:
        login_and_buy_ok = register(session, opt, cache, log)
        is_new_reg = True
        cache['email'] = [session.email]
        if is_checkin(session, opt):
            cache['last_checkin'] = ['0']
    else:
        if len(cache['email']) < int(reg_limit):
            login_and_buy_ok = register(session, opt, cache, log)
            is_new_reg = True
            cache['email'].append(session.email)
            if is_checkin(session, opt):
                cache['last_checkin'] += ['0'] * (len(cache['email']) - len(cache['last_checkin']))
        elif len(cache['email']) > int(reg_limit):
            del cache['email'][:-int(reg_limit)]
            if is_checkin(session, opt):
                del cache['last_checkin'][:-int(reg_limit)]

        cache['email'] = cache['email'][-1:] + cache['email'][:-1]
        if is_checkin(session, opt):
            cache['last_checkin'] = cache['last_checkin'][-1:] + cache['last_checkin'][:-1]

    if not login_and_buy_ok:
        try:
            session.login(cache['email'][0])
        except Exception as e:
            raise Exception(f'登录失败: {e}')
        try_buy(session, opt, log)

    try_checkin(session, opt, cache, log)
    cache['sub_url'] = [session.get_sub_url(**opt)]
    cache['time'] = [timestamp2str(time())]
    log.append(f'{"更新订阅链接(新注册)" if is_new_reg else "续费续签"}({session.host}) {cache["sub_url"][0]}')


def try_turn(session: PanelSession, opt: dict, cache: dict[str, list[str]], log: list):
    cache.pop('更新旧订阅失败', None)
    cache.pop('更新订阅链接/续费续签失败', None)
    cache.pop('获取订阅失败', None)

    try:
        turn, *sub = should_turn(session, opt, cache)
    except Exception as e:
        cache['更新旧订阅失败'] = [e]
        log.append(f'更新旧订阅失败({session.host})({cache["sub_url"][0]}): {e}')
        return None

    if turn:
        try:
            do_turn(session, opt, cache, log)
        except Exception as e:
            cache['更新订阅链接/续费续签失败'] = [e]
            log.append(f'更新订阅链接/续费续签失败({session.host}): {e}')
            return sub
        try:
            sub = get_sub(session, opt, cache)
        except Exception as e:
            cache['获取订阅失败'] = [e]
            log.append(f'获取订阅失败({session.host})({cache["sub_url"][0]}): {e}')

    return sub


def cache_sub_info(info, opt: dict, cache: dict[str, list[str]]):
    if not info:
        raise Exception('no sub info')
    used = float(info["upload"]) + float(info["download"])
    total = float(info["total"])
    rest = '(剩余 ' + size2str(total - used)
    if opt.get('expire') == 'never' or not info.get('expire'):
        expire = '永不过期'
    else:
        ts = str2timestamp(info['expire'])
        expire = timestamp2str(ts)
        rest += ' ' + str(timedelta(seconds=ts - time()))
    rest += ')'
    cache['sub_info'] = [size2str(used), size2str(total), expire, rest]


def save_sub_base64_and_clash(base64, clash, host, opt: dict):
    return gen_base64_and_clash_config(
        base64_path=f'trials/{host}',
        clash_path=f'trials/{host}.yaml',
        providers_dir=f'trials_providers/{host}',
        base64=base64,
        clash=clash,
        exclude=opt.get('exclude')
    )


def save_sub(info, base64, clash, base64_url, clash_url, host, opt: dict, cache: dict[str, list[str]], log: list):
    cache.pop('保存订阅信息失败', None)
    cache.pop('保存base64/clash订阅失败', None)

    try:
        cache_sub_info(info, opt, cache)
    except Exception as e:
        cache['保存订阅信息失败'] = [e]
        log.append(f'保存订阅信息失败({host})({clash_url}): {e}')
    try:
        node_n = save_sub_base64_and_clash(base64, clash, host, opt)
        if (d := node_n - (int(cache['node_n'][0]) if 'node_n' in cache else 0)) != 0:
            log.append(f'{host} 节点数 {"+" if d > 0 else ""}{d} ({node_n})')
        cache['node_n'] = node_n
    except Exception as e:
        cache['保存base64/clash订阅失败'] = [e]
        log.append(f'保存base64/clash订阅失败({host})({base64_url})({clash_url}): {e}')


def get_and_save(session: PanelSession, host, opt: dict, cache: dict[str, list[str]], log: list):
    try_checkin(session, opt, cache, log)
    sub = try_turn(session, opt, cache, log)
    if sub:
        save_sub(*sub, host, opt, cache, log)


def get_trial(Class, host, opt: dict, cache: dict[str, list[str]]):
    log = []
    session = Class(host, **{k: opt[k] for k in opt.keys() & ('auth_path',)})
    get_and_save(session, host, opt, cache, log)
    return log


def get_ip_info():
    try:
        return ['  '.join(Session().get_ip_info())]
    except Exception as e:
        return [f'获取 ip 信息失败 {e}']


def build_options(cfg):
    opt = {
        host: dict(zip(opt[::2], opt[1::2]))    #功能模块下面有注释
        for host, *opt in chain(*(cfg[k] for k in panel_class_map))
    }
    for host, _opt in opt.items():  #for key,values in dict.items():  https://www.runoob.com/python/python-date-time.html
        _opt.setdefault('name', host)   #dict.setdefault(key, default=None) https://www.runoob.com/python/python-date-time.html
    return opt
#dict() 函数用于创建一个字典，
#zip() 函数用于将可迭代的对象作为参数, 
#[::2]，[1::2]冒号分隔切片参数 start:stop:step，（host：url功能中[::2]，相当于取host，[1::2]相当于取url）
"""
>>>dict()                        # 创建空字典
{}
>>> dict(a='a', b='b', t='t')     # 传入关键字
{'a': 'a', 'b': 'b', 't': 't'}
>>> dict(zip(['one', 'two', 'three'], [1, 2, 3]))   # 映射函数方式来构造字典
{'three': 3, 'two': 2, 'one': 1} 
>>> dict([('one', 1), ('two', 2), ('three', 3)])    # 可迭代对象方式来构造字典
{'three': 3, 'two': 2, 'one': 1}
"""

#主入口main()
if __name__ == '__main__':
    #查看repo目录是否存在，不存在: 1.删除trial.cache,2.将现在的目录写入目录文件
    pre_repo = read('.github/repo_get_trial')
    cur_repo = os.getenv('GITHUB_REPOSITORY')
    if pre_repo != cur_repo:
        remove('trial.cache')
        write('.github/repo_get_trial', cur_repo)
    
    #读取cfg文件：机场网站
    cfg = read_cfg('trial.cfg')
    #将cfg内容读取成字典格式
    opt = build_options(cfg)
    
    cache = read_cfg('trial.cache', dict_items=True)

    for host in [*cache]:
        if host not in opt:
            del cache[host]

    for path in list_file_paths('trials'):
        host, ext = os.path.splitext(os.path.basename(path))
        if ext != '.yaml':
            host += ext
        else:
            host = host.split('_')[0]
        if host not in opt:
            remove(path)

    for path in list_folder_paths('trials_providers'):
        host = os.path.basename(path)
        if '.' in host and host not in opt:
            clear_files(path)
            remove(path)

    with ThreadPoolExecutor(32) as executor:
        f_ip_info = executor.submit(get_ip_info)

        args = [(v, h, opt[h], cache[h]) for k, v in panel_class_map.items() for h, *_ in cfg[k]]

        logs = executor.map(get_trial, *zip(*args))

        for log in chain((f.result() for f in [f_ip_info]), logs):
            for line in log:
                print(line)

    total_node_n = gen_base64_and_clash_config(
        base64_path='./sub/v.txt',
        clash_path='./sub/v.yaml',
        providers_dir='trials_providers',
        base64_paths=(path for path in list_file_paths('trials') if os.path.splitext(path)[1].lower() != '.yaml'),
        providers_dirs=(path for path in list_folder_paths('trials_providers') if '.' in os.path.basename(path))
    )

    print('总节点数', total_node_n)

    write_cfg('trial.cache', cache)
