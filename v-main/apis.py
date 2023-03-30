import json
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
from random import choice
from threading import RLock, Thread
from time import sleep, time
from urllib.parse import parse_qsl, unquote_plus, urlencode, urljoin, urlsplit

import json5
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from requests.structures import CaseInsensitiveDict
from selenium.webdriver.support.expected_conditions import any_of, title_is
from selenium.webdriver.support.ui import WebDriverWait
from undetected_chromedriver import Chrome, ChromeOptions
from urllib3 import Retry

from utils import get_id, parallel_map, str2size, str2timestamp

re_checked_in = re.compile(r'(?:已经?|重复)签到')
re_var_sub_token = re.compile(r'var sub_token = "(.+?)"')
re_email_code = re.compile(r'(?:码|碼|証|code).*?(?<![\da-z])([\da-z]{6})(?![\da-z])', re.I | re.S)

re_snapmail_domains = re.compile(r'emailDomainList.*?(\[.*?\])')
re_mailcx_js_path = re.compile(r'/_next/static/chunks/\d+-[\da-f]{16}.js')
re_mailcx_domains = re.compile(r'mailHosts:(\[.*?\])')
re_option_domain = re.compile(r'<option[^>]+value="@?((?:(?:[\da-z]+-)*[\da-z]+\.)+[a-z]+)"', re.I)

re_invitation_num = re.compile(r'剩\D*(\d+)')
re_sspanel_sub_url = re.compile(r'https?:')
re_sspanel_expire = re.compile(r'等\D*(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})')
re_sspanel_traffic_today = re.compile(r'日已用\D*?([-+]?\d+(?:\.\d+)?[BKMGTPE]?)', re.I)
re_sspanel_traffic_past = re.compile(r'去已用\D*?([-+]?\d+(?:\.\d+)?[BKMGTPE]?)', re.I)
re_sspanel_traffic_remain = re.compile(r'剩.流量\D*?([-+]?\d+(?:\.\d+)?[BKMGTPE]?)', re.I)


def bs(text):
    return BeautifulSoup(text, 'html.parser')


class Response:
    def __init__(self, content: bytes, headers: CaseInsensitiveDict[str], status_code: int, reason: str):
        self.content = content
        self.headers = headers
        self.status_code = status_code
        self.reason = reason

    @property
    def ok(self):
        return 200 <= self.status_code < 300

    @property
    def text(self):
        if not hasattr(self, '_Response__text'):
            self.__text = self.content.decode()
        return self.__text

    def json(self):
        if not hasattr(self, '_Response__json'):
            try:
                self.__json = json.loads(self.text)
            except json.JSONDecodeError as e:
                raise Exception(f'解析 json 失败: {e} ({self})')
        return self.__json

    def bs(self):
        if not hasattr(self, '_Response__bs'):
            self.__bs = bs(self.text)
        return self.__bs

    def __str__(self):
        return f'{self.status_code} {self.reason} {repr(self.text)}'


class Session(requests.Session):
    def __init__(self, host=None, user_agent=None):
        super().__init__()
        self.mount('https://', HTTPAdapter(max_retries=Retry(total=3, backoff_factor=0.1)))
        self.mount('http://', HTTPAdapter(max_retries=Retry(total=3, backoff_factor=0.1)))
        self.headers['User-Agent'] = user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
        self.set_host(host)

    def set_host(self, host):
        if host:
            self.base = 'https://' + host
            self.host = host
        else:
            self.base = None
            self.host = None

    def close(self):
        super().close()
        if hasattr(self, 'chrome'):
            self.chrome.quit()

    def reset(self):
        self.cookies.clear()
        self.headers.pop('authorization', None)
        self.headers.pop('token', None)
        if hasattr(self, 'chrome'):
            self.chrome.delete_all_cookies()
            for cookie in self.chrome_default_cookies:
                self.chrome.add_cookie(cookie)

    def head(self, url='', **kwargs) -> Response:
        return super().head(url, **kwargs)

    def get(self, url='', **kwargs) -> Response:
        return super().get(url, **kwargs)

    def post(self, url='', data=None, **kwargs) -> Response:
        return super().post(url, data, **kwargs)

    def put(self, url='', data=None, **kwargs) -> Response:
        return super().put(url, data, **kwargs)

    def request(self, method, url: str = '', data=None, timeout=10, allow_redirects=True, **kwargs):
        url = urljoin(self.base, url)
        if not hasattr(self, 'chrome'):
            for _ in range(5):
                res = super().request(method, url, data=data, timeout=timeout, allow_redirects=False, **kwargs)
                res = Response(res.content, res.headers, res.status_code, res.reason)
                if not (allow_redirects and 300 <= res.status_code < 400):
                    break
                url = res.headers['Location']
                self.set_host(urlsplit(url).hostname)
                kwargs.pop('params', None)
            else:
                raise requests.TooManyRedirects('重定向次数达到 5 次')
            if True or res.status_code != 403 and (
                'Content-Type' not in res.headers
                or not res.headers['Content-Type'].startswith('text/html')
                or not res.content
                or res.content[0] != 60
                or not res.bs().title
                or res.bs().title.text not in ('Just a moment...', '')
            ):
                return res
        cur_host = urlsplit(url).hostname
        if urlsplit(self.get_chrome().current_url).hostname != cur_host:
            self.chrome.get('https://' + cur_host)
            WebDriverWait(self.chrome, 15).until_not(any_of(title_is('Just a moment...'), title_is('')))
            self.chrome_default_cookies = self.chrome.get_cookies()
        headers = CaseInsensitiveDict()
        if 'authorization' in self.headers:
            headers['authorization'] = self.headers['authorization']
        if data:
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            body = repr(data if isinstance(data, str) else urlencode(data))
        else:
            body = 'null'
        content, header_list, status_code, reason = self.chrome.execute_script(f'''
            const res = await fetch({repr(url)}, {{ method: {repr(method)}, headers: {repr(headers)}, body: {body} }})
            return [new Uint8Array(await res.arrayBuffer()), [...res.headers], res.status, res.statusText]
        ''')
        return Response(bytes(content), CaseInsensitiveDict(header_list), int(status_code), reason)

    def get_chrome(self):
        if not hasattr(self, 'chrome'):
            print(f'{self.host} using Chrome')
            options = ChromeOptions()
            options.add_argument('--disable-web-security')
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--allow-running-insecure-content')
            options.page_load_strategy = 'eager'
            self.chrome = Chrome(
                options=options,
                driver_executable_path=os.path.join(os.getenv('CHROMEWEBDRIVER'), 'chromedriver')
            )
            self.chrome.set_page_load_timeout(15)
        return self.chrome

    def get_ip_info(self):
        """return (ip, 位置, 运营商)"""
        addr = self.get(f'https://ip125.com/api/{self.get("https://ident.me").text}?lang=zh-CN').json()
        return (
            addr['query'],
            addr['country'] + (',' + addr['city'] if addr['city'] and addr['city'] != addr['country'] else ''),
            addr['isp'] + (',' + addr['org'] if addr['org'] and addr['org'] != addr['isp'] else '')
        )


class V2BoardSession(Session):
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
    def raise_for_fail(res):
        if 'data' not in res:
            raise Exception(res)

    def register(self, email: str, password=None, email_code=None, invite_code=None) -> str | None:
        self.reset()
        res = self.post('api/v1/passport/auth/register', {
            'email': email,
            'password': password or email.split('@')[0],
            'email_code': email_code or '',
            'invite_code': invite_code or '',
        }).json()
        if 'data' in res:
            self.__set_auth(email, res)
            return None
        if 'message' in res:
            return res['message']
        raise Exception(res)

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

    def buy(self, data):
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

    def get_sub_url(self, **params) -> str:
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


class SSPanelSession(Session):
    def __init__(self, host=None, user_agent=None, auth_path=None):
        super().__init__(host, user_agent)
        self.auth_path = auth_path or 'auth'

    def reset(self):
        super().reset()
        if hasattr(self, 'email'):
            del self.email

    @staticmethod
    def raise_for_fail(res):
        if not res.get('ret'):
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
        if res.get('ret'):
            self.email = email
            return None
        if 'msg' in res:
            return res['msg']
        raise Exception(res)

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

    def buy(self, data):
        res = self.post(
            'user/buy',
            data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        ).json()
        self.raise_for_fail(res)

    def checkin(self):
        res = self.post('user/checkin').json()
        if not res.get('ret') and ('msg' not in res or not re_checked_in.search(res['msg'])):
            raise Exception(res)

    def get_sub_url(self, **params) -> str:
        r = self.get('user')
        tag = r.bs().find(attrs={'data-clipboard-text': re_sspanel_sub_url})
        if tag:
            sub_url = tag['data-clipboard-text']
            for k, v in parse_qsl(urlsplit(sub_url).query):
                if k == 'url':
                    sub_url = v
                    break
            params = {k: params[k] for k in params.keys() & ('sub', 'clash', 'mu')}
            if not params:
                params['sub'] = '3'
            sub_url_prefix = f"{sub_url.split('?')[0]}?"
            sub_url = '|'.join(f'{sub_url_prefix}{k}={v}' for k, vs in params.items() for v in vs.split())
        else:
            m = re_var_sub_token.search(r.text)
            if not m:
                raise Exception('未找到订阅链接')
            sub_url = m[1]
        return sub_url

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

    def get_invite_info(self) -> tuple[str, int]:
        r = self.get('user/invite', allow_redirects=False)
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
        m_in = re_invitation_num.search(r.bs().text)
        return invite_code, int(m_in[1]) if m_in else -1


class HkspeedupSession(Session):
    def reset(self):
        super().reset()
        if hasattr(self, 'email'):
            del self.email

    @staticmethod
    def raise_for_fail(res):
        if res.get('code') != 200:
            raise Exception(res)

    def register(self, email: str, password=None, email_code=None, invite_code=None) -> str | None:
        self.reset()
        password = password or email.split('@')[0]
        res = self.post('user/register', json={
            'email': email,
            'password': password,
            'ensurePassword': password,
            **({'code': email_code} if email_code else {}),
            **({'inviteCode': invite_code} if invite_code else {})
        }).json()
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
        res = self.post('user/sendAuthCode', json={
            'email': email
        }, timeout=60).json()
        self.raise_for_fail(res)

    def checkin(self):
        res = self.post('user/checkIn').json()
        if res.get('code') != 200 and ('message' not in res or not re_checked_in.search(res['message'])):
            raise Exception(res)

    def get_sub_url(self, **params) -> str:
        res = self.get('user/info').json()
        self.raise_for_fail(res)
        self.sub_url = f"{self.base}/subscribe/{res['data']['subscribePassword']}"
        return self.sub_url


class TempEmailSession(Session):
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
        r = self.post('inbox', {'domain': domain, 'username': username}, allow_redirects=False)
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


class TempEmail:
    def __init__(self):
        self.__lock_account = RLock()
        self.__lock = RLock()
        self.__queues: list[tuple[str, Queue, float]] = []

    def replace(self, new_id) -> 'TempEmail':
        o = TempEmail()
        o.__session = type(self.__session)()
        o.__address = f"{new_id}@{self.__address.split('@')[1]}"
        o.__session.set_email_address(o.__address)
        return o

    def get_email(self, id=None) -> str:
        with self.__lock_account:
            if not hasattr(self, '_TempEmail__address'):
                #sessions = MailGW(), Snapmail(), MailCX(), GuerrillaMail(), Emailnator(), Moakt(), Rootsh(), Linshiyou()
                sessions = MailGW(), Snapmail(), MailCX(), Emailnator(), Rootsh(), Linshiyou()
                if not id:
                    id = get_id()
                domain_len_limit = 31 - len(id)

                def fn(session: TempEmailSession):
                    try:
                        domains = session.get_domains()
                    except Exception as e:
                        domains = []
                        print(e)
                    return session, domains

                session, domain = choice([
                    (s, d)
                    for s, ds in parallel_map(fn, sessions)
                    for d in ds if len(d) <= domain_len_limit
                ])

                address = f'{id}@{domain}'
                session.set_email_address(address)
                self.__session = session
                self.__address = address
        return self.__address

    def get_email_code(self, keyword) -> str | None:
        queue = Queue(1)
        with self.__lock:
            self.__queues.append((keyword, queue, time() + 60))
            if not hasattr(self, '_TempEmail__th'):
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
                    delattr(self, '_TempEmail__th')
                    break
