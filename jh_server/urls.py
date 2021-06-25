"""jh_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from jh_server.apps.jidou_hikki import views as jh_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", jh_views.index, name="index"),
    path("accounts/register/", jh_views.register_view, name="register"),
    path("notebooks/", jh_views.new_notebook, name="notebooks"),
    path("home/", jh_views.home, name="home"),
    path("notebooks/<int:book_id>", jh_views.notebook_content, name="book_content"),
    path("notebooks/<int:book_id>/add_page/", jh_views.new_page, name="new_page"),
    path("pages/<int:page_id>", jh_views.page, name="page"),
    path("vocab/", jh_views.vocabs, name="vocab"),
]
