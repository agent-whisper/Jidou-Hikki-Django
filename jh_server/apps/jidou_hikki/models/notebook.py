from typing import Iterator

from django.db import models, transaction
from django.db.models import Q
from django.contrib.auth import get_user_model
from model_utils.models import TimeStampedModel

from .vocabulary import Vocabulary, UserFlashCard
from ..tokenizer import get_tokenizer

_TOKENIZER = get_tokenizer()
_USER_MODEL = get_user_model()


class Sentence(TimeStampedModel):
    text = models.TextField()
    html_template = models.TextField()
    vocabularies = models.ManyToManyField(Vocabulary)
    prev = models.ForeignKey(
        "Sentence",
        on_delete=models.SET_NULL,
        null=True,
        default=None,
        related_name="next_line",
    )
    next = models.ForeignKey(
        "Sentence",
        on_delete=models.SET_NULL,
        null=True,
        default=None,
        related_name="prev_line",
    )

    @transaction.atomic
    def set_next(self, sentence: "Sentence") -> None:
        if not self.next:
            self.next = sentence
            sentence.prev = self
            self.save()
            sentence.save()
        else:
            # Insert in the middle
            self.next.prev = sentence
            sentence.prev = self
            sentence.next = self.next
            self.next = sentence


class NotePageManager(models.Manager):
    @transaction.atomic
    def write_new_page(self, title, raw_text, notebook):
        page = self.model(title=title, text=raw_text, notebook=notebook)
        page.analyze()
        return page


class NotePage(TimeStampedModel):
    objects = NotePageManager()

    title = models.TextField()
    text = models.TextField()
    sentences = models.ManyToManyField(Sentence, related_name="page")
    html = models.TextField()
    vocabularies = models.ManyToManyField(Vocabulary)
    notebook = models.ForeignKey(
        "Notebook", on_delete=models.CASCADE, related_name="pages"
    )
    first_line = models.ForeignKey(
        Sentence,
        on_delete=models.SET_NULL,
        null=True,
        default=None,
        related_name="first_line_of",
    )
    last_line = models.ForeignKey(
        Sentence,
        on_delete=models.SET_NULL,
        null=True,
        default=None,
        related_name="last_line_of",
    )

    def __str__(self):
        return f"({self.notebook.title}) {self.title}"

    class Meta:
        unique_together = ("title", "notebook")

    @transaction.atomic
    def write_append(self, text: str) -> Sentence:
        tokens = _TOKENIZER.tokenize_text(text)
        html = []
        vocabularies = []
        for tkn in tokens:
            if tkn.contains_kanji():
                vocabs = Vocabulary.objects.update_or_create_from_token(tkn)
                for vocab in vocabs:
                    UserFlashCard.objects.get_or_create(
                        owner=self.notebook.owner, vocabulary=vocab
                    )
                vocabularies += vocabs
                html.append(f"{{{tkn.word_id}}}")
            else:
                html.append(tkn.word)
        new_sentence = Sentence.objects.create(text=text, html_template=" ".join(html))
        new_sentence.vocabularies.set(vocabs)
        if not (self.first_line and self.last_line):
            self.first_line = new_sentence
            self.last_line = new_sentence
        else:
            self.last_line.set_next(new_sentence)
            self.last_line = new_sentence
        self.save()
        return new_sentence

    @transaction.atomic
    def analyze(self):
        lines = self.text.split("\n")
        html_lines = []
        vocabularies = []
        for line in lines:
            if line:
                tokens = _TOKENIZER.tokenize_text(line.strip())
                for tkn in tokens:
                    if tkn.contains_kanji():
                        vocabs = Vocabulary.objects.update_or_create_from_token(tkn)
                        for vocab in vocabs:
                            UserFlashCard.objects.get_or_create(
                                owner=self.notebook.owner, vocabulary=vocab
                            )
                        vocabularies += vocabs
                html = [tkn.as_html() for tkn in tokens]
                html_lines.append("".join(html))
        self.html = "<br>".join(html_lines)
        self.save()
        self.vocabularies.set(vocabularies)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(first_line__isnull=True, last_line__isnull=True)
                | Q(first_line__isnull=False, last_line__isnull=False),
                name="cc_notepage_first_last_line_match",
            )
        ]

    @property
    def is_empty(self):
        return not (self.first_line and self.last_line)

    def read_contents(self) -> Iterator[Sentence]:
        if self.is_empty:
            return
        sentence = self.first_line
        yield sentence
        while sentence.next:
            sentence = sentence.next
            yield sentence
        return


class Notebook(TimeStampedModel):
    owner = models.ForeignKey(_USER_MODEL, on_delete=models.CASCADE)
    title = models.TextField()
    description = models.TextField(default="")

    def __str__(self):
        return self.title

    def add_page(self, title, raw_text):
        return NotePage.objects.write_new_page(title, raw_text, self)
