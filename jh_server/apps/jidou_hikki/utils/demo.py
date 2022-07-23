import logging
from typing import Tuple, List

import jamdict
from jamdict import Jamdict

from jh_server.services.tokenizer import DefaultTokenizer
from jh_server.services.tokenizer.schemas import Token
from jh_server.services.tokenizer.sudachi import SudachiSplitMode
from jh_server.services.dictionary import DefaultJisho

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

DefaultJisho = DefaultJisho


class DryVocabulary:
    """
    Pseuodo Vocabulary model without DB connection.
    """

    def __init__(self, *args, **kwargs):
        self.dict_id = kwargs.get("idseq")
        self.word = kwargs.get("word")
        self.kanji = kwargs.get("kanji")
        self.furigana = kwargs.get("furigana")
        self.okurigana = kwargs.get("okurigana")
        self.reading = kwargs.get("reading_form")
        self._jmd_lookup = kwargs.get("jmd_lookup")

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


def token_2_vocab(token) -> Tuple[List[DryVocabulary], List[str]]:
    vocabs = []
    failed = []
    normalized_tokens = DefaultTokenizer.normalize_token(token)
    logger.debug(f"Normalized {token} -> {normalized_tokens}")
    for normalized_tkn in normalized_tokens:
        # Assume the first entry to be the best match
        jmd_info = DefaultJisho.lookup_token(normalized_tkn)
        if len(jmd_info.entries) > 0:
            # Some tokens may be a set of expressions, and not available in
            # JMDict. Example cases:
            #   -  キャラ作り
            jmd_entry = jmd_info.entries[0]
            vocabs.append(
                DryVocabulary(
                    dict_id=jmd_entry.idseq,
                    word=normalized_tkn.word,
                    kanji=normalized_tkn.kanji,
                    furigana=normalized_tkn.furigana,
                    okurigana=normalized_tkn.okurigana,
                    reading=normalized_tkn.reading_form,
                    jmd_lookup=jmd_info,
                )
            )
        else:
            failed.append(normalized_tkn.word)
            logger.error(
                f"Cannot process ({token} -> {normalized_tkn}) into vocabulary."
            )
    return vocabs, failed


def analyze_text(text: str) -> Tuple[str, List[DryVocabulary], List[str]]:
    """Similar to NotePage.analyze(), but returns the HTML text and list of DryVocabulary."""
    lines = text.split("\n")
    html_lines = []
    vocabularies = []
    failed_analysis = []
    for line in lines:
        if line:
            tokens = DefaultTokenizer.tokenize_text(
                line.strip(), SudachiSplitMode.MODE_B
            )
            for tkn in tokens:
                if tkn.contains_kanji():
                    vocabs, failed = token_2_vocab(tkn)
                    failed_analysis += failed
                    vocabularies += vocabs
            html = [tkn.as_html() for tkn in tokens]
            html_lines.append("".join(html))
    return "<br>".join(html_lines), vocabularies, failed_analysis
