import io
from typing import Tuple

import jaconv
import sudachipy
import unicodedata
from sudachipy import tokenizer, dictionary


def process_token(token: sudachipy.morpheme.Morpheme) -> str:
    surface = token.surface()
    if any([utils.is_kanji(ch) for ch in surface]):
        kanji, furigana, okurigana, meta = process_okurigana(token)
        return f"<ruby><div data-word-id={meta.get('word_id')} onclick='toggleFurigana(this);'><rb>{kanji}</rb><rt>{furigana}</rt></div>{okurigana}</ruby>"
    else:
        return "{0}".format(surface, end="")


def process_okurigana(token: sudachipy.morpheme.Morpheme) -> Tuple[str, str, str]:
    okurigana_reversed_idx = 0
    surface = token.surface()
    reading_form = jaconv.kata2hira(token.reading_form())
    attributes = {
        "word_id": token.word_id(),
        "dictionary_form": token.dictionary_form(),
        "reading_form": reading_form,
    }
    for ch in reversed(surface):
        if utils.is_kanji(ch):
            break
        okurigana_reversed_idx += 1
    if okurigana_reversed_idx == 0:
        kanji = surface
        okurigana = ""
        furigana = reading_form
    else:
        kanji = surface[: 0 - okurigana_reversed_idx]
        okurigana = reading_form[len(reading_form) - okurigana_reversed_idx :]
        furigana = reading_form[: len(reading_form) - okurigana_reversed_idx]
    return (kanji, furigana, okurigana, attributes)