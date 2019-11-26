#!/usr/bin/env python3
#coding=utf-8
import os
import sys
import datetime
import time

draft_seconds = 300
if __name__ == "__main__":
 
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "appointment.settings_dev")
    
    from appointment.models import Appointment
    from message.models import Mail
    from django.utils.timezone import localtime
    from django.contrib.auth.models import User
    # print Appointment.objects.filter()
    admin_users = User.objects.filter(is_superuser = True)
    # print admin_users
    email_list = [u.email for u in admin_users if u.email]    

    while True:   
 
        now = datetime.datetime.now()

        draft_list = Appointment.objects.filter(draft = True)
        for draft in draft_list:
            if not draft.last_edit_time:
                continue
            last_edit_time = draft.last_edit_time.replace(tzinfo=None)
            time_span = now - last_edit_time
            if time_span.seconds >= draft_seconds:
                if draft.user.email:
                    mail = Mail()
                    mail.receiver = ','.join(email_list + [draft.user.email])
                    mail.subject = u'设备使用预约申请确认通知'
                    mail.content = u'''
%(username)s 于 %(last_edit_time)s 提交了设备使用预约申请，使用时间段为：
    %(start_time)s 到 %(end_time)s 。
申请人IP地址 %(apply_ip)s 。
''' % {'username': draft.user.username,
       'last_edit_time': localtime(draft.last_edit_time).strftime('%Y-%m-%d %H:%M:%S'),
       'start_time': localtime(draft.start_time).strftime('%Y-%m-%d %H:%M:%S'),
       'end_time': localtime(draft.end_time).strftime('%Y-%m-%d %H:%M:%S'),
       'apply_ip': draft.apply_ip
}
                    # mail.send('script')

                draft.draft = False
                draft.save()
        time.sleep(60)
