from django.http import HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404

from .models import NoteBook, NotePage, JidouHikkiUser


def notebooks(request):
    notebooks = NoteBook.objects.all()
    template = loader.get_template("jidou_hikki/notebooks.html")
    context = {"notebooks": notebooks}
    return HttpResponse(template.render(context, request))


def notebook_content(request, book_id):
    book = get_object_or_404(NoteBook, id=book_id)
    template = loader.get_template("jidou_hikki/notebook_contents.html")
    context = {"book": book}
    return HttpResponse(template.render(context, request))


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
