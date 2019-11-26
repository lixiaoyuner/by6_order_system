#coding=utf-8
import os
import sys
import datetime
import time


from dateutil.relativedelta import relativedelta

from django.core.management.base import BaseCommand 
from appointment.models import Appointment
from message.models import Mail
from django.utils.timezone import localtime
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        mail = Mail()
        mail.receiver = 'bobfu01@163.com'
        mail.subject = u'test'
        mail.content = u'test'
        mail.send('script')
       
