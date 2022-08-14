from typing import Dict, List, Tuple

from django.db import models, transaction
from django.contrib.auth import get_user_model
from pydantic import BaseModel

from src.services.logging import logger
from src.services.tokenizer import DefaultTokenizer
from src.services.tokenizer.utils import check_only_japanese_chars
from src.services.tokenizer.schemas import PartOfSpeech, Token
from src.apps.wordcollection.models import Word, WordCollection

_User = get_user_model()


class WordToken(BaseModel):
    word: str
    word_id: str
    count: int = 1

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

    def _should_save_token(self, token: Token) -> bool:
        """Check if token should be saved into collection."""
        verdict = False
        try:
            if token.only_contains_japanese_chars and PartOfSpeech.is_noteworthy(
                token.part_of_speech
            ):
                logger.debug(f"Including token {token} to word list.")
                verdict = True
            else:
                logger.debug(f"Skipping token {token} from word list")
        except ValueError:
            logger.warning(f"Unknown part-of-speech found: {token}")
        return verdict

    def parse_title(self, *, save=True):
        html_lines, word_tokens = self._parse_html_and_tokens([self.title])
        self.title_html = "<br>".join(html_lines)
        self.add_word_list(word_tokens)
        if save:
            self.save()

    def parse_content(self, *, save=True):
        lines = self.content.split("\n")
        html_lines, word_tokens = self._parse_html_and_tokens(lines)
        self.content_html = "<br>".join(html_lines)
        self.add_word_list(word_tokens)
        if save:
            self.save()

    def _parse_html_and_tokens(
        self, lines_of_text: List[str]
    ) -> Tuple[List[str], List[Token]]:
        html_lines = []
        word_token_map = {}
        for line in lines_of_text:
            if line:
                tokens = DefaultTokenizer.tokenize_text(line.strip())
                html = []
                for tkn in tokens:
                    if self._should_save_token(tkn):
                        html.append(tkn.to_html())
                        if tkn.word_id not in word_token_map:
                            word_token_map[tkn.word_id] = {
                                "word": tkn.normalized_form,
                                "word_id": tkn.word_id,
                                "count": 1,
                            }
                        else:
                            word_token_map[tkn.word_id]["count"] += 1
                html_lines.append("".join(html))
        word_tokens = list(word_token_map.values())
        return html_lines, word_tokens

    def add_word_list(self, words: List[Dict]):
        current_state = set([WordToken(**wt) for wt in self.word_list])
        additional_state = set([WordToken(**wt) for wt in words])
        new_state = current_state.union(additional_state)
        self.word_list = sorted(
            [wt.dict() for wt in new_state],
            key=lambda item: item["count"],
            reverse=True,
        )

    @transaction.atomic
    def register_words(self):
        for word in self.word_list:
            tokens = DefaultTokenizer.tokenize_text(word["word"])
            for tkn in tokens:
                WordCollection.objects.add_token(self.owner, tkn)
