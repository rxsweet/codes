import os
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from random import choice, randint, random
from threading import Lock
from time import time
from urllib.parse import urlsplit, urlunsplit

from apis import (Forbidden, PanelSession, TempEmail, guess_panel,
                  panel_class_map)
from subconverter import SCError, gen_base64_and_clash_config, get, select
from utils import (clear_files, g0, keep, list_file_paths, list_folder_paths,
                   rand_id, read, read_cfg, remove, size2str, str2timestamp,
                   timestamp2str, to_zero, write, write_cfg)

errors = [
    '更新旧订阅失败',
    '更新订阅链接/续费续签失败',
    '获取订阅失败',
    '保存base64/clash订阅失败',
]

name_locks = defaultdict(Lock)
name_cnts = Counter()


def get_sub(session: PanelSession, opt: dict, cache: dict[str, list[str]]):
    url = cache['sub_url'][0]
    suffix = ' - ' + ' '.join(cache['name'])
    if 'speed_limit' in opt:
        suffix += ' ⚠️限速 ' + opt['speed_limit']
    try:
        info, *rest = get(url, suffix)
    except SCError as e:
        raise e
    except Exception:
        origin = urlsplit(session.origin)[:2]
        url = '|'.join(urlunsplit(origin + urlsplit(part)[2:]) for part in url.split('|'))
        info, *rest = get(url, suffix)
        cache['sub_url'][0] = url
    if not info and hasattr(session, 'get_sub_info'):
        session.login(cache['email'][0])
        info = session.get_sub_info()
    return info, *rest


def should_turn(session: PanelSession, opt: dict, cache: dict[str, list[str]]):
    if 'sub_url' not in cache:
        return 1,

    now = time()
    try:
        info, *rest = get_sub(session, opt, cache)
    except Exception as e:
        msg = str(e)
        if '邮箱不存在' in msg or '禁' in msg:
            del cache['sub_url']
            if (d := cache['email'][0].split('@')[1]) not in ('gmail.com', 'qq.com', g0(cache, 'email_domain')):
                cache['banned_domains'].append(d)
            return 2,
        raise e

    return int(
        not info
        or opt.get('turn') == 'always'
        or float(info['total']) - (float(info['upload']) + float(info['download'])) < (1 << 28) #1<<32 是512MB    原大小(1 << 28)
        or (opt.get('expire') != 'never' and info.get('expire') and str2timestamp(info.get('expire')) - now < ((now - str2timestamp(cache['time'][0])) / 7 if 'reg_limit' in opt else 2400))
    ), info, *rest


def _register(session: PanelSession, email, *args, **kwargs):
    try:
        return session.register(email, *args, **kwargs)
    except Forbidden as e:
        raise e
    except Exception as e:
        raise Exception(f'注册失败({email}): {e}')


def _get_email_and_email_code(kwargs, session: PanelSession, opt: dict, cache: dict[str, list[str]]):
    while True:
        tm = TempEmail(banned_domains=cache.get('banned_domains'))
        try:
            email = kwargs['email'] = tm.email
        except Exception as e:
            raise Exception(f'获取邮箱失败: {e}')
        try:
            session.send_email_code(email)
        except Forbidden as e:
            raise e
        except Exception as e:
            msg = str(e)
            if '禁' in msg or '黑' in msg:
                cache['banned_domains'].append(email.split('@')[1])
                continue
            raise Exception(f'发送邮箱验证码失败({email}): {e}')
        email_code = tm.get_email_code(g0(cache, 'name'))
        if not email_code:
            cache['banned_domains'].append(email.split('@')[1])
            raise Exception(f'获取邮箱验证码超时({email})')
        kwargs['email_code'] = email_code
        return email


def register(session: PanelSession, opt: dict, cache: dict[str, list[str]], log: list) -> bool:
    kwargs = keep(opt, 'name_eq_email', 'reg_fmt', 'aff')

    if 'invite_code' in cache:
        kwargs['invite_code'] = cache['invite_code'][0]
    elif 'invite_code' in opt:
        kwargs['invite_code'] = choice(opt['invite_code'].split())

    email = kwargs['email'] = f"{rand_id()}@{g0(cache, 'email_domain', default='gmail.com')}"
    while True:
        if not (msg := _register(session, **kwargs)):
            if g0(cache, 'auto_invite', 'T') == 'T' and hasattr(session, 'get_invite_info'):
                if 'buy' not in opt and 'invite_code' not in kwargs:
                    session.login()
                    try:
                        code, num, money = session.get_invite_info()
                    except Exception as e:
                        if g0(cache, 'auto_invite') == 'T':
                            log.append(f'{session.host}({email}): {e}')
                        if '邀请' in str(e):
                            cache['auto_invite'] = 'F'
                        return False
                    if 'auto_invite' not in cache:
                        if not money:
                            cache['auto_invite'] = 'F'
                            return False
                        balance = session.get_balance()
                        plan = session.get_plan(min_price=balance + 0.01, max_price=balance + money)
                        if not plan:
                            cache['auto_invite'] = 'F'
                            return False
                        cache['auto_invite'] = 'T'
                    cache['invite_code'] = [code, num]
                    kwargs['invite_code'] = code

                    session.reset()

                    while True:
                        if 'email_code' in kwargs:
                            email = _get_email_and_email_code(kwargs, session, opt, cache)
                        else:
                            email = kwargs['email'] = f"{rand_id()}@{email.split('@')[1]}"
                        msg = _register(session, **kwargs)
                        if not (msg and '后缀' in msg and ('禁' in msg or '黑' in msg)):
                            break
                        cache['banned_domains'].append(email.split('@')[1])
                    if msg:
                        break

                if 'invite_code' in kwargs:
                    if 'invite_code' not in cache or int(cache['invite_code'][1]) == 1 or randint(0, 1):
                        session.login()
                        try_buy(session, opt, cache, log)
                        try:
                            cache['invite_code'] = [*session.get_invite_info()[:2]]
                        except Exception as e:
                            if 'invite_code' not in cache:
                                cache['auto_invite'] = 'F'
                            else:
                                log.append(f'{session.host}({email}): {e}')
                        return True
                    else:
                        n = int(cache['invite_code'][1])
                        if n > 0:
                            cache['invite_code'][1] = n - 1
            return False
        if '后缀' in msg:
            if email.split('@')[1] == 'gmail.com':
                email = kwargs['email'] = f'{rand_id()}@qq.com'
            elif '禁' in msg or '黑' in msg:
                cache['banned_domains'].append(email.split('@')[1])
                email = _get_email_and_email_code(kwargs, session, opt, cache)
            else:
                break
        elif '验证码' in msg:
            email = _get_email_and_email_code(kwargs, session, opt, cache)
        elif '联' in msg:
            kwargs['im_type'] = True
        elif (
            '邀请人' in msg
            and g0(cache, 'invite_code', '') == kwargs.get('invite_code')
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
            except Exception as e:
                log.append(f'尝试签到失败({session.host}): {e}')
    else:
        cache.pop('last_checkin', None)


def try_buy(session: PanelSession, opt: dict, cache: dict[str, list[str]], log: list):
    if not hasattr(session, 'buy'):
        return False
    try:
        if (plan := opt.get('buy')):
            return session.buy(plan)
        if (plan := g0(cache, 'buy')):
            if plan == 'pass':
                return False
            try:
                return session.buy(plan)
            except Exception as e:
                del cache['buy']
                cache.pop('auto_invite', None)
                cache.pop('invite_code', None)
                log.append(f'上次购买成功但这次购买失败({session.host}): {e}')
        plan = session.buy()
        cache['buy'] = plan or 'pass'
        return plan
    except Exception as e:
        log.append(f'购买失败({session.host}): {e}')
    return False


def cache_sub_url(session: PanelSession, cache: dict[str, list[str]]):
    sub_url = None
    if hasattr(session, 'get_sub_urls'):
        sub_urls = session.get_sub_urls()
        if len(sub_urls) == 1:
            sub_url = sub_urls[0]
        elif (old := g0(cache, 'sub_url')):
            sub_url_map = {session.get_sub_url_type_key(u): u for u in sub_urls}
            _sub_urls = old.split('|')
            for i, u in enumerate(_sub_urls):
                if (u := sub_url_map.get(session.get_sub_url_type_key(u))):
                    _sub_urls[i] = u
                else:
                    break
            else:
                sub_url = '|'.join(_sub_urls)
        if not sub_url:
            sub_url = select(sub_urls, session.is_clash_sub_url)
    else:
        sub_url = session.get_sub_url()
    cache['sub_url'] = [sub_url]


def do_turn(session: PanelSession, opt: dict, cache: dict[str, list[str]], log: list, force_reg=False) -> bool:
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
        reg_limit = int(reg_limit)
        if len(cache['email']) < reg_limit or force_reg:
            login_and_buy_ok = register(session, opt, cache, log)
            is_new_reg = True
            cache['email'].append(session.email)
            if is_checkin(session, opt):
                cache['last_checkin'] += ['0'] * (len(cache['email']) - len(cache['last_checkin']))
        if len(cache['email']) > reg_limit:
            del cache['email'][:-reg_limit]
            if is_checkin(session, opt):
                del cache['last_checkin'][:-reg_limit]

        cache['email'] = cache['email'][-1:] + cache['email'][:-1]
        if is_checkin(session, opt):
            cache['last_checkin'] = cache['last_checkin'][-1:] + cache['last_checkin'][:-1]

    if not login_and_buy_ok:
        try:
            session.login(cache['email'][0])
        except Exception as e:
            raise Exception(f'登录失败: {e}')
        try_buy(session, opt, cache, log)

    try_checkin(session, opt, cache, log)
    cache_sub_url(session, cache)
    cache['time'] = [timestamp2str(time())]
    log.append(f'{"更新订阅链接(新注册)" if is_new_reg else "续费续签"}({session.host}) {cache["sub_url"][0]}')
    return is_new_reg


def try_turn(session: PanelSession, opt: dict, cache: dict[str, list[str]], log: list):
    try:
        turn, *sub = should_turn(session, opt, cache)
    except (Forbidden, SCError):
        turn = 1
    except Exception as e:
        cache['更新旧订阅失败'] = [e]
        log.append(f'更新旧订阅失败({session.host})({cache["sub_url"][0]}): {e}')
        return None

    while turn:
        try:
            is_new_reg = do_turn(session, opt, cache, log, force_reg=turn == 2)
        except (Forbidden, SCError) as e:
            raise e
        except Exception as e:
            cache['更新订阅链接/续费续签失败'] = [e]
            log.append(f'更新订阅链接/续费续签失败({session.host}): {e}')
            return sub
        try:
            sub = get_sub(session, opt, cache)
        except SCError as e:
            if not is_new_reg:
                turn = 2
                continue
            raise e
        except Exception as e:
            cache['获取订阅失败'] = [e]
            log.append(f'获取订阅失败({session.host})({cache["sub_url"][0]}): {e}')
        break

    return sub


def cache_sub_info(info, opt: dict, cache: dict[str, list[str]]):
    if not info:
        raise Exception('no sub info')
    used = float(info["upload"]) + float(info["download"])
    total = float(info["total"])
    rest = '(剩余 ' + size2str(total - used)
    if opt.get('expire') == 'never' or not info.get('expire'):
        expire = '永不过期'
        #将'永不过期'改成了'2099-01-01'='4070883661',为了收集节点时能采集到
        #ts = 4070883661
        #expire = timestamp2str(ts)
        #rest += ' ' + str(timedelta(seconds=ts - time()))
    else:
        ts = str2timestamp(info['expire'])
        expire = timestamp2str(ts)
        rest += ' ' + str(timedelta(seconds=ts - time()))
    rest += ')'
    cache['sub_info'] = [size2str(used), size2str(total), expire, rest]
    if total == 0:
        raise SCError('0流量')
    #先关掉小于4G的流量pass掉
    #if total < (1 << 32):
        #raise SCError(f'流量少于{size2str((1 << 32))}')


def save_sub_base64_and_clash(base64, clash, host, opt: dict):
    return gen_base64_and_clash_config(
        base64_path=f'trials/{host}',
        clash_path=f'trials/{host}.yaml',
        clash_pp_path=f'trials/{host}_pp.yaml',
        providers_dir=f'trials_providers/{host}',
        base64=base64,
        clash=clash,
        exclude=opt.get('exclude')
    )


def save_sub(info, base64, clash, base64_url, clash_url, host, opt: dict, cache: dict[str, list[str]], log: list):
    try:
        cache_sub_info(info, opt, cache)
    except SCError as e:
        raise e
    except Exception as e:
        log.append(f'保存订阅信息失败({host})({clash_url}): {e}')
    try:
        node_n = save_sub_base64_and_clash(base64, clash, host, opt)
        if (d := node_n - int(g0(cache, 'node_n', 0))) != 0:
            log.append(f'{host} 节点数 {"+" if d > 0 else ""}{d} ({node_n})')
        cache['node_n'] = node_n
    except SCError as e:
        raise e
    except Exception as e:
        cache['保存base64/clash订阅失败'] = [e]
        log.append(f'保存base64/clash订阅失败({host})({base64_url})({clash_url}): {e}')


def get_and_save(session: PanelSession, host, opt: dict, cache: dict[str, list[str]], log: list):
    try_checkin(session, opt, cache, log)
    sub = try_turn(session, opt, cache, log)
    if sub:
        save_sub(*sub, host, opt, cache, log)


def new_panel_session(host, cache: dict[str, list[str]]) -> PanelSession:
    if 'type' not in cache:
        info = guess_panel(host)
        if 'type' not in info:
            if (e := info.get('error')):
                if isinstance(e, Forbidden):
                    raise e
                raise Exception(f"判别类型失败: {e}")
            raise Exception('未知类型')

        # 名称重复时添加递增数字
        name = info.pop('name')
        try:
            with name_locks[name]:
                name_cnts[name] += 1
                cnt = name_cnts[name]
        finally:
            name_locks.pop(name, None)
        if cnt == 1:
            cache['name'] = [name]
        else:
            cache['name'] = [name, str(cnt)]

        cache.update(info)
    return panel_class_map[g0(cache, 'type')](g0(cache, 'api_host', host), **keep(cache, 'auth_path', getitem=g0))


def get_trial(host, opt: dict, cache: dict[str, list[str]]):
    log = []
    try:
        session = new_panel_session(host, cache)

        get_and_save(session, host, opt, cache, log)

        if session.redirect_origin:
            cache['api_host'] = session.host

        if not any(k in cache for k in errors):
            cache.pop('fail_n', None)
            return log
    except Exception as e:
        log.append(f"{host} {e}")
        cache['disabled'] = e
        remove_trial(host)
    cache['fail_n'] = int(g0(cache, 'fail_n', 0)) + 1
    return log


def remove_trial(host):
    remove(f'trials/{host}')
    remove(f'trials/{host}.yaml')
    remove(f'trials/{host}_pp.yaml')
    clear_files(f'trials_providers/{host}')
    remove(f'trials_providers/{host}')


def remove_trials_not_in(hosts):
    for path in list_file_paths('trials'):
        host, ext = os.path.splitext(os.path.basename(path))
        if ext != '.yaml':
            host += ext
        else:
            host = host.split('_')[0]
        if host not in hosts:
            remove(path)

    for path in list_folder_paths('trials_providers'):
        host = os.path.basename(path)
        if '.' in host and host not in hosts:
            clear_files(path)
            remove(path)


def build_options(cfg):
    opt = {
        host: dict(zip(opt[::2], opt[1::2]))
        for host, *opt in cfg
    }
    return opt


def f_retry(x): return 1 / 50 + 49 / (50 * x)
def f_enable(x): return 1 / 50 + 49 / (50 * x ** 2)
def f_clear(x): return 1 - 2 ** -((x - 1) / 16) ** 6


if __name__ == '__main__':
    # 新仓库第一次运行自动删除 trial.cache
    pre_repo = read('.github/repo_get_trial')
    cur_repo = os.getenv('GITHUB_REPOSITORY')
    if pre_repo != cur_repo:
        remove('trial.cache')
        write('.github/repo_get_trial', cur_repo)

    opt = build_options(read_cfg('trial.cfg')['default'])

    remove_trials_not_in(opt)

    cache = read_cfg('trial.cache', dict_items=True)

    for host in [*cache]:
        if host in opt:
            _cache = cache[host]
            # 第一次失败 100% 重试，0% 清缓存，连续失败次数越多，重试概率越低，清缓存概率越高
            if 'disabled' in _cache:
                x = _cache['fail_n'] = int(g0(_cache, 'fail_n', 1))
                if random() < f_enable(x):
                    if random() < f_clear(x):
                        _cache.clear()
                        _cache['fail_n'] = x
                    else:
                        del _cache['disabled']
                else:
                    del opt[host]
            elif any(k in _cache for k in errors):
                x = _cache['fail_n'] = int(g0(_cache, 'fail_n', 1))
                if random() < f_retry(x):
                    if random() < f_clear(x):
                        _cache.clear()
                        _cache['fail_n'] = x
                    else:
                        for k in errors:
                            _cache.pop(k, None)
                else:
                    del opt[host]
        else:
            del cache[host]

    # 名称重复时添加递增数字
    for _cache in cache.values():
        if 'type' in _cache:
            name = _cache['name']
            name_cnts[name[0]] += 1
            if name_cnts[name[0]] == 1:
                del name[1:]
            else:
                name[1:] = [str(name_cnts[name[0]])]

    with ThreadPoolExecutor(32) as executor:
        args = [(h, v, cache[h]) for h, v in opt.items()]
        for log in executor.map(get_trial, *zip(*args)):
            for line in log:
                print(line)

    total_node_n = gen_base64_and_clash_config(
        base64_path='trial',
        clash_path='trial.yaml',
        clash_pp_path='trial_pp.yaml',
        providers_dir='trials_providers',
        base64_paths=(path for path in list_file_paths('trials') if os.path.splitext(path)[1].lower() != '.yaml'),
        providers_dirs=(path for path in list_folder_paths('trials_providers') if '.' in os.path.basename(path))
    )

    print('总节点数', total_node_n)

    write_cfg('trial.cache', cache)
