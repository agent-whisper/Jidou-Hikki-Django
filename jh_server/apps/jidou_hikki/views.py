from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import login

from .forms import NotebookForm, JidouHikkiUserCreationForm, NotePageForm
from .models import Notebook, NotePage, JidouHikkiUser


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
            return HttpResponseRedirect(f"/notebooks/{book.id}")
    else:
        form = NotePageForm()
    return render(
        request, "jidou_hikki/new_page.html", {"form": form, "notebook": book}
    )


def page(request, page_id):
    page = get_object_or_404(NotePage, id=page_id)
    template = loader.get_template("jidou_hikki/page.html")
    context = {"page": page}
    return HttpResponse(template.render(context, request))


def vocabs(request):
    user = JidouHikkiUser.objects.first()
    template = loader.get_template("jidou_hikki/vocabs.html")
    context = {"user": user}
    return HttpResponse(template.render(context, request))
