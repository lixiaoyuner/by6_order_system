from django.contrib import admin
from .models import News, Help

# Register your models here.
@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display_links = ('title', )
    list_display = ('title', 'content', 'time', 'top')
    ordering = ('-top', '-time')


@admin.register(Help)
class HelpAdmin(admin.ModelAdmin):
    list_display_links = ('id', 'content', )
    list_display = ('id', 'content')