import re
import importlib


def get_tokenizer():
    from django.conf import settings

    tokenizer = getattr(
        settings,
        "TOKENIZER_CLASS",
        "jh_server.apps.jidou_hikki.analyzer.sudachi.SudachiTokenizer",
    )
    tokenizer = re.findall("(.*)\.(.*)$", tokenizer)
    assert tokenizer and len(tokenizer[0]) == 2
    pkg_name, cls_name = tokenizer[0]
    pkg = importlib.import_module(pkg_name)
    return getattr(pkg, cls_name)