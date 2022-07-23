from typing import Dict

from jamdict import Jamdict
from jamdict.jmdict import JMDEntry

from .base import AbstractJisho
from .schemas import Entry


class JamdictJisho(AbstractJisho):
    _jisho = Jamdict()

    @classmethod
    def lookup(cls, word: str, **kwargs):
        result = cls._jisho.lookup(word, **kwargs)
        return [cls._wrap_jmdict_entry(entry) for entry in result.entries]

    @staticmethod
    def _wrap_jmdict_entry(entry: JMDEntry) -> Entry:
        return Entry(
            kana_forms=entry.kana_forms,
            kanji_forms=entry.kanji_forms,
            translations=[str(sense) for sense in entry.senses],
        )
