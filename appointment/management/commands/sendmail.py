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

draft_seconds = 300

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        admin_users = User.objects.filter(is_superuser = True)
        email_list = [u.email for u in admin_users if u.email]    

        now = timezone.now()
        draft_line = now + relativedelta(seconds=-draft_seconds)
#        print (now, draft_line)
        draft_list = Appointment.objects.filter(last_edit_time__lt = draft_line, draft = True)
#        print(draft_list)
        for draft in draft_list:
 #           print(draft)
            if not draft.last_edit_time:
                continue
            time_span = now - draft.last_edit_time
            # print time_span
            if time_span.seconds >= draft_seconds:
                if draft.user.email:
                    mail = Mail()
                    mail.receiver = ','.join(email_list + [draft.user.email])
                    mail.subject = u'设备使用预约申请确认通知'
                    mail.content = u'''
%(username)s 于 %(last_edit_time)s 提交(或修改)了设备使用预约申请，使用时间段为：<br/>
    %(start_time)s 到 %(end_time)s 。<br/>
申请人IP地址 %(apply_ip)s 。
''' % {'username': draft.user.username,
       'last_edit_time': localtime(draft.last_edit_time).strftime('%Y-%m-%d %H:%M:%S'),
       'start_time': localtime(draft.start_time).strftime('%Y-%m-%d %H:%M:%S'),
       'end_time': localtime(draft.end_time).strftime('%Y-%m-%d %H:%M:%S'),
       'apply_ip': draft.apply_ip
}
                    mail.send('script')
                    print('[send mail to]', mail.receiver, '[user]', draft.user.username, '[ip]', draft.apply_ip, '[start_time]', draft.start_time, '[end_time]', draft.end_time)
                draft.set_draft(False)
