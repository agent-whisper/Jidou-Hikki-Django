from typing import Type
import re
import importlib

from .base import Tokenizer


def get_tokenizer() -> Type[Tokenizer]:
    from django.conf import settings

    tokenizer = settings.TOKENIZER_CLASS
    tokenizer = re.findall("(.*)\.(.*)$", tokenizer)
    assert tokenizer and len(tokenizer[0]) == 2
    pkg_name, cls_name = tokenizer[0]
    pkg = importlib.import_module(pkg_name)
    return getattr(pkg, cls_name)


DefaultTokenizer = get_tokenizer()
