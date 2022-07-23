from enum import Enum
from typing import List, Tuple

from sudachipy import tokenizer, dictionary
import sudachipy

from . import utils
from .base import Tokenizer
from .schemas import Token


class SudachiSplitMode(Enum):
    MODE_A = tokenizer.Tokenizer.SplitMode.A
    MODE_B = tokenizer.Tokenizer.SplitMode.B
    MODE_C = tokenizer.Tokenizer.SplitMode.C


class SudachiTokenizer(Tokenizer):
    _tokenizer = dictionary.Dictionary(dict_type="full").create()

    @classmethod
    def tokenize_text(
        cls,
        sentence: str,
        split_mode: SudachiSplitMode = SudachiSplitMode.MODE_C,
    ) -> List[Token]:
        return [
            cls._wrap_morpheme(morpheme)
            for morpheme in cls._tokenizer.tokenize(sentence, split_mode)
        ]

    @classmethod
    def normalize_token(
        cls,
        token: Token,
        split_mode: SudachiSplitMode = SudachiSplitMode.MODE_C,
    ) -> List[Token]:
        morphemes = cls._tokenizer.tokenize(token.normalized_form, split_mode)
        return [cls._wrap_morpheme(morpheme) for morpheme in morphemes]

    @classmethod
    def _wrap_morpheme(cls, morpheme: sudachipy.morpheme.Morpheme) -> Token:
        kanji, furigana, okurigana = cls._parse_kanji_furigana_okurigana(morpheme)
        return Token(
            word=morpheme.surface(),
            word_id=f"sudachi__{morpheme.word_id()}",
            reading_form=morpheme.reading_form(),
            normalized_form=morpheme.normalized_form(),
            lemma=morpheme.dictionary_form(),
            part_of_speech=morpheme.part_of_speech()[0],
            kanji=kanji,
            furigana=furigana,
            okurigana=okurigana,
        )

    @staticmethod
    def _parse_kanji_furigana_okurigana(
        morpheme: sudachipy.morpheme.Morpheme,
    ) -> Tuple[str, str, str]:
        word = morpheme.surface()
        reading_form = utils.to_katakana(morpheme.reading_form())
        if utils.check_contains_kanji(word):
            okurigana_reversed_idx = 0
            for ch in reversed(word):
                if utils.is_kanji(ch):
                    break
                okurigana_reversed_idx += 1

            if okurigana_reversed_idx > 0:
                kanji = word[: 0 - okurigana_reversed_idx]
                okurigana = reading_form[len(reading_form) - okurigana_reversed_idx :]
                furigana = reading_form[: len(reading_form) - okurigana_reversed_idx]
            else:
                # Whole word consists of kanji
                kanji = word
                okurigana = ""
                furigana = reading_form
        else:
            kanji = ""
            furigana = ""
            okurigana = ""
        return kanji, furigana, okurigana
