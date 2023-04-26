import re
from base64 import b64decode

import requests
from ddddocr import DdddOcr

from utils import cached, read

re_code = re.compile(r'[\da-z]+', re.I)


@cached
def _ocr_dddd_beta(): return DdddOcr(show_ad=False, beta=True)
@cached
def _ocr_dddd(): return DdddOcr(show_ad=False)


def ocr_dddd(img):
    yield _ocr_dddd_beta().classification(img)
    yield _ocr_dddd().classification(img)


def get_code(text):
    return ''.join(re_code.findall(text)).lower()


def ocr_code_iter(img: str | bytes):
    if isinstance(img, str):
        if img.startswith('data:'):
            img = b64decode(img.split(',', 1)[1])
        elif img.startswith(('http:', 'https:')):
            img = requests.get(img).content
        else:
            img = read(img, b=True)
    _set = set()
    for fn in [ocr_dddd]:
        for text in fn(img):
            text = get_code(text)
            if text and text not in _set:
                yield text
                _set.add(text)
