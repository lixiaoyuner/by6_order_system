#!/usr/bin/env python36
# -*- coding: utf-8 -*-
import os, sys, time, datetime
import traceback
import django
import logging
logging.basicConfig(level=logging.WARNING, filename='/var/log/nginx/by6_crontab.log', filemode='a')  # 'a'为追加模式,'w'为覆盖写

try:
    # 将项目路径添加到系统搜寻路径当中，查找方式为从当前脚本开始，找到要调用的django项目的路径
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    # 设置项目的配置文件 不做修改的话就是 settings 文件
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
    django.setup()  # 加载项目配置
except Exception as e:
    msg = traceback.format_exc()
    logging.error(msg)
    sys.exit(1) 

draft_seconds = 300
if __name__ == "__main__":
    from appointment.models import Appointment
    from message.models import Mail
    from django.utils.timezone import localtime
    from django.contrib.auth.models import User
    admin_users = User.objects.filter(is_superuser = True)
    email_list = [u.email for u in admin_users if u.email]    
    #print(email_list)

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
                    mail.send('script')

                draft.draft = False
                draft.save()
        sys.exit(1) 
        time.sleep(60)
