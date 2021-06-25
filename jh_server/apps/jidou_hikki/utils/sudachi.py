from typing import List

import jaconv
import sudachipy
import unicodedata
from sudachipy import tokenizer, dictionary


def is_kanji(ch):
    return "CJK UNIFIED IDEOGRAPH" in unicodedata.name(ch)


def is_hiragana(ch):
    return "HIRAGANA" in unicodedata.name(ch)


def is_katakana(ch):
    return "KATAKANA" in unicodedata.name(ch)


def is_punctuation(ch):
    return not (is_kanji(ch) or is_hiragana(ch) or is_katakana(ch))


MODE_A = tokenizer.Tokenizer.SplitMode.A
MODE_B = tokenizer.Tokenizer.SplitMode.B
MODE_C = tokenizer.Tokenizer.SplitMode.C


class Token(object):
    _okurigana_template = "<ruby data-word-id={word_id}><rb>{surface}</rb><rp>(</rp><rt>{furigana}</rt><rp>)</rp>{okurigana}</ruby>"

    def __init__(self, morpheme: sudachipy.morpheme.Morpheme):
        self._token = morpheme
        self.kanji = None
        self.furigana = None
        self.okurigana = None
        self._split_okurigana()

    def __repr__(self):
        return self._token.surface()

    def __str__(self):
        return self._token.surface()

    def _split_okurigana(self):
        if self.contains_kanji():
            okurigana_reversed_idx = 0
            surface = self._token.surface()
            reading_form = jaconv.kata2hira(self._token.reading_form())
            for ch in reversed(surface):
                if is_kanji(ch):
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
            self.kanji = kanji
            self.okurigana = okurigana
            self.furigana = furigana

    @property
    def word_id(self):
        return f"sudachi__{self._token.word_id()}"

    @property
    def reading_form(self):
        return self._token.reading_form()

    @property
    def lemma(self):
        return self._token.dictionary_form()

    @property
    def meta(self):
        return self._token.part_of_speech()

    def as_html(self):
        if self.contains_kanji():
            return self._okurigana_template.format(
                word_id=self.word_id,
                surface=self.kanji,
                furigana=self.furigana,
                okurigana=self.okurigana,
            )
        return str(self)

    def contains_kanji(self):
        return any([is_kanji(ch) for ch in str(self)])

    def as_hiragana(self):
        return jaconv.kata2hira(self._token.reading_form())

    def as_katana(self):
        return jaconv.kata2hira(self._token.reading_form())

    def is_punctuation(self):
        ch = str(self)
        return len(ch) == 1 and not (is_kanji(ch) or is_hiragana(ch) or is_katakana(ch))


class Tokenizer(object):
    _tokenizer = dictionary.Dictionary().create()

    @classmethod
    def from_text(cls, sentence: str, split_mode: "SplitMode" = MODE_A) -> List[Token]:
        return [Token(token) for token in cls._tokenizer.tokenize(sentence, split_mode)]
