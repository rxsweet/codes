__all__ = ['ocr_code_iter']

from utils import cached


def ocr_code_iter(img: str | bytes):
    return _get_fn_ocr_code_iter()(img)


@cached
def _get_fn_ocr_code_iter():
    try:
        from .ocr import ocr_code_iter
    except ModuleNotFoundError as e:
        if e.name != 'ddddocr':
            raise e
        from subprocess import run
        r = run(['pip', 'install', 'ddddocr'], capture_output=True, text=True)
        if r.returncode:
            raise Exception(r.stderr)
        from .ocr import ocr_code_iter
    return ocr_code_iter
