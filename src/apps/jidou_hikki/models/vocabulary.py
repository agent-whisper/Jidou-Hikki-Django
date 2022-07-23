import math
import logging
from typing import List
from datetime import timedelta

import jamdict
from jamdict import Jamdict
from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from model_utils.models import TimeStampedModel
from model_utils.choices import Choices
from django.contrib.auth import get_user_model

from src.services.tokenizer import DefaultTokenizer
from src.services.tokenizer.base import Token
from src.services.dictionary import DefaultJisho

logger = logging.getLogger("root")
_User = get_user_model()

MASTERY = Choices("new", "learning", "acquired")


def calc_repetition_interval(iteration: int, easiness_factor: float) -> int:
    if iteration == 1:
        return 1
    elif iteration == 2:
        return 6
    else:
        return math.ceil(
            calc_repetition_interval(iteration - 1, easiness_factor) * easiness_factor
        )


def calc_new_easiness_factor(old_ef: float, ans_quality: int) -> float:
    ef = old_ef - 0.8 + 0.28 * ans_quality - 0.02 * ans_quality
    if ef < 1.3:
        ef = 1.3
    elif ef > 2.5:
        ef = 2.5
    return ef


class UserFlashCardManager(models.Manager):
    def get_new_cards(self, owner: AbstractUser, limit: int = None) -> QuerySet:
        """Query UserFlashCard with `new` mastery level, ordered by the created time.

        :param owner: Reference to the cards owner.
        :param limit: How many cards to be returned.
        """
        queryset = self.filter(owner=owner, mastery=MASTERY.new).order_by("created")
        if limit:
            return queryset[:limit]
        return queryset

    def get_learning_cards(self, owner: AbstractUser, limit: int = None) -> QuerySet:
        """Query UserFlashCard with `learning` mastery level, ordered by the earliest next review schedule.

        :param owner: Reference to the cards owner.
        :param limit: How many cards to be returned.
        """
        queryset = self.filter(owner=owner, mastery=MASTERY.learning).order_by(
            "next_review_time"
        )
        if limit:
            return queryset[:limit]
        return queryset

    def get_acquired_cards(self, owner: AbstractUser, limit: int = None) -> QuerySet:
        """Query UserFlashCard with `acquired` mastery level, ordered by the latest last review schedule.

        :param owner: Reference to the cards owner.
        :param limit: How many cards to be returned.
        """
        queryset = self.filter(owner=owner, mastery=MASTERY.acquired).order_by(
            "-last_review_time"
        )
        if limit:
            return queryset[:limit]
        return queryset


class UserFlashCard(TimeStampedModel):
    objects = UserFlashCardManager()

    owner = models.ForeignKey(_User, on_delete=models.CASCADE, related_name="cards")
    vocabulary = models.ForeignKey("Vocabulary", on_delete=models.CASCADE)
    mastery = models.CharField(max_length=64, choices=MASTERY, default=MASTERY.new)
    last_review_time = models.DateTimeField(null=True, default=None)
    next_review_time = models.DateTimeField(null=True, default=None)
    easiness_factor = models.FloatField(default=2.5)
    review_iteration = models.IntegerField(default=1)

    class Meta:
        unique_together = ("user", "vocabulary")

    def __str__(self):
        return f"({self.owner.username}: {self.mastery}) {self.vocabulary}"

    class Meta:
        ordering = ["vocabulary__dict_id"]

    def update_review_stats(self, answer_quality: int) -> None:
        """
        Update repetition_interval and easiness_factor after a review.

        :param answer_quality: An intenger in range of [0, 5] (higher is better)
        """
        if answer_quality not in range(0, 6):
            raise ValueError("Answer quality must be in range of [0, 5].")

        if self.mastery == MASTERY.new:
            self.mastery = MASTERY.learning
        if answer_quality < 3:
            self.review_iteration = 1
        else:
            self.review_iteration += 1
            self.easiness_factor = calc_new_easiness_factor(
                self.easiness_factor, answer_quality
            )
        next_interval = calc_repetition_interval(
            self.review_iteration, self.easiness_factor
        )
        curr_time = timezone.now()
        self.last_review_time = curr_time
        self.next_review_time = self.last_review_time + timedelta(days=next_interval)

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)


class TokenIndex(TimeStampedModel):
    vocabulary = models.ForeignKey("Vocabulary", on_delete=models.CASCADE)
    token_id = models.TextField(unique=True)

    def __str__(self):
        return self.token_id


class VocabularyManager(models.Manager):
    def update_or_create_from_token(self, token: Token) -> List["Vocabulary"]:
        # Check if token has been indexed before
        vocabs = []
        if TokenIndex.objects.filter(token_id=token.word_id).exists():
            vocabs.append(TokenIndex.objects.get(token_id=token.word_id).vocabulary)
        else:
            normalized_tokens = DefaultTokenizer.normalize_token(token)
            for normalized_tkn in normalized_tokens:
                # Assume the first entry to be the best match
                jmd_info = DefaultJisho.lookup_token(normalized_tkn)
                if len(jmd_info.entries) > 0:
                    # Some tokens may be a set of expressions, and not available in
                    # JMDict. Example cases:
                    #   -  キャラ作り
                    jmd_entry = jmd_info.entries[0]
                    vocab, _ = self.update_or_create(
                        dict_id=jmd_entry.idseq,
                        defaults={
                            "word": normalized_tkn.word,
                            "kanji": normalized_tkn.kanji,
                            "furigana": normalized_tkn.furigana,
                            "okurigana": normalized_tkn.okurigana,
                            "reading": normalized_tkn.reading_form,
                        },
                    )
                    # Index normalized token for future lookup
                    TokenIndex.objects.update_or_create(
                        token_id=normalized_tkn.word_id, vocabulary=vocab
                    )
                    vocabs.append(vocab)
                else:
                    logger.error(f"No JMDict entries for {normalized_tkn}.")
        return vocabs


class Vocabulary(TimeStampedModel):
    _reading_template = "{first}{second}"

    objects = VocabularyManager()

    dict_id = models.IntegerField()
    word = models.TextField()
    reading = models.TextField()
    kanji = models.TextField(null=True)
    furigana = models.TextField(null=True)
    okurigana = models.TextField(null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._jmd_lookup = None

    def __str__(self):
        return f"{self.word}"

    def as_token(self) -> Token:
        token = DefaultTokenizer.tokenize_text(self.word)
        return token[0] if token else None

    def as_html(self) -> str:
        token = self.as_token()
        return token.as_html() if token else ""

    @property
    def jmdict(self) -> jamdict.util.LookupResult:
        if not self._jmd_lookup:
            self._jmd_lookup = DefaultJisho.lookup(f"id#{self.dict_id}")
        return self._jmd_lookup

    def as_text(self) -> str:
        if self.kanji:
            return self._reading_template.format(
                first=self.furigana,
                second=("." + self.okurigana) if self.okurigana else "",
            )
        return self.word


class Translation(TimeStampedModel):
    vocabulary = models.ForeignKey(Vocabulary, on_delete=models.CASCADE)
    translation = models.TextField()
    lang = models.CharField(max_length=8)
