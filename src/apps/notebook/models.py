from typing import Dict, List

from django.db import models, transaction
from django.contrib.auth import get_user_model
from pydantic import BaseModel

from src.services.logging import logger
from src.services.tokenizer import DefaultTokenizer
from src.services.tokenizer.schemas import PartOfSpeech
from src.apps.wordcollection.models import Word, WordCollection

_User = get_user_model()


class WordToken(BaseModel):
    word: str
    word_id: str

    def __hash__(self):
        return hash(tuple(self.word_id))


class NotebookManager(models.Manager):
    @transaction.atomic
    def create_notes(self, **kwargs):
        notes = self.create(**kwargs)
        notes.parse_title(save=False)
        notes.parse_content(save=False)
        notes.save()
        notes.register_words()
        return notes


class Notebook(models.Model):
    objects: NotebookManager = NotebookManager()

    owner = models.ForeignKey(_User, on_delete=models.CASCADE)
    title = models.CharField(max_length=256)
    title_html = models.TextField(default="")
    description = models.CharField(max_length=512, default="")
    content = models.TextField()
    content_html = models.TextField(default="")
    word_list = models.JSONField(default=list)
    words = models.ManyToManyField(Word)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    @transaction.atomic
    def update_notes(self, data: Dict):
        for key, val in data.items():
            if val is not None:
                setattr(self, key, val)
        if "title" in data:
            self.parse_title(save=False)
        if "content" in data:
            self.parse_content(save=False)
        self.save()
        self.register_words()

    @transaction.atomic
    def redo_parsing(self):
        self.parse_title(save=False)
        self.parse_content(save=False)
        self.save()
        self.register_words()

    def parse_title(self, *, save=True):
        html_lines = []
        word_tokens = []
        if self.title:
            html = []
            for tkn in DefaultTokenizer.tokenize_text(self.title):
                html.append(tkn.to_html())
                try:
                    pos = PartOfSpeech(tkn.part_of_speech)
                    if pos in PartOfSpeech.noteworthy_pos():
                        logger.debug(f"Including token {tkn} to word list.")
                        word_tokens.append(
                            {
                                "word": tkn.normalized_form,
                                "word_id": tkn.word_id,
                            }
                        )
                    else:
                        logger.debug(f"Skipping token {tkn} from word list")
                except ValueError:
                    logger.warning(f"Unknown part-of-speech found: {tkn}")
            html_lines.append("".join(html))
        self.content_html = "<br>".join(html_lines)
        self.add_word_list(word_tokens)
        if save:
            self.save()

    def parse_content(self, *, save=True):
        lines = self.content.split("\n")
        html_lines = []
        word_tokens = []
        for line in lines:
            if line:
                tokens = DefaultTokenizer.tokenize_text(line.strip())
                html = []
                for tkn in tokens:
                    html.append(tkn.to_html())
                    try:
                        pos = PartOfSpeech(tkn.part_of_speech)
                        if pos in PartOfSpeech.noteworthy_pos():
                            logger.debug(f"Including token {tkn} to word list.")
                            word_tokens.append(
                                {
                                    "word": tkn.normalized_form,
                                    "word_id": tkn.word_id,
                                }
                            )
                        else:
                            logger.debug(f"Skipping token {tkn} from word list")
                    except ValueError:
                        logger.warning(f"Unknown part-of-speech found: {tkn}")
                html_lines.append("".join(html))
        self.content_html = "<br>".join(html_lines)
        self.add_word_list(word_tokens)
        if save:
            self.save()

    def add_word_list(self, words: List[Dict]):
        current_state = set([WordToken(**wt) for wt in self.word_list])
        additional_state = set([WordToken(**wt) for wt in words])
        new_state = current_state.union(additional_state)
        self.word_list = [wt.dict() for wt in new_state]

    @transaction.atomic
    def register_words(self):
        for word in self.word_list:
            tokens = DefaultTokenizer.tokenize_text(word["word"])
            for tkn in tokens:
                WordCollection.objects.add_token(self.owner, tkn)
