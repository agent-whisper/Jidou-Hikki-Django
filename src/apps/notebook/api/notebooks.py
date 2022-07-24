from typing import List, Optional

from ninja import Router, ModelSchema, Schema
from ninja.pagination import paginate
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, get_list_or_404

from src.apps.notebook.models import Notebook

# Schema definitions
_User = get_user_model()


class OwnerSchema(ModelSchema):
    class Config:
        model = _User
        model_fields = [
            "username",
            "first_name",
            "last_name",
            "is_active",
        ]


class NotebookMinSchema(ModelSchema):
    owner: OwnerSchema

    class Config:
        model = Notebook
        model_fields = [
            "id",
            "owner",
            "title",
            "description",
            "created_at",
            "modified_at",
        ]


class NotebookSchema(ModelSchema):
    owner: OwnerSchema

    class Config:
        model = Notebook
        model_fields = [
            "id",
            "owner",
            "title",
            "title_html",
            "content",
            "content_html",
            "word_list",
            "description",
            "created_at",
            "modified_at",
        ]


class CreateNotebookSchema(Schema):
    title: str
    description: str
    content: str


class UpdateNotebookSchema(Schema):
    title: str = None
    description: str = None
    content: str = None


# Routes
router = Router()


@router.get("/", response=List[NotebookMinSchema])
@paginate
def list_notebooks(request):
    return Notebook.objects.filter(owner=request.user)


@router.get("/{id}", response=NotebookSchema)
def get_notebook(request, id: int):
    return get_object_or_404(Notebook, owner=request.user, id=id)


@router.post("/", response=NotebookSchema)
def create_notebook(request, data: CreateNotebookSchema):
    notebook = Notebook.objects.create_notes(
        owner=request.user,
        title=data.title,
        description=data.description,
        content=data.content,
    )
    return notebook


@router.api_operation(["PUT", "PATCH"], "/{id}", response=NotebookSchema)
def update_notebook(request, id: int, data: UpdateNotebookSchema):
    notebook = get_object_or_404(Notebook, owner=request.user, id=id)
    notebook.update_notes(data.dict())
    return notebook


@router.delete("/{id}", response={204: None})
def delete_notebook(request, id: int):
    notebook = get_object_or_404(Notebook, owner=request.user, id=id)
    notebook.delete()
    return 204, None
