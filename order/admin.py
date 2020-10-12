from django.contrib import admin
from .models import Chargetype, Charge, PayType, Pay, Overtime
# Register your models here.
class ChargeTypeAdmin(admin.ModelAdmin):
    list_display_links = ('name',)
    list_display = ('id', 'name', 'value')
    ordering = ('name',)

admin.site.register(Chargetype, ChargeTypeAdmin)

class ChargeAdmin(admin.ModelAdmin):
    list_display_links = ('time',)
    list_display = ( 'time', 'money', 'rest_money', 'group', 'type', 'remarks')
    search_fields =  ['time']
    list_filter = ['type', 'group']
    ordering = ('-time',)

admin.site.register(Charge, ChargeAdmin)

class PayTypeAdmin(admin.ModelAdmin):
    list_display_links = ('name',)
    list_display = ('id', 'name', 'value')
    ordering = ('name',)

admin.site.register(PayType, PayTypeAdmin)

class PayAdmin(admin.ModelAdmin):
    list_display_links = ('time',)
    list_display = ( 'time', 'money', 'appointment', 'charge', 'type', 'remarks')
    search_fields =  ['time']
    list_filter = ['type']
    ordering = ('-time',)

admin.site.register(Pay, PayAdmin)

class OvertimeAdmin(admin.ModelAdmin):
    list_display_links = ('date',)
    list_display = ('id', 'date', 'on')

admin.site.register(Overtime, OvertimeAdmin)
