from typing import List

import jaconv
import sudachipy
from sudachipy import tokenizer, dictionary

from . import utils
from .base import Token, Tokenizer


MODE_A = tokenizer.Tokenizer.SplitMode.A
MODE_B = tokenizer.Tokenizer.SplitMode.B
MODE_C = tokenizer.Tokenizer.SplitMode.C


class SudachiToken(Token):
    _html_template = "<ruby data-word-id={word_id}><rb>{surface}</rb><rp>(</rp><rt>{furigana}</rt><rp>)</rp>{okurigana}</ruby>"

    def __init__(self, morpheme: sudachipy.morpheme.Morpheme):
        self._token = morpheme
        self.kanji = None
        self.furigana = None
        self.okurigana = None
        self._split_okurigana()

    def _split_okurigana(self):
        if self.contains_kanji():
            okurigana_reversed_idx = 0
            surface = self._token.surface()
            reading_form = jaconv.kata2hira(self._token.reading_form())
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
            self.kanji = kanji
            self.okurigana = okurigana
            self.furigana = furigana

    @property
    def word(self):
        return self._token.surface()

    @property
    def word_id(self):
        return f"sudachi__{self._token.word_id()}"

    @property
    def reading_form(self):
        return self._token.reading_form()

    @property
    def normalized_form(self):
        return self._token.normalized_form()

    @property
    def lemma(self):
        return self._token.dictionary_form()

    @property
    def part_of_speech(self):
        return self._token.part_of_speech()

    def as_html(self):
        if self.contains_kanji():
            return self._html_template.format(
                word_id=self.word_id,
                surface=self.kanji,
                furigana=self.furigana,
                okurigana=self.okurigana,
            )
        return str(self)


class SudachiTokenizer(Tokenizer):
    _tokenizer = dictionary.Dictionary().create()

    @classmethod
    def from_text(
        cls,
        sentence: str,
        split_mode: "sudachipy.tokenizer.Tokenizer.SplitMode" = MODE_A,
    ) -> List[SudachiToken]:
        return [
            SudachiToken(token)
            for token in cls._tokenizer.tokenize(sentence, split_mode)
        ]

    @classmethod
    def normalize(
        cls,
        token: Token,
        split_mode: "sudachipy.tokenizer.Tokenizer.SplitMode" = MODE_A,
    ) -> SudachiToken:
        tokens = cls._tokenizer.tokenize(token.normalized_form, split_mode)
        if len(tokens) == 1:
            return SudachiToken(tokens[0])
        raise ValueError(f"Cannot normalize {token}")