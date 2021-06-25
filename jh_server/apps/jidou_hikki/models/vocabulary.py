import math
from datetime import timedelta

from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone
from model_utils.models import TimeStampedModel
from model_utils.choices import Choices
from django.contrib.auth import get_user_model

from ..analyzer import get_tokenizer
from ..analyzer.base import Token

_TOKENIZER = get_tokenizer()
_USER_MODEL = get_user_model()

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
    def get_new_cards(self, limit: int = None) -> QuerySet:
        """Query UserFlashCard with `new` mastery level, ordered by the created time.

        :param limit: How many cards to be returned.
        """
        self.filter(mastery=MASTERY.new).order_by("created")

    def get_learning_cards(self, limit: int = None) -> QuerySet:
        """Query UserFlashCard with `learning` mastery level, ordered by the earliest next review schedule.

        :param limit: How many cards to be returned.
        """
        self.filter(mastery=MASTERY.learning).order_by("next_review_time")

    def get_acquired_cards(self, limit: int = None) -> QuerySet:
        """Query UserFlashCard with `acquired` mastery level, ordered by the latest last review schedule.

        :param limit: How many cards to be returned.
        """
        self.filter(mastery=MASTERY.acquired).order_by("-last_review_time")


class UserFlashCard(TimeStampedModel):
    objects = UserFlashCardManager()

    owner = models.ForeignKey(
        _USER_MODEL, on_delete=models.CASCADE, related_name="cards"
    )
    vocabulary = models.ForeignKey("Vocabulary", on_delete=models.CASCADE)
    mastery = models.CharField(max_length=64, choices=MASTERY, default=MASTERY.learning)
    last_review_time = models.DateTimeField(null=True, default=None)
    next_review_time = models.DateTimeField(null=True, default=None)
    easiness_factor = models.FloatField(default=2.5)
    review_iteration = models.IntegerField(default=1)

    class Meta:
        unique_together = ("user", "vocabulary")

    def __str__(self):
        return f"({self.user.username}: {self.mastery}) {self.vocabulary}"

    class Meta:
        ordering = ["vocabulary__word_id"]

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


class VocabularyManager(models.Manager):
    def update_or_create_from_token(self, token: Token) -> "Vocabulary":
        return self.update_or_create(
            word_id=token.word_id,
            defaults={
                "word": token.lemma,
                "kanji": token.kanji,
                "furigana": token.furigana,
                "okurigana": token.okurigana,
                "reading": token.reading_form,
                "part_of_speech": token.part_of_speech,
            },
        )


class Vocabulary(TimeStampedModel):
    _reading_template = "{first}{second}"

    objects = VocabularyManager()

    word_id = models.TextField(unique=True)
    word = models.TextField()
    reading = models.TextField()
    kanji = models.TextField()
    furigana = models.TextField()
    okurigana = models.TextField()
    part_of_speech = models.JSONField()

    def __str__(self):
        return f"{self.word_id}: {self.word}"

    def as_token(self):
        token = _TOKENIZER.tokenize_text(self.word)
        return token[0] if token else None

    def as_html(self):
        token = self.as_token()
        return token.as_html() if token else ""

    def as_text(self):
        if self.kanji:
            return self._reading_template.format(
                first=self.furigana,
                second=("." + self.okurigana) if self.okurigana else "",
            )
        return self.word


class EnglishTranslation(TimeStampedModel):
    jp_word = models.ForeignKey(Vocabulary, on_delete=models.CASCADE)
    translation = models.TextField()
