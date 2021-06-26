from django.db import models, transaction
from django.contrib.auth import get_user_model
from model_utils.models import TimeStampedModel

from .vocabulary import Vocabulary, UserFlashCard
from ..tokenizer import get_tokenizer

_TOKENIZER = get_tokenizer()
_USER_MODEL = get_user_model()


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
                tokens = _TOKENIZER.tokenize_text(line.strip())
                for tkn in tokens:
                    if tkn.contains_kanji():
                        vocab, _ = Vocabulary.objects.update_or_create_from_token(tkn)
                        UserFlashCard.objects.get_or_create(
                            owner=self.notebook.owner, vocabulary=vocab
                        )
                        vocabularies.append(vocab)
                html = [tkn.as_html() for tkn in tokens]
                html_lines.append("".join(html))
        self.html = "<br>".join(html_lines)
        self.save()
        self.vocabularies.set(vocabularies)


class Notebook(TimeStampedModel):
    owner = models.ForeignKey(_USER_MODEL, on_delete=models.CASCADE)
    title = models.TextField()
    description = models.TextField(default="")

    def __str__(self):
        return self.title

    def add_page(self, title, raw_text):
        return NotePage.objects.write_new_page(title, raw_text, self)
