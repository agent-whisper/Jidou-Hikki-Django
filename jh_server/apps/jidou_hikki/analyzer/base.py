from abc import ABC, abstractmethod
from typing import List

import jaconv

from . import utils


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
        return any([utils.is_kanji(ch) for ch in self.word])

    def as_hiragana(self):
        return jaconv.kata2hira(self.reading_form)

    def as_katana(self):
        return jaconv.kata2hira(self.reading_form)

    def is_punctuation(self):
        ch = self.word
        return len(ch) == 1 and not (
            utils.is_kanji(ch) or utils.is_hiragana(ch) or utils.is_katakana(ch)
        )


class Tokenizer(ABC):
    @classmethod
    @abstractmethod
    def tokenize_text(cls, sentence: str, *args, **kwargs) -> List[Token]:
        """
        Tokenize a sentence into a list of tokens.
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def normalize(cls, token: Token, *args, **kwargs) -> Token:
        """Create a normalized token from input token (i.e. dictionary form)."""
        raise NotImplementedError
