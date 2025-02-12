import imghdr
import re
from base64 import b64decode
from io import BytesIO

import requests

from utils import cached, pip_install, read

re_code = re.compile(r'[\da-z]+', re.I)


@cached
def _DdddOcr():
    try:
        from ddddocr import DdddOcr
    except ModuleNotFoundError:
        pip_install('ddddocr')
        from ddddocr import DdddOcr
    return DdddOcr


@cached
def _PaddleOCR():
    try:
        from paddleocr import PaddleOCR
    except ModuleNotFoundError:
        pip_install('paddlepaddle', 'paddleocr')
        from paddleocr import PaddleOCR
    return PaddleOCR


@cached
def _Image():
    try:
        from PIL import Image
    except ModuleNotFoundError:
        pip_install('Pillow')
        from PIL import Image
    return Image


@cached
def _ocr_dddd_beta(): return _DdddOcr()(show_ad=False, beta=True)
@cached
def _ocr_dddd(): return _DdddOcr()(show_ad=False)
@cached
def _ocr_paddle_ch(): return _PaddleOCR()(show_log=False, use_angle_cls=True, lang='ch')
@cached
def _ocr_paddle_en(): return _PaddleOCR()(show_log=False, use_angle_cls=True, lang='en')


def to_png_if_gif(img: bytes):
    if imghdr.what(None, img) == 'gif':
        with _Image().open(img) as pim, BytesIO() as out:
            pim.save(out, 'png')
            img = out.getvalue()
    return img


def ocr_dddd(img: bytes):
    yield _ocr_dddd_beta().classification(img)
    yield _ocr_dddd().classification(img)


def ocr_paddle(img: bytes):
    img = to_png_if_gif(img)
    yield from (item[0] for item in _ocr_paddle_ch().ocr(img, det=False)[0])
    yield from (item[1][0] for item in _ocr_paddle_ch().ocr(img)[0])
    yield from (item[0] for item in _ocr_paddle_en().ocr(img, det=False)[0])
    yield from (item[1][0] for item in _ocr_paddle_en().ocr(img)[0])


def get_code(text: str):
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
    for fn in [ocr_dddd, ocr_paddle]:
        for text in fn(img):
            text = get_code(text)
            if text and text not in _set:
                yield text
                _set.add(text)
