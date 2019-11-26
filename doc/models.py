from django.db import models
from ckeditor.fields import RichTextField

# Create your models here.

class News(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField('标题', max_length=100, unique=True)
    content = RichTextField('内容',default='')
    time = models.DateTimeField('时间')
    top = models.BooleanField('是否置顶',default=False)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '新闻'
        verbose_name_plural = '新闻列表'

class Help(models.Model):
    id = models.AutoField(primary_key=True)
    content = RichTextField('内容',default='')

    class Meta:
        verbose_name = '帮助'
        verbose_name_plural = '帮助文档'