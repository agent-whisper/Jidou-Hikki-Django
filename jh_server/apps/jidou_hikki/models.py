from django.db import models, transaction
from django.contrib.auth.models import AbstractUser
from model_utils.choices import Choices
from model_utils.models import TimeStampedModel

from .utils.sudachi import Token, Tokenizer

MASTERY = Choices("new", "seen", "acquired")


class JidouHikkiUser(AbstractUser):
    pass


class UserVocabulary(TimeStampedModel):
    user = models.ForeignKey(
        JidouHikkiUser, on_delete=models.CASCADE, related_name="word_bank"
    )
    vocabulary = models.ForeignKey("Vocabulary", on_delete=models.CASCADE)
    mastery = models.CharField(max_length=64, choices=MASTERY, default=MASTERY.new)

    class Meta:
        unique_together = ("user", "vocabulary")

    def __str__(self):
        return f"({self.user.username}: {self.mastery}) {self.vocabulary}"

    class Meta:
        ordering = ["vocabulary__word_id"]


class VocabularyManager(models.Manager):
    def update_or_create_from_token(self, token: Token) -> "Vocabulary":
        return self.update_or_create(
            word_id=token.word_id,
            defaults={
                "word": token.lemma,
                "kanji": token.kanji,
                "furigana": token.furigana,
                "okurigana": token.okurigana,
            },
        )


class Vocabulary(TimeStampedModel):
    _reading_template = "{first}{second}"

    objects = VocabularyManager()

    word_id = models.IntegerField(unique=True)
    word = models.TextField(unique=True)
    kanji = models.TextField(null=True)
    furigana = models.TextField(null=True)
    okurigana = models.TextField(null=True)

    def __str__(self):
        return f"{self.word_id}: {self.word}"

    def reading_html(self):
        if self.kanji:
            return self._reading_template.format(
                first=self.furigana,
                second=("." + self.okurigana) if self.okurigana else "",
            )
        return self.word


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
    html = models.TextField()
    vocabularies = models.ManyToManyField(Vocabulary)
    notebook = models.ForeignKey(
        "Notebook", on_delete=models.CASCADE, related_name="pages"
    )

    def __str__(self):
        return f"({self.notebook.title}) {self.title}"

    class Meta:
        unique_together = ("title", "notebook")

    @transaction.atomic
    def analyze(self):
        lines = self.text.split("\n")
        html_lines = []
        vocabularies = []
        for line in lines:
            if line:
                tokens = Tokenizer.from_text(line.strip())
                for tkn in tokens:
                    if tkn.contains_kanji():
                        vocab, _ = Vocabulary.objects.update_or_create_from_token(tkn)
                        UserVocabulary.objects.get_or_create(
                            user=self.notebook.owner, vocabulary=vocab
                        )
                        vocabularies.append(vocab)
                html = [tkn.as_html() for tkn in tokens]
                html_lines.append("".join(html))
        self.html = "<br>".join(html_lines)
        self.save()
        self.vocabularies.set(vocabularies)


class Notebook(TimeStampedModel):
    owner = models.ForeignKey(JidouHikkiUser, on_delete=models.CASCADE)
    title = models.TextField()
    description = models.TextField(default="")

    def __str__(self):
        return self.title

    def add_page(self, title, raw_text):
        return NotePage.objects.write_new_page(title, raw_text, self)
