import os
import re
from base64 import b64decode, b64encode
from collections import defaultdict
from copy import deepcopy
from random import randint
from threading import RLock
from time import time
from urllib.parse import quote, urljoin

from ruamel.yaml import YAML, CommentedMap

from apis import Session
from get_trial_update_url import get_short_url
from utils import (DOMAIN_SUFFIX_Tree, IP_CIDR_SegmentTree, clear_files,
                   get_name, list_file_paths, re_non_empty_base64, read,
                   read_cfg, write)

github_raw_url_prefix = f"https://raw.kgithub.com/{os.getenv('GITHUB_REPOSITORY')}/{os.getenv('GITHUB_REF_NAME')}"

subconverters = [row[0] for row in read_cfg('subconverters.cfg')['default']]


def _yaml():
    yaml = YAML()
    yaml.version = (1, 1)
    yaml.width = float('inf')
    return yaml


def _get_by_any(session: Session, url):
    if session.host:
        try:
            res = session.get(url)
            if res.ok:
                return res
        except Exception:
            pass
    idx_map = {}
    for i in range(len(subconverters) - 1, -1, -1):
        j = randint(0, i)
        session.set_base(subconverters[idx_map.get(j, j)])
        idx_map[j] = idx_map.get(i, i)
        try:
            res = session.get(url)
            if res.ok:
                return res
        except Exception:
            pass
    return res


_lock_sc_config_url = RLock()
_sc_config_url = None


def _get_sc_config_url():
    global _sc_config_url
    with _lock_sc_config_url:
        if not _sc_config_url:
            try:
                """
                data = Session().get(
                    'https://api.github.com/repos/zsokami/ACL4SSR/git/refs/heads/main',
                    headers={'Authorization': f"Bearer {os.getenv('GITHUB_TOKEN')}"}
                ).json()
                """
                #先用以前的方法，避免使用GITHUB_TOKEN
                data = Session().get('https://api.github.com/repos/zsokami/ACL4SSR/git/refs/heads/main').json()
                try:
                    sha = data['object']['sha']
                except KeyError:
                    raise Exception(data)
                _sc_config_url = f'https://raw.githubusercontent.com/zsokami/ACL4SSR/{sha}/ACL4SSR_Online_Full_Mannix.ini'
            except Exception as e:
                raise Exception(f'_get_sc_config_url: 获取订阅转换配置链接失败: {e}')
    return _sc_config_url

_lock_base_clash_config = RLock()
_base_yaml: CommentedMap = None
_group_to_provider_map = None
_rules = None


def _cache_base_clash_config():
    global _base_yaml, _group_to_provider_map, _rules
    with _lock_base_clash_config:
        if not _base_yaml:
            session = Session(user_agent='ClashforWindows')
            url = f"sub?target=clash&config={_get_sc_config_url()}&url=ss://YWVzLTEyOC1nY206YWJj@c.c:1%231"
            try:
                res = _get_by_any(session, url)
                y = _yaml()
                cfg = y.load(res.content)
                _base_yaml = read('base.yaml', reader=y.load)
                _group_to_provider_map = {g['name']: g['use'][0] for g in _base_yaml['proxy-groups']}
                groups = _base_yaml['proxy-groups'] = cfg['proxy-groups']
                for g in groups:
                    if (p := _group_to_provider_map.get(g['name'])):
                        del g['proxies']
                        g['use'] = [p]
                        _base_yaml['proxy-providers'].setdefault(p, None)
                _rules = _remove_redundant_rules(cfg['rules'])
            except Exception as e:
                raise Exception(f'_cache_base_clash_config: 获取基本 clash 配置失败: {e}')


def _get_base_yaml():
    _cache_base_clash_config()
    return _base_yaml


def _get_group_to_provider_map():
    _cache_base_clash_config()
    return _group_to_provider_map


def _get_rules():
    _cache_base_clash_config()
    return _rules


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


def get(url, suffix=None):
    session = Session(user_agent='ClashforWindows')
    url = '|'.join(f'{part}#{time()}' for part in url.split('|'))
    params = f"config={_get_sc_config_url()}&url={quote(url)}"
    if suffix:
        params += '&rename=' + quote(f'$@{suffix}')
    clash_url = f'sub?target=clash&udp=true&scv=true&expand=false&classic=true&{params}'
    base64_url = f'sub?target=mixed&{params}'

    res = _get_by_any(session, clash_url)
    info = res.headers.get('subscription-userinfo')
    if info:
        info = dict(kv.split('=') for kv in info.split('; '))
    clash = res.content
    clash_url = urljoin(session.base, clash_url)

    res = _get_by_any(session, base64_url)
    base64 = res.content
    base64_url = urljoin(session.base, base64_url)

    return info, base64, clash, base64_url, clash_url


def _parse_node_groups(y: YAML, clash, exclude: re.Pattern = None):
    cfg = y.load(clash)
    g_to_p = _get_group_to_provider_map()
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
    to_order = defaultdict(lambda: 99, ((k, i) for i, k in enumerate(_get_base_yaml()['proxy-providers'])))

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


def _add_proxy_providers(cfg, real_providers, providers_dir, use_short_url):
    providers = {}
    base_provider = _get_base_yaml()['proxy-providers']['All']
    for k in real_providers:
        provider = deepcopy(base_provider)
        if use_short_url:
            provider['url'] = get_short_url(f'{providers_dir}/{k}.yaml')
        else:
            provider['url'] = f'{github_raw_url_prefix}/{providers_dir}/{k}.yaml'
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


def gen_base64_and_clash_config(base64_path, clash_path, providers_dir, base64=None, base64_paths=None, clash=None, providers_dirs=None, exclude=None):
    y = _yaml()
    split_result = _split_and_write_providers(
        y, providers_dir, clash, providers_dirs, re.compile(exclude, re.I) if exclude else None)
    provider_map, to_real_providers, real_providers, name_to_node_map = split_result
    base64_node_n = _gen_base64_config(base64_path, name_to_node_map, base64, base64_paths)
    _gen_clash_config(y, clash_path, providers_dir, name_to_node_map, provider_map, to_real_providers, real_providers)
    if base64_node_n != len(name_to_node_map):
        print(f'base64 ({base64_node_n}) 与 clash {len(name_to_node_map)} 节点数量不一致')
    return base64_node_n


def _gen_clash_config(y, clash_path, providers_dir, name_to_node_map, provider_map, to_real_providers, real_providers):
    cfg = deepcopy(_get_base_yaml())
    del cfg['proxy-providers']
    _remove_redundant_groups(cfg, provider_map)
    hardcode_cfg = deepcopy(cfg)

    _to_real_providers(cfg, to_real_providers)
    _add_proxy_providers(cfg, real_providers, providers_dir, clash_path == 'trial.yaml')
    cfg['rules'] = _get_rules()

    _to_proxies(hardcode_cfg, provider_map)
    hardcode_cfg['proxies'] = [*name_to_node_map.values()]
    hardcode_cfg['rules'] = _get_rules()

    write(clash_path, lambda f: y.dump(hardcode_cfg, f))
    #先注释掉，不写_pp
    #prefix, ext = os.path.splitext(clash_path)
    #write(f'{prefix}_pp{ext}', lambda f: y.dump(cfg, f))


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
