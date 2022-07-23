from typing import List

from pydantic import BaseModel


class Entry(BaseModel):
    kanji_forms: List[str]
    kana_forms: List[str]
    translations: List[str]
