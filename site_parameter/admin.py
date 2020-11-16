from django.contrib import admin
from .models import Parameter

class ParameterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'value', 'desc', 'modify_time')

    def has_delete_permission(self, request, obj=None):
        return False
    # def has_change_permission(self, request, obj=None):
    #     return False
    def get_actions(self, request):
        return []

admin.site.register(Parameter, ParameterAdmin)
