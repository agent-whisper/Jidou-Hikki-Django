from ninja import NinjaAPI
from ninja.security import django_auth
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

from src.apps.common.api.auth import router as auth_router
from src.apps.notebook.api.notebooks import router as notebook_router

api = NinjaAPI(csrf=True)
api.add_router("/auth", auth_router, tags=["auth"])
api.add_router("/notebooks", notebook_router, tags=["notebooks"], auth=django_auth)

urlpatterns = [
    path("api/", api.urls),
    path("admin/", admin.site.urls),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)