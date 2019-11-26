from django.urls import path, re_path
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import (
LoginView, LogoutView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', LoginView.as_view(template_name='login.html')),
    path('accounts/logout/', LogoutView.as_view()),
    path('', include('appointment.urls')),
    path('order/', include('order.urls')),
    path('doc/', include('doc.urls')),
]
