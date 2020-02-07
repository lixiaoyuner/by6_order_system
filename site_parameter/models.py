from django.db import models

class Parameter(models.Model):
    id = models.IntegerField(primary_key=True)
    name  = models.CharField(max_length=32)
    value = models.CharField(max_length=32)
    desc  = models.CharField(max_length=200)
    modify_time = models.DateTimeField('modify time')


