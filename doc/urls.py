from django.urls import path, re_path
from django.conf import settings
from django.contrib import admin

from . import views
from django.views import static

admin.autodiscover()

urlpatterns = [
    path('newslist/', views.newslist, name='newslist'),
    path('help/', views.help, name='help'),
]
