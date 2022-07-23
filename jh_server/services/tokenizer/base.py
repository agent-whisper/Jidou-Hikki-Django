from abc import ABC, abstractmethod
from typing import List, Any
from .schemas import Token


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
    def normalize_token(cls, token: Token, *args, **kwargs) -> Token:
        """Create a normalized token from input token (i.e. dictionary form)."""
        raise NotImplementedError
