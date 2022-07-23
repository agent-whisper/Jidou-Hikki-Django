from typing import List, Optional

from ninja import Router, ModelSchema, Schema
from ninja.pagination import paginate
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, get_list_or_404

from .pages import router as pages_router
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


class NotebookSchema(ModelSchema):
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


class CreateNotebookSchema(Schema):
    title: str
    description: str


class UpdateNotebookSchema(Schema):
    title: str = None
    description: str = None


# Routes
router = Router()
router.add_router("", pages_router)


@router.get("/", response=List[NotebookSchema])
@paginate
def list_notebooks(request):
    # TODO: Use user from authorization
    owner = _User.objects.first()
    return Notebook.objects.filter(owner=owner)


@router.get("/{id}", response=NotebookSchema)
def get_notebook(request, id: int):
    # TODO: Use user from authorization
    owner = _User.objects.first()
    return get_object_or_404(Notebook, owner=owner)


@router.post("/", response=NotebookSchema)
def create_notebook(request, data: CreateNotebookSchema):
    # TODO: Use user from authorization
    owner = _User.objects.first()
    notebook = Notebook.objects.create(
        owner=owner, title=data.title, description=data.description
    )
    return notebook


@router.api_operation(["PUT", "PATCH"], "/{id}", response=NotebookSchema)
def update_notebook(request, id: int, data: UpdateNotebookSchema):
    # TODO: Use user from authorization
    owner = _User.objects.first()
    notebook = get_object_or_404(Notebook, owner=owner, id=id)
    for key, val in data.dict().items():
        if val is not None:
            setattr(notebook, key, val)
    return notebook


@router.delete("/{id}", response={204: None})
def delete_notebook(request, id: int):
    # TODO: Use user from authorization
    owner = _User.objects.first()
    notebook = get_object_or_404(Notebook, owner=owner, id=id)
    notebook.delete()
    return 204, None
