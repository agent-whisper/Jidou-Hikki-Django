import jaconv
import unicodedata


def check_contains_kanji(word: str) -> bool:
    return any([is_kanji(ch) for ch in word])


def to_hiragana(word: str) -> str:
    return jaconv.kata2hira(word)


def to_katakana(word: str) -> str:
    return jaconv.kata2hira(word)


def write_normal_html(word: str):
    return f"<span>{word}</span>"


def write_kanji_html(word_id: str, kanji: str, furigana: str, okurigana: str) -> str:
    return f"<span><ruby data-word-id={word_id}><rb>{kanji}</rb><rp>(</rp><rt>{furigana}</rt><rp>)</rp></ruby>{okurigana}</span>"


def is_kanji(ch) -> bool:
    return "CJK UNIFIED IDEOGRAPH" in unicodedata.name(ch)


def is_hiragana(ch) -> bool:
    return "HIRAGANA" in unicodedata.name(ch)


def is_katakana(ch) -> bool:
    return "KATAKANA" in unicodedata.name(ch)


def is_punctuation(ch) -> bool:
    return not (is_kanji(ch) or is_hiragana(ch) or is_katakana(ch))
