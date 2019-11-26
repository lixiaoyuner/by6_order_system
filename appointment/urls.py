from django.urls import path, re_path
from django.conf import settings
from django.contrib import admin

from . import views
from django.views import static

admin.autodiscover()

urlpatterns = [
    path('', views.home, name='home'),
    path('add/', views.add, name='add'),
    path('update/', views.update, name='update'),
    path('delete/', views.delete, name='delete'),
    path('load/', views.load, name='load'),
    path('mark_break/', views.mark_break, name='mark-break'),
    path('stats/', views.stats, name='stats'),
    path('myapt/', views.my_appointment, name='my-appointment'),
    path('export/', views.export, name='export'),
    path('forget/', views.forget, name='forget'),
    path('forget_end/', views.forget_end, name='forget_end'),
    path('modify/', views.modify, name='modify'),
    re_path(r'^site_media/(?P<path>.*)$', static.serve, {'document_root': settings.STATIC_PATH}),
    re_path(r'^static/(?P<path>.*)$', static.serve, {'document_root': settings.STATIC_ROOT}),
]
