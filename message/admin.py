from django.contrib import admin
from .models import Mail, MailLog

class MailAdmin(admin.ModelAdmin):
    list_display_links = ('creator', 'subject', )
    list_display = ('creator', 'sender', 'receiver', 'subject', 'attach', 'mail_type', 'desc', 'add_time', )
    list_filter = ['mail_type', 'sender']
    search_fields = ['creator', 'sender', 'receiver', 'subject', 'content', 'attach', 'mail_type', 'desc', 'add_time']
    ordering = ('-add_time',)

admin.site.register(Mail,MailAdmin)
