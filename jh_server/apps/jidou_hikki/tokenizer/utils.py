import unicodedata


def is_kanji(ch):
    return "CJK UNIFIED IDEOGRAPH" in unicodedata.name(ch)


def is_hiragana(ch):
    return "HIRAGANA" in unicodedata.name(ch)


def is_katakana(ch):
    return "KATAKANA" in unicodedata.name(ch)


def is_punctuation(ch):
    return not (is_kanji(ch) or is_hiragana(ch) or is_katakana(ch))
