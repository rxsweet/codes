import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
from random import choice
from threading import RLock, Thread
from time import sleep, time
from urllib.parse import (parse_qsl, unquote_plus, urlencode, urljoin,
                          urlsplit, urlunsplit)

import json5
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
# from requests.structures import CaseInsensitiveDict
# from selenium.webdriver.support.expected_conditions import any_of, title_is
# from selenium.webdriver.support.ui import WebDriverWait
# from undetected_chromedriver import Chrome, ChromeOptions
from urllib3 import Retry
from urllib3.util import parse_url

from ocr import ocr_code_iter
from utils import cached, get, parallel_map, rand_id, str2size, str2timestamp

REDIRECT_TO_GET = 1
REDIRECT_ORIGIN = 2
REDIRECT_PATH_QUERY = 4
REDIRECT_REFRESH = 8

re_scheme = re.compile(r'^(?:(https?):)?[\\/]*', re.I)

re_checked_in = re.compile(r'(?:已经?|重复)签到')
re_var_sub_token = re.compile(r'var sub_token = "(.+?)"')
re_email_code = re.compile(r'(?:码|碼|証|code).*?(?<![\da-z])([\da-z]{6})(?![\da-z])', re.I | re.S)

re_snapmail_domains = re.compile(r'emailDomainList.*?(\[.*?\])')
re_mailcx_js_path = re.compile(r'/_next/static/chunks/\d+-[\da-f]{16}.js')
re_mailcx_domains = re.compile(r'mailHosts:(\[.*?\])')
re_option_domain = re.compile(r'<option[^>]+value="@?((?:(?:[\da-z]+-)*[\da-z]+\.)+[a-z]+)"', re.I)

re_v2board_APP_NAME = re.compile(r'APP_NAME.*[=:]\s*[\'"](.+)[\'"]')

re_sspanel_invitation_num = re.compile(r'剩\D*(\d+)')
re_sspanel_initial_money = re.compile(r'得\s*(\d+(?:\.\d+)?)\s*元')
re_sspanel_sub_url = re.compile(r'https?:')
re_sspanel_expire = re.compile(r'等\D*(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})')
re_sspanel_traffic_today = re.compile(r'日已用\D*?([-+]?\d+(?:\.\d+)?[BKMGTPE]?)', re.I)
re_sspanel_traffic_past = re.compile(r'去已用\D*?([-+]?\d+(?:\.\d+)?[BKMGTPE]?)', re.I)
re_sspanel_traffic_remain = re.compile(r'剩.流量\D*?([-+]?\d+(?:\.\d+)?[BKMGTPE]?)', re.I)
re_sspanel_balance = re.compile(r'(?:[余餘][额額]|¥|￥)[\s¥￥：:]*(\d+(?:\.\d+)?)')
re_sspanel_tab_shop_id = re.compile(r'tab-shop-(\d+)')
re_sspanel_plan_num = re.compile(r'\d+')
re_sspanel_plan_id = re.compile(r'buy\D+(\d+)')
re_sspanel_price = re.compile(r'\d+(?:\.\d+)?')
re_sspanel_traffic = re.compile(r'\d+(?:\.\d+)?\s*[BKMGTPE]', re.I)
re_sspanel_duration = re.compile(r'(\d+)\s*(天|month)')

re_v2board_disabled = re.compile(r'关闭注册|邮箱后缀不处于白名单中|^验证码有误')
re_sspanel_disabled = re.compile(r'系统无法接受您的验证结果|非法请求|小老弟还会发送post请求啊|进行验证')


def bs(text):
    return BeautifulSoup(text, 'html.parser')


def get_redirect_url(r: requests.Response, refresh):
    if r.is_redirect:
        url = r.headers['Location']
    elif (
        refresh
        and 200 <= r.status_code < 400
        and (type := r.headers.get('Content-Type'))
        and type.startswith('text/html')
        and (tag := bs(r.text).find('meta', {'http-equiv': 'refresh'}))
    ):
        url = get(tag['content'].split('=', 1), 1, default=r.url)
    else:
        return None
    return urljoin(r.url, url)


class Response:
    def __init__(self, r: requests.Response, redirect):
        self.__content = r.content
        self.__headers = r.headers
        self.__status_code = r.status_code
        self.__reason = r.reason
        self.__url = r.url
        self.__redirect = redirect

    @property
    def content(self):
        return self.__content

    @property
    def headers(self):
        return self.__headers

    @property
    def status_code(self):
        return self.__status_code

    @property
    def ok(self):
        return 200 <= self.__status_code < 300

    @property
    def reason(self):
        return self.__reason

    @property
    def url(self):
        return self.__url

    @property
    def redirect(self):
        return self.__redirect

    @property
    @cached
    def text(self):
        return self.__content.decode()

    @cached
    def json(self):
        try:
            return json.loads(self.text)
        except json.JSONDecodeError as e:
            raise Exception(f'解析 json 失败: {e} ({self})')

    @cached
    def bs(self):
        return bs(self.text)

    @cached
    def __str__(self):
        return f'{self.__status_code} {self.__reason} {repr(self.text)}'


class Forbidden(Exception):
    def __init__(self, msg='拒绝访问'):
        super().__init__(msg)


class Session(requests.Session):
    def __init__(self, base=None, user_agent=None, max_redirects=5, allow_redirects=7, retry=3):
        super().__init__()
        self.mount('https://', HTTPAdapter(max_retries=Retry(total=retry, backoff_factor=0.1)))
        self.mount('http://', HTTPAdapter(max_retries=Retry(total=retry, backoff_factor=0.1)))
        self.max_redirects = max_redirects
        self.allow_redirects = allow_redirects
        self.headers['User-Agent'] = user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
        self.set_base(base)

    def set_base(self, base):
        if base:
            self.__base = re_scheme.sub(lambda m: f"{m[1] or 'https'}://", base.split('#', 1)[0])
        else:
            self.__base = None

    def set_origin(self, origin):
        if self.__base:
            if origin:
                base_split = urlsplit(self.__base)
                origin_split = urlsplit(re_scheme.sub(lambda m: f"{m[1] or base_split[0]}://", origin))
                self.__base = urlunsplit(origin_split[:2] + base_split[2:])
            else:
                self.__base = None
        else:
            self.set_base(origin)

    set_host = set_origin

    @property
    def base(self):
        return self.__base

    @property
    def host(self):
        return self.__base and urlsplit(self.__base).netloc

    @property
    def hostname(self):
        return self.__base and urlsplit(self.__base).hostname

    @property
    def origin(self):
        if self.__base:
            return '://'.join(urlsplit(self.__base)[:2])
        else:
            return None

    def close(self):
        super().close()
        # if hasattr(self, 'chrome'):
        #     self.chrome.quit()

    def reset(self):
        self.cookies.clear()
        self.headers.pop('authorization', None)
        self.headers.pop('token', None)
        # if hasattr(self, 'chrome'):
        #     self.chrome.delete_all_cookies()
        #     for cookie in self.chrome_default_cookies:
        #         self.chrome.add_cookie(cookie)

    def head(self, url='', **kwargs) -> Response:
        return self.request('HEAD', url, **kwargs)

    def get(self, url='', **kwargs) -> Response:
        return self.request('GET', url, **kwargs)

    def post(self, url='', data=None, **kwargs) -> Response:
        return self.request('POST', url, data, **kwargs)

    def put(self, url='', data=None, **kwargs) -> Response:
        return self.request('PUT', url, data, **kwargs)

    def request(self, method: str, url: str = '', data=None, timeout=10, allow_redirects=None, **kwargs):
        method = method.upper()
        url = urljoin(self.__base, url.split('#', 1)[0])
        kwargs.update(data=data, timeout=timeout, allow_redirects=False)
        if allow_redirects is None:
            allow_redirects = self.allow_redirects
        # if not hasattr(self, 'chrome'):
        res = super().request(method, url, **kwargs)
        redirect = 0
        if allow_redirects and (redirect_url := get_redirect_url(res, allow_redirects & REDIRECT_REFRESH)):
            no = ~allow_redirects
            url = res.url
            kwargs.pop('params', None)
            i = 0
            while True:
                i += 1
                if i > self.max_redirects:
                    raise requests.TooManyRedirects(f'重定向次数超过 {self.max_redirects} 次')
                if url == redirect_url:
                    if no & REDIRECT_TO_GET:
                        break
                    redirect |= REDIRECT_TO_GET
                    method = 'GET'
                    for k in ('data', 'files', 'json'):
                        kwargs.pop(k, None)
                else:
                    if no & REDIRECT_ORIGIN and no & REDIRECT_PATH_QUERY:
                        break
                    old, new = map(parse_url, (url, redirect_url))
                    ro = old[:4] != new[:4]
                    rpq = old.request_uri != new.request_uri
                    if (ro and no & REDIRECT_ORIGIN) or (rpq and no & REDIRECT_PATH_QUERY):
                        break
                    if ro:
                        redirect |= REDIRECT_ORIGIN
                    if rpq:
                        redirect |= REDIRECT_PATH_QUERY
                    url = redirect_url

                if not res.is_redirect:
                    redirect |= REDIRECT_REFRESH

                res = super().request(method, url, **kwargs)

                if res.status_code == 405 and method == 'POST':
                    if no & REDIRECT_TO_GET:
                        break
                    redirect |= REDIRECT_TO_GET
                    method = 'GET'
                    for k in ('data', 'files', 'json'):
                        kwargs.pop(k, None)
                    res = super().request(method, url, **kwargs)

                if not (redirect_url := get_redirect_url(res, allow_redirects & REDIRECT_REFRESH)):
                    break
        res = Response(res, redirect)
        if (
            res.status_code == 403
            or (res.ok and b'5 seconds' in res.content and (title := res.bs().title) and not title.text)
            or (res.status_code == 500 and b'turnstile' in res.content)
        ):
            raise Forbidden
        return res
        #     if True or res.status_code != 403 and (
        #         'Content-Type' not in res.headers
        #         or not res.headers['Content-Type'].startswith('text/html')
        #         or not res.content
        #         or res.content[0] != 60
        #         or not res.bs().title
        #         or res.bs().title.text not in ('Just a moment...', '')
        #     ):
        #         return res
        # cur_host = urlsplit(url).hostname
        # if urlsplit(self.get_chrome().current_url).hostname != cur_host:
        #     self.chrome.get('https://' + cur_host)
        #     WebDriverWait(self.chrome, 15).until_not(any_of(title_is('Just a moment...'), title_is('')))
        #     self.chrome_default_cookies = self.chrome.get_cookies()
        # headers = CaseInsensitiveDict()
        # if 'authorization' in self.headers:
        #     headers['authorization'] = self.headers['authorization']
        # if data:
        #     headers['Content-Type'] = 'application/x-www-form-urlencoded'
        #     body = repr(data if isinstance(data, str) else urlencode(data))
        # else:
        #     body = 'null'
        # content, header_list, status_code, reason = self.chrome.execute_script(f'''
        #     const res = await fetch({repr(url)}, {{ method: {repr(method)}, headers: {repr(headers)}, body: {body} }})
        #     return [new Uint8Array(await res.arrayBuffer()), [...res.headers], res.status, res.statusText]
        # ''')
        # return Response(bytes(content), CaseInsensitiveDict(header_list), int(status_code), reason)

    # def get_chrome(self):
    #     if not hasattr(self, 'chrome'):
    #         print(f'{self.host} using Chrome')
    #         options = ChromeOptions()
    #         options.add_argument('--disable-web-security')
    #         options.add_argument('--ignore-certificate-errors')
    #         options.add_argument('--allow-running-insecure-content')
    #         options.page_load_strategy = 'eager'
    #         self.chrome = Chrome(
    #             options=options,
    #             driver_executable_path=os.path.join(os.getenv('CHROMEWEBDRIVER'), 'chromedriver')
    #         )
    #         self.chrome.set_page_load_timeout(15)
    #     return self.chrome

    def get_ip_info(self):
        """return (ip, 位置, 运营商)"""
        addr = self.get(f'https://ip125.com/api/{self.get("https://ident.me").text}?lang=zh-CN').json()
        return (
            addr['query'],
            addr['country'] + (',' + addr['city'] if addr['city'] and addr['city'] != addr['country'] else ''),
            addr['isp'] + (',' + addr['org'] if addr['org'] and addr['org'] != addr['isp'] else '')
        )


class _ROSession(Session):
    def __init__(self, base=None, user_agent=None, allow_redirects=REDIRECT_ORIGIN):
        super().__init__(base, user_agent, allow_redirects=allow_redirects)
        self.__times = 0
        self.__redirect_origin = False

    @property
    def redirect_origin(self):
        return self.__redirect_origin

    def request(self, method, url='', *args, **kwargs):
        r = super().request(method, url, *args, **kwargs)
        if self.__times < 2:
            if r.redirect & REDIRECT_ORIGIN:
                print(f'{self.host}: {urljoin(self.base, url)} -> {r.url}')
                self.set_origin(r.url)
                self.__redirect_origin = True
            self.__times += 1
        return r


class V2BoardSession(_ROSession):
    def __set_auth(self, email: str, reg_info: dict):
        self.login_info = reg_info['data']
        self.email = email
        if 'v2board_session' not in self.cookies:
            self.headers['authorization'] = self.login_info['auth_data']

    def reset(self):
        super().reset()
        if hasattr(self, 'login_info'):
            del self.login_info
        if hasattr(self, 'email'):
            del self.email

    @staticmethod
    def raise_for_fail(res: dict):
        if 'data' not in res:
            if (msg := res.get('message')) and re_v2board_disabled.search(msg):
                raise Forbidden(msg)
            raise Exception(res)

    def register(self, email: str, password=None, email_code=None, invite_code=None) -> str | None:
        self.reset()
        res = self.post('api/v1/passport/auth/register', {
            'email': email,
            'password': password or email.split('@')[0],
            'email_code': email_code or '',
            'invite_code': invite_code or '',
        }).json()
        try:
            self.raise_for_fail(res)
        except Exception as e:
            if not isinstance(e, Forbidden) and (msg := res.get('message')):
                return msg
            raise e
        self.__set_auth(email, res)
        return None

    def login(self, email: str = None, password=None):
        if hasattr(self, 'login_info') and (not email or email == getattr(self, 'email', None)):
            return
        self.reset()
        res = self.post('api/v1/passport/auth/login', {
            'email': email,
            'password': password or email.split('@')[0]
        }).json()
        self.raise_for_fail(res)
        self.__set_auth(email, res)

    def send_email_code(self, email):
        res = self.post('api/v1/passport/comm/sendEmailVerify', {
            'email': email
        }, timeout=60).json()
        self.raise_for_fail(res)

    def buy(self, data=None):
        if not data:
            data = self.get_plan()
            if not data:
                return None
            data = urlencode(data)
        res = self.post(
            'api/v1/user/order/save',
            data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        ).json()
        self.raise_for_fail(res)
        res = self.post('api/v1/user/order/checkout', {
            'trade_no': res['data']
        }).json()
        self.raise_for_fail(res)
        return data

    def get_sub_url(self) -> str:
        res = self.get('api/v1/user/getSubscribe').json()
        self.raise_for_fail(res)
        self.sub_url = res['data']['subscribe_url']
        return self.sub_url

    def get_sub_info(self):
        res = self.get('api/v1/user/getSubscribe').json()
        self.raise_for_fail(res)
        d = res['data']
        return {
            'upload': d['u'],
            'download': d['d'],
            'total': d['transfer_enable'],
            'expire': d['expired_at']
        }

    def get_plan(self, min_price=0, max_price=0):
        r = self.get('api/v1/user/plan/fetch').json()
        self.raise_for_fail(r)
        min_price *= 100
        max_price *= 100
        plan = None
        _max = (0, 0, 0)
        for p in r['data']:
            if (ik := next(((i, k) for i, k in enumerate((
                'onetime_price',
                'three_year_price',
                'two_year_price',
                'year_price',
                'half_year_price',
                'quarter_price',
                'month_price',
            )) if (price := p.get(k)) is not None and min_price <= price <= max_price), None)):
                i, period = ik
                v = p[period], p['transfer_enable'], -i
                if v > _max:
                    _max = v
                    plan = {
                        'period': period,
                        'plan_id': p['id'],
                    }
        return plan


class SSPanelSession(_ROSession):
    def __init__(self, host=None, user_agent=None, auth_path=None):
        super().__init__(host, user_agent)
        self.auth_path = auth_path or 'auth'
        self.__pass_get_plan_time = False

    def reset(self):
        super().reset()
        if hasattr(self, 'email'):
            del self.email

    @staticmethod
    def raise_for_fail(res: dict):
        if not res.get('ret'):
            if (msg := res.get('msg')) and re_sspanel_disabled.search(msg):
                raise Forbidden(msg)
            raise Exception(res)

    def register(self, email: str, password=None, email_code=None, invite_code=None, name_eq_email=None, reg_fmt=None, im_type=False, aff=None) -> str | None:
        self.reset()
        email_code_k, invite_code_k = ('email_code', 'invite_code') if reg_fmt == 'B' else ('emailcode', 'code')
        password = password or email.split('@')[0]
        res = self.post(f'{self.auth_path}/register', {
            'name': email if name_eq_email == 'T' else password,
            'email': email,
            'passwd': password,
            'repasswd': password,
            email_code_k: email_code or '',
            invite_code_k: invite_code or '',
            **({'imtype': 1, 'wechat': password} if im_type else {}),
            **({'aff': aff} if aff is not None else {}),
        }).json()
        try:
            self.raise_for_fail(res)
        except Exception as e:
            if not isinstance(e, Forbidden) and (msg := res.get('msg')):
                return msg
            raise e
        self.email = email
        return None

    def login(self, email: str = None, password=None):
        if not email:
            email = self.email
        if 'email' in self.cookies and email == unquote_plus(self.cookies['email']):
            return
        self.reset()
        res = self.post(f'{self.auth_path}/login', {
            'email': email,
            'passwd': password or email.split('@')[0]
        }).json()
        self.raise_for_fail(res)
        self.email = email

    def send_email_code(self, email):
        res = self.post(f'{self.auth_path}/send', {
            'email': email
        }, timeout=60).json()
        self.raise_for_fail(res)

    def buy(self, data=None):
        if not data:
            data = self.get_plan(max_price=self.get_balance())
            if not data:
                return None
            data = urlencode(data)
        res = self.post(
            'user/buy',
            data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        ).json()
        self.raise_for_fail(res)
        return data

    def checkin(self):
        res = self.post('user/checkin').json()
        if not res.get('ret') and ('msg' not in res or not re_checked_in.search(res['msg'])):
            raise Exception(res)

    @staticmethod
    def normalize_sub_url(sub_url: str):
        split = [*urlsplit(sub_url)]
        if not split[3]:
            return sub_url
        split[3] = '&'.join(kv for kv in split[3].split('&') if kv.split('=', 1)[0] in ('sub', 'clash', 'mu'))
        if not split[3]:
            return None
        return urlunsplit(split)

    @staticmethod
    def is_clash_sub_url(sub_url: str):
        return any(k == 'clash' for k, _ in parse_qsl(urlsplit(sub_url).query))

    @staticmethod
    def get_sub_url_type_key(sub_url: str):
        split = [*urlsplit(sub_url)]
        split[2] = split[2].rsplit('/', 1)[0]
        return urlunsplit(split)

    def get_sub_urls(self) -> list[str]:
        sub_urls = {}
        r = self.get('user')
        if (tags := r.bs().find_all(attrs={'data-clipboard-text': re_sspanel_sub_url})):
            for tag in tags:
                sub_url = tag['data-clipboard-text']
                params = parse_qsl(urlsplit(sub_url).query)
                for k, v in params:
                    if k == 'url':
                        sub_url = v
                        params = parse_qsl(urlsplit(sub_url).query)
                        break
                if (sub_url := self.normalize_sub_url(sub_url)):
                    sub_urls[sub_url] = None
        elif (m := re_var_sub_token.search(r.text)):
            if (sub_url := self.normalize_sub_url(m[1])):
                sub_urls[sub_url] = None
        if sub_urls:
            sub_urls = [*sub_urls]
            first, *rest = sub_urls
            first = urlsplit(first).path.rsplit('/', 1)[-1]
            if not all(urlsplit(sub_url).path.rsplit('/', 1)[-1] == first for sub_url in rest):
                raise Exception(f'订阅链接有误: {sub_urls}')
            return sub_urls
        raise Exception('未找到订阅链接')

    def get_sub_url(self) -> str:
        sub_url = None
        r = self.get('user')
        if (tag := r.bs().find(attrs={'data-clipboard-text': re_sspanel_sub_url})):
            sub_url = tag['data-clipboard-text']
            for k, v in parse_qsl(urlsplit(sub_url).query):
                if k == 'url':
                    sub_url = v
                    break
        elif (m := re_var_sub_token.search(r.text)):
            sub_url = m[1]
        if sub_url:
            return sub_url.split('?')[0]
        raise Exception('未找到订阅链接')

    def get_sub_info(self):
        text = self.get('user').bs().text
        if not (
            (m_today := re_sspanel_traffic_today.search(text))
            and (m_past := re_sspanel_traffic_past.search(text))
            and (m_remain := re_sspanel_traffic_remain.search(text))
        ):
            return None
        m_expire = re_sspanel_expire.search(text)
        used = str2size(m_today[1]) + str2size(m_past[1])
        return {
            'upload': 0,
            'download': used,
            'total': used + str2size(m_remain[1]),
            'expire': str2timestamp(m_expire[1]) if m_expire else ''
        }

    def get_invite_info(self) -> tuple[str, int, float]:
        r = self.get('user/invite')
        if not r.ok:
            r = self.get('user/setting/invite')
        tag = r.bs().find(attrs={'data-clipboard-text': True})
        if not tag:
            raise Exception('未找到邀请码')
        invite_code = tag['data-clipboard-text']
        for k, v in parse_qsl(urlsplit(invite_code).query):
            if k == 'code':
                invite_code = v
                break
        t = r.bs().text
        m_in = re_sspanel_invitation_num.search(t)
        m_im = re_sspanel_initial_money.search(t)
        return invite_code, int(m_in[1]) if m_in else -1, float(m_im[1]) if m_im else 0

    def get_plan(self, min_price=0, max_price=0):
        doc = self.get('user/shop').bs()
        plan = None
        _max = (0, 0, 0)

        def up(id, price, traffic, duration):
            nonlocal plan, _max
            if min_price <= price <= max_price:
                v = price, traffic, duration
                if v > _max:
                    _max = v
                    plan = {'shop': id}

        if (tags := doc.find_all(id=re_sspanel_tab_shop_id)):
            for tag in tags:
                first = tag.find()
                if not first:
                    continue
                id = int(re_sspanel_tab_shop_id.fullmatch(tag['id'])[1])
                price = float(get(re_sspanel_price.search(first.text), 0, default=0))
                traffic = str2size(get(re_sspanel_traffic.search(tag.text), 0, default='1T'))
                duration = int(get(re_sspanel_duration.search(tag.text), 1, default=999))
                up(id, price, traffic, duration)
        elif (tags := doc.find_all(class_='pricing')):
            num_infos = []
            for tag in tags:
                m_price = re_sspanel_price.search(tag.find(class_='pricing-price').find().text)
                price = float(get(m_price, 0, default=0))
                if not (min_price <= price <= max_price):
                    continue
                traffic = str2size(get(re_sspanel_traffic.search(
                    tag.find(class_='pricing-padding').text), 0, default='1T'))
                cta = tag.find(class_='pricing-cta')
                onclick = cta.get('onclick') or cta.find()['onclick']
                m_id = re_sspanel_plan_id.search(onclick)
                if not m_id:
                    m_num = re_sspanel_plan_num.search(onclick)
                    if not m_num:
                        raise Exception('未找到 plan_num & plan_id')
                    num_infos.append((f'plan_{m_num[0]}', traffic))
                else:
                    duration = int(get(re_sspanel_duration.search(
                        tag.find(class_='pricing-padding').text), 1, default=999))
                    up(int(m_id[1]), price, traffic, duration)

            def fn(item):
                for id, price, _time in self.get_plan_infos(item[0]):
                    m_duration = re_sspanel_duration.search(_time)
                    if get(m_duration, 2) != 'month':
                        raise Exception(f'未知时间单位: {_time}')
                    yield id, float(price), item[1], int(m_duration[1]) * 30

            for plans in parallel_map(fn, num_infos):
                for args in plans:
                    up(*args)
        elif (tags := doc.find_all(class_='shop-price')):
            for tag in tags:
                id = int(re_sspanel_plan_id.search(tag.find_next_sibling(class_='btn')['onclick'])[1])
                price, traffic, duration = map(float, (tag.text, *tag.find_next_sibling().text.split(' / ')))
                up(id, price, traffic, duration)
        elif (tags := doc.find_all(class_='pricingTable-firstTable_table__pricing')):
            for tag in tags:
                id = int(re_sspanel_plan_id.search(
                    tag.find_next_sibling(class_='pricingTable-firstTable_table__getstart')['onclick']
                )[1])
                price = float(get(re_sspanel_price.search(tag.text), 0, default=0))
                traffic = str2size(get(re_sspanel_traffic.search(tag.find_next_sibling().text), 0, default='1T'))
                duration = int(get(re_sspanel_duration.search(tag.find_next_sibling().text), 1, default=999))
                up(id, price, traffic, duration)
        elif (tags := doc.find_all(class_='pricing-card')):
            for tag in tags:
                id = int(re_sspanel_plan_id.search(tag.find('button')['onclick'])[1])
                price = float(tag.find(class_='amount').text)
                traffic = str2size(re_sspanel_traffic.search(tag.find(class_='pricing-content').text)[0])
                duration = int(re_sspanel_duration.search(tag.find(class_='duration').text)[1])
                up(id, price, traffic, duration)
        return plan

    def get_plan_time(self, num):
        if not self.__pass_get_plan_time:
            r = self.get('user/shop/getplantime', params={'num': num})
            if r.ok:
                r = r.json()
                self.raise_for_fail(r)
                return r['plan_time']
            self.__pass_get_plan_time = True
        return ['1month']

    def get_plan_info(self, num, time):
        r = self.get('user/shop/getplaninfo', params={'num': num, 'time': time}).json()
        self.raise_for_fail(r)
        return r['id'], r['price']

    def get_plan_infos(self, num):
        return parallel_map(lambda time: (*self.get_plan_info(num, time), time), self.get_plan_time(num))

    def get_balance(self) -> float:
        m = re_sspanel_balance.search(self.get('user/code').bs().text)
        if m:
            return float(m[1])
        print(f'{self.host} 未找到余额')
        return 0.0


class HkspeedupSession(_ROSession):
    def reset(self):
        super().reset()
        if hasattr(self, 'email'):
            del self.email

    @staticmethod
    def raise_for_fail(res):
        if res.get('code') != 200:
            raise Exception(res)

    def get_captcha_code_and_key(self):
        r = self.post('captcha/create').json()
        self.raise_for_fail(r)
        r = r['data']
        return next(ocr_code_iter(r['img'])), r['key']

    def post_with_captcha(self, url, json, **kwargs) -> dict:
        for _ in range(3):
            json['verifyCode'], json['verifyKey'] = self.get_captcha_code_and_key()
            r = self.post(url, json=json, **kwargs).json()
            if r.get('message') != '图片验证码错误':
                break
        return r

    def register(self, email: str, password=None, email_code=None, invite_code=None) -> str | None:
        self.reset()
        password = password or email.split('@')[0]
        res = self.post_with_captcha('user/register', json={
            'code': email_code or '',
            'email': email,
            'ensurePassword': password,
            'inviteCode': invite_code,
            'password': password,
        })
        if res.get('code') == 200:
            self.email = email
            return None
        if 'message' in res:
            return res['message']
        raise Exception(res)

    def login(self, email: str = None, password=None):
        if not email:
            email = self.email
        if 'token' in self.headers and email == self.email:
            return
        self.reset()
        res = self.post('user/login', json={
            'email': email,
            'password': password or email.split('@')[0]
        }).json()
        self.raise_for_fail(res)
        self.headers['token'] = res['data']['token']
        self.email = email

    def send_email_code(self, email):
        res = self.post_with_captcha('user/sendAuthCode', json={
            'email': email
        }, timeout=60)
        self.raise_for_fail(res)

    def checkin(self):
        res = self.post('user/checkIn').json()
        if res.get('code') != 200 and ('message' not in res or not re_checked_in.search(res['message'])):
            raise Exception(res)

    def get_sub_url(self) -> str:
        res = self.get('user/info').json()
        self.raise_for_fail(res)
        self.sub_url = f"{self.base}/subscribe/{res['data']['subscribePassword']}"
        return self.sub_url


PanelSession = V2BoardSession | SSPanelSession | HkspeedupSession

panel_class_map = {
    'v2board': V2BoardSession,
    'sspanel': SSPanelSession,
    'hkspeedup': HkspeedupSession,
}


def guess_panel(host):
    info = {}
    session = _ROSession(host)
    try:
        try:
            r = session.get('api/v1/guest/comm/config', allow_redirects=15)
        except Forbidden:
            r = session.get()
            if not r.content:
                raise Forbidden
            if r.ok and session.redirect_origin:
                r = session.get('api/v1/guest/comm/config')
        if r.ok and not r.redirect & ~REDIRECT_ORIGIN:
            r.json()
            info['type'] = 'v2board'
            _r = session.get()
            if _r.ok and _r.bs().title:
                if (m := re_v2board_APP_NAME.search(_r.text)):
                    info['name'] = m[1]
                else:
                    info['name'] = _r.bs().title.text
            else:
                if (app_url := get(r.json(), 'data', 'app_url')):
                    session.set_base(app_url)
                _r = session.get('env.js')
                if _r.ok:
                    settings = json5.loads(_r.text[_r.text.index('{'):])
                    info['name'] = settings['title']
            if (
                (email_whitelist_suffix := get(r.json(), 'data', 'email_whitelist_suffix'))
                and not ('gmail.com' in email_whitelist_suffix or 'qq.com' in email_whitelist_suffix)
            ):
                info['email_domain'] = email_whitelist_suffix[0]
        elif 400 <= r.status_code < 500:
            _r = session.get('env.js')
            if _r.ok:
                info['type'] = 'v2board'
                settings = json5.loads(_r.text[_r.text.index('{'):])
                info['name'] = settings['title']
                info['api_host'] = parse_url(settings['host']).netloc
            elif 400 <= _r.status_code < 500:
                _r = session.get()
                if _r.ok:
                    if (tag := _r.bs().find('a', string='开始试用')):
                        api_host = parse_url(tag['href']).netloc
                        session.set_base(api_host)
                        _r = session.get('api/v1/guest/comm/config')
                        if _r.ok:
                            _r = session.get()
                            if _r.ok and (m := re_v2board_APP_NAME.search(_r.text)):
                                info['type'] = 'v2board'
                                info['name'] = m[1]
                                info['api_host'] = api_host
                    elif host == 'main.hkspeedup.com':
                        info['type'] = 'hkspeedup'
                        info['name'] = _r.bs().title.text
                        info['api_host'] = 'api.hkspeedup.com'
        if 'type' not in info:
            r = session.get('auth/login', allow_redirects=15)
            if r.ok and session.redirect_origin and r.redirect & REDIRECT_PATH_QUERY:
                r = session.get('auth/login')
            if r.ok:
                info['type'] = 'sspanel'
                info['name'] = r.bs().title.text.split(' — ')[-1]
            else:
                r = session.head('user/login')
                if r.ok:
                    info['type'] = 'sspanel'
                    r = session.get('404')
                    if r.ok:
                        info['name'] = r.bs().title.text.split(' — ')[-1]
                    info['auth_path'] = 'user'
                elif r.status_code == 405 and host == 'api.hkspeedup.com':
                    info['type'] = 'hkspeedup'
                    info['name'] = session.get('https://main.hkspeedup.com').bs().title.text
        if 'api_host' not in info and session.redirect_origin:
            info['api_host'] = session.host
    except Exception as e:
        info['error'] = e
    return info


class TempEmailSession(_ROSession):
    def get_domains(self) -> list[str]: ...
    def set_email_address(self, address: str): ...
    def get_messages(self) -> list[str]: ...


class MailGW(TempEmailSession):
    def __init__(self):
        super().__init__('api.mail.gw')

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


class Snapmail(TempEmailSession):
    def __init__(self):
        super().__init__('snapmail.cc')

    def get_domains(self) -> list[str]:
        r = self.get('scripts/controllers/addEmailBox.js')
        if not r.ok:
            raise Exception(f'获取 {self.host} addEmailBox.js 失败: {r}')
        return json5.loads(re_snapmail_domains.search(r.text)[1])

    def set_email_address(self, address: str):
        self.address = address

    def get_messages(self) -> list[str]:
        r = self.get(f'emailList/{self.address}')
        if r.ok and isinstance(r.json(), list):
            return [bs(item['html']).get_text('\n', strip=True) for item in r.json()]
        return []


class MailCX(TempEmailSession):
    def __init__(self):
        super().__init__('api.mail.cx/api/v1/')

    def get_domains(self) -> list[str]:
        r = self.get('https://mail.cx')
        if not r.ok:
            raise Exception(f'获取 {self.host} 页面失败: {r}')
        js_paths = []
        for js in r.bs().find_all('script'):
            if js.has_attr('src') and re_mailcx_js_path.fullmatch(js['src']):
                js_paths.append(js['src'])
        if js_paths:
            executor = ThreadPoolExecutor(len(js_paths))
            try:
                for future in as_completed(executor.submit(self.get, urljoin('https://mail.cx', js_path)) for js_path in js_paths):
                    r = future.result()
                    if r.ok:
                        m = re_mailcx_domains.search(r.text)
                        if m:
                            return json5.loads(m[1])
            finally:
                executor.shutdown(wait=False, cancel_futures=True)
        return []

    def set_email_address(self, address: str):
        r = self.post('auth/authorize_token')
        if not r.ok:
            raise Exception(f'获取 {self.host} token 失败: {r}')
        self.headers['Authorization'] = f'Bearer {r.json()}'
        self.address = address

    def get_messages(self) -> list[str]:
        r = self.get(f'mailbox/{self.address}')
        return [
            r.json()['body']['text']
            for r in parallel_map(self.get, (f'mailbox/{self.address}/{item["id"]}' for item in r.json()))
            if r.ok
        ] if r.ok else []


class GuerrillaMail(TempEmailSession):
    def __init__(self):
        super().__init__('api.guerrillamail.com/ajax.php')

    def get_domains(self) -> list[str]:
        r = self.get('https://www.spam4.me')
        if not r.ok:
            raise Exception(f'获取 spam4.me 页面失败: {r}')
        return re_option_domain.findall(r.text)

    def set_email_address(self, address: str):
        r = self.get(f'?f=set_email_user&email_user={address.split("@")[0]}')
        if not (r.ok and r.content and r.json().get('email_addr')):
            raise Exception(f'设置 {self.host} 账户失败: {r}')

    def get_messages(self) -> list[str]:
        r = self.get('?f=get_email_list&offset=0')
        return [
            bs(r.json()['mail_body']).get_text('\n', strip=True)
            for r in parallel_map(self.get, (f'?f=fetch_email&email_id={item["mail_id"]}' for item in r.json()['list']))
            if r.ok and r.content and r.text != 'false'
        ] if r.ok and r.content else []


class Emailnator(TempEmailSession):
    def __init__(self):
        super().__init__('www.emailnator.com/message-list')

    def get_domains(self) -> list[str]:
        return ['smartnator.com', 'femailtor.com', 'psnator.com', 'mydefipet.live', 'tmpnator.live']

    def set_email_address(self, address: str):
        self.get()
        if not (token := self.cookies.get('XSRF-TOKEN')):
            raise Exception(f'获取 {self.host} XSRF-TOKEN 失败')
        self.headers['x-xsrf-token'] = unquote_plus(token)
        r = self.post(json={'email': address})
        if not r.ok:
            raise Exception(f'设置 {self.host} 账户失败({address}): {r}')
        self.address = address

    def get_messages(self) -> list[str]:
        r = self.post(json={'email': self.address})
        def fn(item): return self.post(json={'email': self.address, 'messageID': item['messageID']})
        return [
            r.bs().get_text('\n', strip=True)
            for r in parallel_map(fn, r.json()['messageData'][1:])
            if r.ok
        ] if r.ok else []


class Moakt(TempEmailSession):
    def __init__(self):
        super().__init__('moakt.com')

    def get_domains(self) -> list[str]:
        r = self.get()
        if not r.ok:
            raise Exception(f'获取 {self.host} 页面失败: {r}')
        return re_option_domain.findall(r.text)

    def set_email_address(self, address: str):
        username, domain = address.split('@')
        r = self.post('inbox', {'domain': domain, 'username': username})
        if 'tm_session' not in self.cookies:
            raise Exception(f'设置 {self.host} 账户失败: {r}')

    def get_messages(self) -> list[str]:
        r = self.get('inbox')
        return [
            r.bs().get_text('\n', strip=True)
            for r in parallel_map(self.get, (f"{item['href']}/content" for item in r.bs().select('.tm-table td:first-child>a')))
            if r.ok
        ] if r.ok else []


class Rootsh(TempEmailSession):
    def __init__(self):
        super().__init__('rootsh.com')
        self.headers['Accept-Language'] = 'zh-CN,zh;q=0.9'

    def get_domains(self) -> list[str]:
        r = self.get()
        if not r.ok:
            raise Exception(f'获取 {self.host} 页面失败: {r}')
        return [a.text for a in r.bs().select('#domainlist a')]

    def set_email_address(self, address: str):
        if 'mail' not in self.cookies:
            self.get()
        r = self.post('applymail', {'mail': address})
        if not r.ok or r.json()['success'] != 'true':
            raise Exception(f'设置 {self.host} 账户失败: {r}')
        self.address = address

    def get_messages(self) -> list[str]:
        r = self.post('getmail', {'mail': self.address})
        prefix = f"win/{self.address.replace('@', '(a)').replace('.', '-_-')}/"
        return [
            r.bs().get_text('\n', strip=True)
            for r in parallel_map(self.get, (prefix + item[4] for item in r.json()['mail']))
            if r.ok
        ] if r.ok else []


class Linshiyou(TempEmailSession):
    def __init__(self):
        super().__init__('linshiyou.com')

    def get_domains(self) -> list[str]:
        r = self.get()
        if not r.ok:
            raise Exception(f'获取 {self.host} 页面失败: {r}')
        return re_option_domain.findall(r.text)

    def set_email_address(self, address: str):
        r = self.get('user.php', params={'user': address})
        if not r.ok or r.text != address:
            raise Exception(f'设置 {self.host} 账户失败: {r}')
        self.address = address

    def get_messages(self) -> list[str]:
        self.set_email_address(self.address)
        r = self.get('mail.php')
        if r.ok and r.content:
            return [tag.get_text('\n', strip=True) for tag in r.bs().find_all(class_='tmail-email-body-content')]
        return []


@cached
def temp_email_domain_to_session_type(domain: str = None) -> dict[str, type[TempEmailSession]] | type[TempEmailSession] | None:
    if domain:
        return temp_email_domain_to_session_type().get(domain)

    session_types = TempEmailSession.__subclasses__()

    def fn(session_type: type[TempEmailSession]):
        try:
            domains = session_type().get_domains()
        except Exception as e:
            domains = []
            print(e)
        return session_type, domains

    return {d: s for s, ds in parallel_map(fn, session_types) for d in ds}


class TempEmail:
    def __init__(self, banned_domains=None):
        self.__lock = RLock()
        self.__queues: list[tuple[str, Queue, float]] = []
        self.__banned = set(banned_domains or [])

    @property
    @cached
    def email(self) -> str:
        id = rand_id()
        domain_len_limit = 31 - len(id)
        domain = choice([
            d for d in temp_email_domain_to_session_type()
            if len(d) <= domain_len_limit and d not in self.__banned
        ])
        address = f'{id}@{domain}'
        self.__session = temp_email_domain_to_session_type(domain)()
        self.__session.set_email_address(address)
        del self.__banned
        return address

    def get_email_code(self, keyword, timeout=60) -> str | None:
        queue = Queue(1)
        with self.__lock:
            self.__queues.append((keyword, queue, time() + timeout))
            if not hasattr(self, f'_{TempEmail.__name__}__th'):
                self.__th = Thread(target=self.__run)
                self.__th.start()
        return queue.get()

    def __run(self):
        while True:
            sleep(1)
            try:
                messages = self.__session.get_messages()
            except Exception as e:
                messages = []
                print(f'TempEmail.__run: {e}')
            with self.__lock:
                new_len = 0
                for item in self.__queues:
                    keyword, queue, end_time = item
                    for message in messages:
                        if keyword in message:
                            m = re_email_code.search(message)
                            queue.put(m[1] if m else m)
                            break
                    else:
                        if time() > end_time:
                            queue.put(None)
                        else:
                            self.__queues[new_len] = item
                            new_len += 1
                del self.__queues[new_len:]
                if new_len == 0:
                    del self.__th
                    break
