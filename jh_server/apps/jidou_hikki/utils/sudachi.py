from abc import ABC, abstractmethod, abstractstaticmethod
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


class Token(ABC):
    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.word}>"

    def __str__(self):
        return self.word

    @property
    @abstractmethod
    def word(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def word_id(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def reading_form(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def lemma(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def reading_form(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def normalized_form(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def part_of_speech(self):
        raise NotImplementedError

    @abstractmethod
    def as_html(self):
        raise NotImplementedError

    def contains_kanji(self):
        return any([is_kanji(ch) for ch in self.word])

    def as_hiragana(self):
        return jaconv.kata2hira(self.reading_form)

    def as_katana(self):
        return jaconv.kata2hira(self.reading_form)

    def is_punctuation(self):
        ch = self.word
        return len(ch) == 1 and not (is_kanji(ch) or is_hiragana(ch) or is_katakana(ch))


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


class Tokenizer(ABC):
    @classmethod
    @abstractmethod
    def from_text(cls, sentence: str, *args, **kwargs) -> List[Token]:
        """
        Tokenize a sentence into a list of tokens.
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def normalize(cls, token: Token, *args, **kwargs) -> Token:
        """Create a normalized token from input token (i.e. dictionary form)."""
        raise NotImplementedError


class SudachiTokenizer(Tokenizer):
    _tokenizer = dictionary.Dictionary().create()

    @classmethod
    def from_text(
        cls, sentence: str, split_mode: "SplitMode" = MODE_A
    ) -> List[SudachiToken]:
        return [
            SudachiToken(token)
            for token in cls._tokenizer.tokenize(sentence, split_mode)
        ]

    @classmethod
    def normalize(cls, token: Token, split_mode: "SplitMode" = MODE_A) -> SudachiToken:
        tokens = cls._tokenizer.tokenize(token.normalized_form, split_mode)
        if len(tokens) == 1:
            return SudachiToken(tokens[0])
        raise ValueError(f"Cannot normalize {token}")