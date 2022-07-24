from enum import Enum
from typing import Tuple

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser

from src.services.tokenizer.schemas import Token

_User = get_user_model()


class WordStatus(str, Enum):
    NEW = "new"
    LEARNED = "learned"


class WordCollectionManager(models.Manager):
    # TODO: Find a way to do batch upsert
    def add_token(self, user: AbstractUser, token: Token) -> None:
        word, _ = Word.objects.from_token(token)
        self.add_word(user, word)

    def add_word(self, user: AbstractUser, word: "Word") -> None:
        self.get_or_create(user=user, word=word)


class WordCollection(models.Model):
    objects: WordCollectionManager = WordCollectionManager()

    def __repr__(self) -> str:
        return f"<WordCollection: {self.user.username} - {self.word}>"

    user = models.ForeignKey(_User, on_delete=models.CASCADE)
    word = models.ForeignKey("Word", on_delete=models.CASCADE)
    status = models.CharField(max_length=64, default=WordStatus.NEW.value)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["user", "word"]


class WordManager(models.Manager):
    def from_token(self, token: Token) -> Tuple["Word", bool]:
        """Get or create a word entry based on word_id."""
        return self.get_or_create(word_id=token.word_id, defaults=token.dict())


class Word(models.Model):
    objects: WordManager = WordManager()

    word = models.CharField(max_length=512)
    word_id = models.CharField(max_length=64, unique=True)
    reading_form = models.CharField(max_length=512)
    normalized_form = models.CharField(max_length=512)
    lemma = models.CharField(max_length=512)
    part_of_speech = models.CharField(max_length=32)
    kanji = models.CharField(max_length=256)
    furigana = models.CharField(max_length=256)
    okurigana = models.CharField(max_length=256)

    def __repr__(self) -> str:
        return f"<Word({self.word_id}): {self.word}>"

    def __str__(self) -> str:
        return self.normalized_form

    def to_token(self) -> Token:
        return Token(
            word=self.word,
            word_id=self.word_id,
            reading_form=self.reading_form,
            normalized_form=self.normalized_form,
            lemma=self.lemma,
            part_of_speech=self.part_of_speech,
            kanji=self.kanji,
            furigana=self.furigana,
            okurigana=self.okurigana,
        )
