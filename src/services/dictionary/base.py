from abc import ABC, abstractclassmethod
from typing import List


from .schemas import Entry
from src.services.tokenizer.base import Token, Tokenizer
from src.services.tokenizer.sudachi import SudachiTokenizer


class AbstractJisho(ABC):
    _tokenizer: Tokenizer = SudachiTokenizer()

    @classmethod
    def lookup_token(cls, token: Token, **kwargs) -> List[Entry]:
        return cls.lookup(token.normalized_form, **kwargs)

    @abstractclassmethod
    def lookup(cls, word: str, **kwargs) -> List[Entry]:
        raise NotImplementedError
