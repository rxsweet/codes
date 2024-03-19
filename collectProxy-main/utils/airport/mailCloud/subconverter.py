import os
import re
from base64 import b64decode, b64encode, urlsafe_b64encode
from collections import defaultdict
from copy import deepcopy
from random import randint
from time import time
from typing import Callable, Iterable
from urllib.parse import quote, urljoin

from ruamel.yaml import YAML

from apis import Response, Session
from get_trial_update_url import get_pp_url
from utils import (DOMAIN_SUFFIX_Tree, IP_CIDR_SegmentTree, cached,
                   clear_files, get_name, list_file_paths, re_non_empty_base64,
                   read, read_cfg, write)

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')


class SCError(Exception):
    pass


@cached
def subconverters():
    try:
        if Session('http://localhost:25500', retry=0).get('version').ok:
            return ['http://localhost:25500'] * 3
    except Exception:
        pass
    print('本地订阅转换不可用，使用远程订阅转换')
    return [row[0] for row in read_cfg('subconverters.cfg')['default']]


def _yaml():
    yaml = YAML()
    yaml.version = (1, 1)
    yaml.width = float('inf')
    return yaml


def _get_by_any(session: Session, url: str | Iterable[str], retry_400=99) -> Response | list[Response]:
    r = None

    if isinstance(url, str):
        def get():
            nonlocal retry_400, r
            try:
                r = session.get(url)
                if r.ok:
                    return True
                if 400 <= r.status_code < 500:
                    if retry_400 <= 0:
                        return True
                    retry_400 -= 1
            except Exception:
                pass
            return False
    else:
        def get():
            nonlocal retry_400, r
            try:
                r = [session.get(url) for url in url]
                if any(r.ok for r in r):
                    for i, u in enumerate(url):
                        for _ in range(5):
                            if r[i].ok:
                                break
                            r[i] = session.get(u)
                    return True
                if all(400 <= r.status_code < 500 for r in r):
                    if retry_400 <= 0:
                        return True
                    retry_400 -= 1
            except Exception:
                pass
            return False

    session.allow_redirects = 0
    o_base = session.base
    if o_base:
        if get():
            return r
    idx_map = {}
    for i in range(len(subconverters()) - 1, -1, -1):
        j = randint(0, i)
        base = subconverters()[idx_map.get(j, j)]
        idx_map[j] = idx_map.get(i, i)
        if base != o_base:
            session.set_base(base)
            if get():
                return r
    if not r:
        raise Exception('_get_by_any: not r')
    return r


@cached
def _sc_config_url():
    try:
        data = Session().get(
            'https://api.github.com/repos/zsokami/ACL4SSR/git/refs/heads/main',
            headers={'Authorization': f"Bearer {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
        ).json()
        try:
            sha = data['object']['sha']
        except KeyError:
            raise Exception(data)
        return f'https://raw.githubusercontent.com/zsokami/ACL4SSR/{sha}/ACL4SSR_Online_Full_Mannix.ini'
    except Exception as e:
        print(f'_sc_config_url: 获取 sha 失败，使用 main: {e}')
        return 'https://raw.githubusercontent.com/zsokami/ACL4SSR/main/ACL4SSR_Online_Full_Mannix.ini'


@cached
def _base_clash_config():
    session = Session(user_agent='ClashforWindows')
    url = f"sub?target=clash&config={_sc_config_url()}&url=ss://YWVzLTEyOC1nY206YWJj@c.c:1%231"
    try:
        res = _get_by_any(session, url)
        y = _yaml()
        cfg = y.load(res.content)
        base_yaml = read('base.yaml', reader=y.load)
        group_to_provider_map = {g['name']: g['use'][0] for g in base_yaml['proxy-groups']}
        groups = base_yaml['proxy-groups'] = cfg['proxy-groups']
        for g in groups:
            if (p := group_to_provider_map.get(g['name'])):
                del g['proxies']
                g['use'] = [p]
                base_yaml['proxy-providers'].setdefault(p, None)
        rules = _remove_redundant_rules(cfg['rules'])
        return base_yaml, group_to_provider_map, rules
    except Exception as e:
        raise Exception(f'_cache_base_clash_config: 获取基本 clash 配置失败: {e}')


def _base_yaml():
    return _base_clash_config()[0]


def _group_to_provider_map():
    return _base_clash_config()[1]


def _rules():
    return _base_clash_config()[2]


def _remove_redundant_rules(rules):
    keywords = []
    domain_tree = DOMAIN_SUFFIX_Tree()
    ip_trees = defaultdict(IP_CIDR_SegmentTree)
    sets = defaultdict(set)
    i = 0
    for rule in rules:
        t, v, *_ = rule.split(',')
        if t.startswith('DOMAIN'):
            if any(w in v for w in keywords):
                continue
            if t == 'DOMAIN-KEYWORD':
                keywords.append(v)
            elif not domain_tree.add(v, t == 'DOMAIN-SUFFIX'):
                continue
        elif 'IP-CIDR' in t:
            if not ip_trees[t].add(v):
                continue
        else:
            if v in sets[t]:
                continue
            sets[t].add(v)
        rules[i] = rule
        i += 1
    del rules[i:]
    return rules


def _get_info(r: Response):
    info = r.headers.get('subscription-userinfo')
    return dict(kv.split('=') for kv in info.split('; ')) if info else None


def get(url: str, suffix=None):
    session = Session(user_agent='ClashforWindows')
    _url = quote('|'.join(f'{part}#{time()}' for part in url.split('|')))
    params = f"config={_sc_config_url()}"
    if suffix:
        params += '&rename=' + quote(f'$@{suffix}')
    clash_url = f'sub?target=clash&udp=true&scv=true&expand=false&classic=true&{params}&url={_url}'
    base64_url = f'sub?target=mixed&{params}&url={_url}'

    res = _get_by_any(session, clash_url, retry_400=1)
    if not res.ok:
        _urls = url.split('|')
        _url = _urls[0]
        _res = session.get(_url)
        if not _res.ok:
            raise Exception(f'({_url}): {_res}')
        if not (re_non_empty_base64.fullmatch(_res.content) or b'proxies:' in _res.content):
            raise SCError(f'订阅链接无效/无试用/无节点/已过期 {_url} {_res}')
        if session.hostname == 'localhost' and len(_urls) == 1:
            _url = 'data:text/plain;base64,' + urlsafe_b64encode(_res.content).decode()
            clash_url = f'sub?target=clash&udp=true&scv=true&expand=false&classic=true&{params}&url={_url}'
            base64_url = f'sub?target=mixed&{params}&url={_url}'
            res = _get_by_any(session, clash_url)
            if res:
                res.headers.update(_res.headers)
        else:
            res = _get_by_any(session, clash_url)

    if not res.ok or b'proxies:' not in res.content:
        raise SCError(f'订阅转换失败(可能订阅链接无效/无试用/无节点/已过期) {url} {res}')

    clash = res.content
    clash_url = urljoin(session.base, clash_url)

    base64 = _get_by_any(session, base64_url).content
    base64_url = urljoin(session.base, base64_url)

    return _get_info(res), base64, clash, base64_url, clash_url


def _is_all_in(a, b):
    b_n_to_p = {p['name']: p for p in b}
    return all(p == b_n_to_p.get(p['name']) for p in a)


def select(urls: list[str], is_clash: Callable[[str], bool]) -> str:
    if len(urls) == 1:
        return urls[0]
    session = Session(user_agent='ClashforWindows')
    clash_url_prefix = f'sub?target=clash&list=true&udp=false&scv=false&config={_sc_config_url()}&url='
    urls_and_rs = [
        (u, r)
        for u, r in zip(
            urls,
            _get_by_any(session, [clash_url_prefix + quote(u) for u in urls])
        )
        if r.ok and r.content.startswith(b'proxies:')
    ]
    if not urls_and_rs:
        raise SCError(f'订阅转换失败(可能订阅链接无效/无试用/无节点/已过期) {urls}')
    if len(urls_and_rs) == 1:
        return urls_and_rs[0][0]
    y = _yaml()
    urls_and_proxies = [(u, y.load(r.content)['proxies']) for u, r in urls_and_rs]
    if (i := next((i for i, (u, _) in enumerate(urls_and_proxies) if is_clash(u)), -1)) != -1:
        u_clash, ps_clash = urls_and_proxies[i]
        urls_and_proxies[i] = urls_and_proxies[0]
        if (ups := [(u, ps) for u, ps in urls_and_proxies[1:] if not is_clash(u) and _is_all_in(ps_clash, ps)]):
            return max(ups, key=lambda ups: len(ups[1]))[0]
        return u_clash
    urls_and_proxies.sort(key=lambda ups: len(ups[1]), reverse=True)
    urls = [urls_and_proxies[0][0]]
    name_set = set(p['name'] for p in urls_and_proxies[0][1])
    for u, ps in urls_and_proxies[1:]:
        if all(p['name'] not in name_set for p in ps):
            urls.append(u)
            name_set.update(p['name'] for p in ps)
    return '|'.join(urls)


def _parse_node_groups(y: YAML, clash, exclude: re.Pattern = None):
    cfg = y.load(clash)
    g_to_p = _group_to_provider_map()
    name_to_node_map = {p['name']: p for p in cfg['proxies'] if not (exclude and exclude.search(p['name']))}
    provider_map = {}
    for g in cfg['proxy-groups']:
        name, proxies = g['name'], g['proxies']
        if (
            name in g_to_p
            and g_to_p[name] not in provider_map
            and proxies[0] != 'DIRECT'
        ):
            proxies = [p for p in proxies if not (exclude and exclude.search(p))]
            if proxies:
                provider_map[g_to_p[name]] = proxies
    return name_to_node_map, provider_map


def _read_and_merge_providers(y: YAML, providers_dirs, exclude: re.Pattern = None):
    name_to_node_map = {}
    provider_map = defaultdict(list)
    for providers_dir in providers_dirs:
        for path in list_file_paths(providers_dir):
            name = os.path.splitext(os.path.basename(path))[0]
            if not name.startswith('p_'):
                proxies = read(path, reader=y.load)['proxies']
                kvs = [(p['name'], p) for p in proxies if not (exclude and exclude.search(p['name']))]
                if kvs:
                    name_to_node_map |= kvs
                    provider_map[name] += (k for k, _ in kvs)
    return name_to_node_map, provider_map


def _split_providers(provider_map: dict[str, list[str]]):
    to_order = defaultdict(lambda: 99, ((k, i) for i, k in enumerate(_base_yaml()['proxy-providers'])))

    node_to_providers = defaultdict(list)
    for k, v in sorted(provider_map.items(), key=lambda kv: to_order[kv[0]]):
        for node in v:
            node_to_providers[node].append(k)

    providers_to_nodes = defaultdict(list)
    for k, v in node_to_providers.items():
        providers_to_nodes[tuple(v)].append(k)

    provider_to_providers = defaultdict(list)
    for k in providers_to_nodes:
        for provider in k:
            provider_to_providers[provider].append(k)

    to_real_providers_kvs = []
    providers_to_name = {}
    providers_set = set()
    for k, v in provider_to_providers.items():
        v_t = tuple(v)
        if v_t not in providers_set:
            providers_set.add(v_t)
            if len(v) == 1:
                providers_to_name[v[0]] = k
            to_real_providers_kvs.append((k, v))

    real_provider_kvs = []
    for k, v in providers_to_nodes.items():
        if k not in providers_to_name:
            providers_to_name[k] = f"p_{'_'.join(k)}"
        real_provider_kvs.append((providers_to_name[k], v))

    for k, v in to_real_providers_kvs:
        for i, providers in enumerate(v):
            v[i] = providers_to_name[providers]
        v.sort(key=lambda k: to_order[k])

    to_real_providers_kvs.sort(key=lambda kv: to_order[kv[0]])
    to_real_providers = dict(to_real_providers_kvs)
    real_provider_kvs.sort(key=lambda kv: to_order[kv[0]])
    real_provider_map = dict(real_provider_kvs)

    return to_real_providers, real_provider_map


def _exclude_p_Other(to_real_providers, real_provider_map, name_to_node_map):
    if 'Other' in to_real_providers:
        excluded = []
        if 'p_Other' in to_real_providers['Other']:
            to_real_providers['Other'].remove('p_Other')
            excluded = real_provider_map['p_Other']
            del real_provider_map['p_Other']
        elif 'Other' in to_real_providers['Other'] and all('Other' not in v and k != 'Other' for k, v in to_real_providers.items()):
            del to_real_providers['Other']
            excluded = real_provider_map['Other']
            del real_provider_map['Other']
        for p in excluded:
            del name_to_node_map[p]


def _split_and_write_providers(y: YAML, providers_dir, clash=None, providers_dirs=None, exclude=None):
    if clash:
        name_to_node_map, provider_map = _parse_node_groups(y, clash, exclude)
    else:
        name_to_node_map, provider_map = _read_and_merge_providers(y, providers_dirs, exclude)
    to_real_providers, real_provider_map = _split_providers(provider_map)
    clear_files(providers_dir)
    for k, v in (provider_map | real_provider_map).items():
        write(
            f'{providers_dir}/{k}.yaml',
            lambda f: y.dump({'proxies': [name_to_node_map[name] for name in v]}, f)
        )
    _exclude_p_Other(to_real_providers, real_provider_map, name_to_node_map)
    provider_map = {k: [p for name in v for p in real_provider_map[name]] for k, v in to_real_providers.items()}
    real_providers = [*real_provider_map]
    return provider_map, to_real_providers, real_providers, name_to_node_map


def _add_proxy_providers(cfg, real_providers, providers_dir):
    providers = {}
    base_provider = _base_yaml()['proxy-providers']['All']
    for k in real_providers:
        provider = deepcopy(base_provider)
        provider['url'] = get_pp_url(f'{providers_dir}/{k}.yaml')
        provider['path'] = f'{providers_dir}/{k}.yaml'
        providers[k] = provider
    cfg['proxy-providers'] = providers


def _remove_redundant_groups(cfg, provider_map):
    groups = cfg['proxy-groups']
    removed_groups = set()
    i = 0
    for g in groups:
        if 'use' in g and g['use'][0] not in provider_map:
            removed_groups.add(g['name'])
        else:
            groups[i] = g
            i += 1
    del groups[i:]
    for g in groups:
        proxies = g.get('proxies')
        if proxies:
            i = 0
            for name in proxies:
                if name not in removed_groups:
                    proxies[i] = name
                    i += 1
            del proxies[i:]


def _to_real_providers(cfg, to_real_providers):
    for g in cfg['proxy-groups']:
        if 'use' in g:
            g.pop('url', None)
            g.pop('interval', None)
            g['use'] = to_real_providers[g['use'][0]]


def _to_proxies(cfg, provider_map):
    for g in cfg['proxy-groups']:
        if 'use' in g:
            g['proxies'] = provider_map[g['use'][0]]
            del g['use']


def gen_base64_and_clash_config(base64_path, clash_path, clash_pp_path, providers_dir, base64=None, base64_paths=None, clash=None, providers_dirs=None, exclude=None):
    y = _yaml()
    split_result = _split_and_write_providers(
        y, providers_dir, clash, providers_dirs, re.compile(exclude, re.I) if exclude else None)
    provider_map, to_real_providers, real_providers, name_to_node_map = split_result
    if not name_to_node_map:
        raise SCError('无可用节点')
    base64_node_n = _gen_base64_config(base64_path, name_to_node_map, base64, base64_paths)
    _gen_clash_config(y, clash_path, clash_pp_path, providers_dir, name_to_node_map,
                      provider_map, to_real_providers, real_providers)
    if base64_node_n != len(name_to_node_map):
        print(f'base64 ({base64_node_n}) 与 clash {len(name_to_node_map)} 节点数量不一致')
    return base64_node_n


def _gen_clash_config(y, clash_path, clash_pp_path, providers_dir, name_to_node_map, provider_map, to_real_providers, real_providers):
    cfg = deepcopy(_base_yaml())
    del cfg['proxy-providers']
    _remove_redundant_groups(cfg, provider_map)
    hardcode_cfg = deepcopy(cfg)

    _to_real_providers(cfg, to_real_providers)
    _add_proxy_providers(cfg, real_providers, providers_dir)
    cfg['rules'] = _rules()

    _to_proxies(hardcode_cfg, provider_map)
    hardcode_cfg['proxies'] = [*name_to_node_map.values()]
    hardcode_cfg['rules'] = _rules()

    write(clash_path, lambda f: y.dump(hardcode_cfg, f))
    write(clash_pp_path, lambda f: y.dump(cfg, f))


def _gen_base64_config(base64_path, name_to_node_map, base64=None, base64_paths=None):
    if base64_paths:
        base64s = (read(path, True) for path in base64_paths)
    else:
        base64s = [base64]
    lines = []
    for base64 in base64s:
        if not re_non_empty_base64.fullmatch(base64):
            raise Exception('_gen_base64_config: ' + (f'no base64: {base64}' if base64 else 'no content'))
        for line in b64decode(base64).splitlines():
            if get_name(line) in name_to_node_map:
                lines.append(line)
    write(base64_path, b64encode(b'\n'.join(lines) + b'\n'))
    return len(lines)
