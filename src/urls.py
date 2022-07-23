from ninja import NinjaAPI
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

from src.apps.notebook.api import router as notebook_router

api = NinjaAPI()
api.add_router("/notebooks", notebook_router)

urlpatterns = [
    path("api/", api.urls),
    path("admin/", admin.site.urls),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)