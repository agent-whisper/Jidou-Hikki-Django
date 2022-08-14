from enum import Enum

from pydantic import BaseModel

from . import utils


class PartOfSpeech(str, Enum):
    DOUSHI = "動詞"  # verb
    MEISHI = "名詞"  # noun
    DAIMEISHI = "代名詞"  # pronoun
    KEIYOUSHI = "形容詞"  # i-adjective
    KEIJOUSHI = "形状詞"  # na-adjective
    JODOUSHI = "助動詞"  # inflecting dependent word
    JOUSHI = "助詞"  # particle
    FUKUSHI = "副詞"  # adverb
    KUUHAKU = "空白"  # whitespace
    RENTAISHI = "連体詞"  # pre-noun adjectival
    HOJOKIGOU = "補助記号"  # number and punctuations
    KANDOUSHI = "感動詞"  # interjection
    SETSUBISHI = "接尾辞"  # suffix
    SETSUZOKUSHI = "接続詞"  # conjunction

    @classmethod
    def noteworthy_pos(cls):
        return [
            cls.DOUSHI,
            cls.MEISHI,
            cls.DAIMEISHI,
            cls.KEIJOUSHI,
            cls.KEIYOUSHI,
            cls.SETSUZOKUSHI,
        ]


class Token(BaseModel):
    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.word}({self.part_of_speech})>"

    def __str__(self):
        return f"{self.word}({self.part_of_speech})"

    word: str
    word_id: str
    reading_form: str
    normalized_form: str
    lemma: str
    part_of_speech: str
    kanji: str = ""
    furigana: str = ""
    okurigana: str = ""

    @property
    def only_contains_japanese_chars(self):
        return utils.check_only_japanese_chars(self.word)

    @property
    def contains_kanji(self):
        return utils.check_contains_kanji(self.word)

    @property
    def hiragana(self):
        return utils.to_hiragana(self.reading_form)

    @property
    def katakana(self):
        return utils.to_katakana(self.reading_form)

    @property
    def is_punctuation(self):
        ch = self.word
        return len(ch) == 1 and not utils.is_punctuation(ch)

    def to_html(self):
        if self.contains_kanji:
            return utils.write_kanji_html(
                self.word_id, self.kanji, self.furigana, self.okurigana
            )
        else:
            return utils.write_normal_html(self.word)
