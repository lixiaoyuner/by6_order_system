from django.db import models

class Parameter(models.Model):
    name  = models.CharField(max_length=32)
    value = models.CharField(max_length=32)
    desc  = models.CharField(max_length=200)
    modify_time = models.DateTimeField('modify time')


