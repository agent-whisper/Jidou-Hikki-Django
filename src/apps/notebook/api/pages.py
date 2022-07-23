from typing import Optional, List

from ninja import Router, ModelSchema, Schema
from ninja.pagination import paginate
from django.shortcuts import get_object_or_404, get_list_or_404

from src.apps.notebook.models import Page, Notebook


# Schema definitions
class PageSchema(ModelSchema):
    class Config:
        model = Page
        model_fields = [
            "id",
            "text",
            "word_list",
            "ordering",
            "created_at",
            "modified_at",
        ]


class PageHtmlSchema(ModelSchema):
    class Config:
        model = Page
        model_fields = [
            "id",
            "html",
            "word_list",
            "created_at",
            "modified_at",
        ]


class CreatePageSchema(Schema):
    text: str


class UpdatePageSchema(Schema):
    text: Optional[str] = None
    ordering: Optional[int] = None


# Routes
router = Router()


@router.get("/{notebook_id}/pages", response=List[PageSchema])
@paginate
def list_pages(request, notebook_id: int):
    return get_list_or_404(Page, notebook__id=notebook_id)


@router.get("/{notebook_id}/pages/{page_id}", response=PageSchema)
def get_page(request, notebook_id: int, page_id: int):
    return get_object_or_404(Page, notebook__id=notebook_id, id=page_id)


@router.get("/{notebook_id}/pages/{page_id}/html", response=PageHtmlSchema)
def get_page(request, notebook_id: int, page_id: int):
    return get_object_or_404(Page, notebook__id=notebook_id, id=page_id)


@router.post("/{notebook_id}/pages", response=PageSchema)
def create_page(request, notebook_id: int, data: CreatePageSchema):
    notebook = get_object_or_404(Notebook, id=notebook_id)
    return notebook.write_page(data.text)


@router.api_operation(
    ["PUT", "PATCH"], "/{notebook_id}/pages/{page_id}", response=PageSchema
)
def update_page(request, notebook_id: int, page_id: int, data: UpdatePageSchema):
    notebook = get_object_or_404(Notebook, id=notebook_id)
    page = get_object_or_404(Page, notebook=notebook, id=page_id)
    return notebook.update_page(page, data.dict())


@router.delete("/{notebook_id}/pages/{page_id}", response={204: None})
def delete_page(request, notebook_id: int, page_id: int):
    page = get_object_or_404(Page, notebook__id=notebook_id, id=page_id)
    page.delete()
    return 204, None
