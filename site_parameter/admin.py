from django.contrib import admin
from .models import Parameter

class ParameterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'value', 'desc', 'modify_time')

admin.site.register(Parameter, ParameterAdmin)
