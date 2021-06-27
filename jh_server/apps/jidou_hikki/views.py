from jh_server.apps.jidou_hikki.models.vocabulary import Vocabulary
from typing import Iterable
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import login

from .utils import demo as demo_utils
from .forms import NotebookForm, JidouHikkiUserCreationForm, NotePageForm, AnalysisForm
from .models import Notebook, NotePage, JidouHikkiUser, UserFlashCard


def serialize_vocab_list(vocabularies: Iterable[Vocabulary]):
    to_json = lambda entry: entry.to_json()
    serialized_deck = []
    for vocab in vocabularies:
        for entry_json in list(map(to_json, vocab.jmdict.entries)):
            card = {
                "word": vocab.word,
                "word_html": vocab.as_html(),
                "kana": ",".join([kana["text"] for kana in entry_json.get("kana", [])]),
                "senses": [],
            }
            for sense in entry_json.get("senses", []):
                card["senses"].append(
                    {
                        "pos": ",".join(sense["pos"]),
                        "translations": ",".join(
                            tl["text"] for tl in sense["SenseGloss"]
                        ),
                    }
                )
            serialized_deck.append(card)
    return serialized_deck


def register_view(request):
    if request.method == "POST":
        form = JidouHikkiUserCreationForm(request.POST)
        if form.is_valid():
            JidouHikkiUser.objects.create(username=form.cleaned_data["username"])
            return HttpResponseRedirect(f"/")
    else:
        form = JidouHikkiUserCreationForm()
    return render(request, "jidou_hikki/register.html", {"form": form})


def index(request):
    return HttpResponseRedirect("/home/")


def new_notebook(request):
    if request.method == "POST":
        form = NotebookForm(request.POST)
        if form.is_valid():
            new_note = Notebook.objects.create(
                title=form.cleaned_data["title"],
                owner=request.user,
                description=form.cleaned_data.get("description"),
            )
            return HttpResponseRedirect(f"/notebooks/{new_note.id}")
    else:
        form = NotebookForm()
    return render(request, "jidou_hikki/new_notebook.html", {"form": form})


def home(request):
    user = JidouHikkiUser.objects.first()
    if not user:
        return HttpResponseRedirect(f"/accounts/register/")
    login(request, user)
    notebooks = Notebook.objects.all().order_by("title")
    template = loader.get_template("jidou_hikki/home.html")
    context = {
        "notebooks": notebooks,
        "user": user,
    }
    return HttpResponse(template.render(context, request))


def notebook_content(request, book_id):
    book = get_object_or_404(Notebook, id=book_id)
    template = loader.get_template("jidou_hikki/notebook_contents.html")
    context = {"book": book}
    return HttpResponse(template.render(context, request))


def new_page(request, book_id):
    book = get_object_or_404(Notebook, id=book_id)
    if request.method == "POST":
        form = NotePageForm(request.POST)
        if form.is_valid():
            new_page = book.add_page(
                form.cleaned_data["title"], form.cleaned_data["content"]
            )
            return HttpResponseRedirect(f"/pages/{new_page.id}")
    else:
        form = NotePageForm()
    return render(
        request, "jidou_hikki/new_page.html", {"form": form, "notebook": book}
    )


def page(request, page_id):
    page = get_object_or_404(NotePage, id=page_id)
    template = loader.get_template("jidou_hikki/page.html")
    words = serialize_vocab_list(page.vocabularies.all())
    context = {"page": page, "words": words}
    return HttpResponse(template.render(context, request))


def vocabs(request):
    user = JidouHikkiUser.objects.first()
    template = loader.get_template("jidou_hikki/vocabs.html")
    context = {
        "user": user,
        "new_deck": serialize_vocab_list(
            [
                card.vocabulary
                for card in UserFlashCard.objects.get_new_cards(owner=user)
            ]
        ),
        "learning_deck": serialize_vocab_list(
            [
                card.vocabulary
                for card in UserFlashCard.objects.get_learning_cards(owner=user)
            ]
        ),
        "acquired_deck": serialize_vocab_list(
            [
                card.vocabulary
                for card in UserFlashCard.objects.get_acquired_cards(owner=user)
            ]
        ),
    }
    return HttpResponse(template.render(context, request))


def analyze(request):
    if request.method == "POST":
        form = AnalysisForm(request.POST)
        if form.is_valid():
            html, vocabs, failed = demo_utils.analyze_text(form.cleaned_data["content"])
            page = {"title": "Result", "html": html}
            words = serialize_vocab_list(vocabs)
            template = loader.get_template("jidou_hikki/analysis.html")
            context = {"page": page, "words": words, "failed": failed}
            return HttpResponse(template.render(context, request))
        else:
            return HttpResponseRedirect(f"/analyze/")
    else:
        form = AnalysisForm()
    return render(request, "jidou_hikki/new_analysis.html", {"form": form})
