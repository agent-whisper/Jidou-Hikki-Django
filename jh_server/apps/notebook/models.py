from typing import Dict

from django.db import models, transaction
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth import get_user_model

from jh_server.services.logging import logger
from jh_server.services.tokenizer import DefaultTokenizer
from jh_server.services.tokenizer.schemas import PartOfSpeech
from jh_server.apps.wordcollection.models import Word, WordCollection

_User = get_user_model()


class Notebook(models.Model):
    owner = models.ForeignKey(_User, on_delete=models.CASCADE)
    title = models.CharField(max_length=256)
    description = models.CharField(max_length=512, default="")
    words = models.ManyToManyField(Word)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    @transaction.atomic
    def write_page(self, text: str) -> "Page":
        page = Page.objects.create(
            notebook=self,
            text=text,
        )
        if self.pages.count() > 1:
            last_ordering_val = self.pages.order_by("-ordering").first().ordering
            page.ordering = last_ordering_val + 100
        page.parse_text(save=False)
        self.register_page_words(page)
        page.save()
        return page

    @transaction.atomic
    def update_page(self, page: "Page", data: Dict) -> "Page":
        if page.notebook != self:
            raise ValueError("Cannot page from other notebook.")
        for key, val in data.items():
            if val is not None:
                setattr(page, key, val)
        page.parse_text(save=True)
        self.register_page_words(page)
        return page

    @transaction.atomic
    def register_all_words(self):
        for page in self.pages:
            for word in page.word_list:
                tokens = DefaultTokenizer.tokenize_text(word)
                for tkn in tokens:
                    WordCollection.objects.add_token(self.owner, tkn)

    @transaction.atomic
    def register_page_words(self, page: "Page"):
        for word in page.word_list:
            tokens = DefaultTokenizer.tokenize_text(word)
            for tkn in tokens:
                WordCollection.objects.add_token(self.owner, tkn)


class Page(models.Model):
    text = models.TextField()
    html = models.TextField()
    notebook = models.ForeignKey(
        Notebook, on_delete=models.CASCADE, related_name="pages"
    )
    word_list = models.JSONField(default=list, encoder=DjangoJSONEncoder)
    ordering = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    _included_pos = []

    def parse_text(self, *, save=True):
        lines = self.text.split("\n")
        html_lines = []
        word_tokens = []
        for line in lines:
            if line:
                tokens = DefaultTokenizer.tokenize_text(line.strip())
                for tkn in tokens:
                    html = [tkn.to_html() for tkn in tokens]
                    try:
                        pos = PartOfSpeech(tkn.part_of_speech)
                        if pos in PartOfSpeech.noteworthy_pos():
                            logger.debug(f"Including token {tkn} to word list.")
                            word_tokens.append(tkn.normalized_form)
                        else:
                            logger.debug(f"Skipping token {tkn} from word list")
                    except ValueError:
                        logger.warning(f"Unknown part-of-speech found: {tkn}")
                        print("")
                html_lines.append("".join(html))
        self.html = "<br>".join(html_lines)
        self.word_list = word_tokens
        if save:
            self.save()
