from django.urls import path, re_path
from django.conf import settings
from django.contrib import admin

from . import views
from django.views import static

admin.autodiscover()

urlpatterns = [
    
    path('charge/', views.charge, name='charge'),
    path('charge/record/', views.charge_record, name='charge_record'),
    path('charge/myrecord/', views.my_charge_record, name='my-charge'),
    path('pay/deduct/', views.deduct, name='deduct'),
]
