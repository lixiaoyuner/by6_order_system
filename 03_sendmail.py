#!/usr/bin/env python36
# -*- coding: utf-8 -*-
import os, sys, time, datetime
from pytz import UTC
import traceback
import django
import logging
logging.basicConfig(level=logging.WARNING, filename='/var/log/nginx/by6_crontab.log', filemode='a')  # 'a'为追加模式,'w'为覆盖写

if __name__ == "__main__":
    try:
        # 将项目路径添加到系统搜寻路径当中，查找方式为从当前脚本开始，找到要调用的django项目的路径
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        # 设置项目的配置文件 不做修改的话就是 settings 文件
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_site.settings")
        django.setup()  # 加载项目配置
    except Exception as e:
        msg = traceback.format_exc()
        logging.error(msg)
        sys.exit(1) 

    from appointment.models import Appointment
    from order.managers import OrderManager
    from message.models import Mail
    from django.utils.timezone import localtime
    from django.contrib.auth.models import User

    now = datetime.datetime.utcnow();    print(now)
    #now = datetime.datetime.now(tz=UTC); print(now)
    admin_users = User.objects.filter(is_superuser = True)
    email_list = [u.email for u in admin_users if u.email]    
    print("管理员邮箱地址：",end='');print(email_list,end='\n\n')

    draft_list = Appointment.objects.filter(draft = True)
    for this_draft in draft_list:
        print(this_draft)
        if not this_draft.last_edit_time:
            continue    #没有最后修改时间，不正常，跳过
        last_edit_time = this_draft.last_edit_time.replace(tzinfo=None)
        #last_edit_time = this_draft.last_edit_time.replace(tzinfo=UTC)
        print("server time now :  ",end=''); print( now );
        print("Last modify time:  ",end=''); print( last_edit_time)
        if last_edit_time > now:
            print("    最后修改时间在未来，不正常，跳过")
            continue   
        draft_minutes  = 5 #最后修改时间5分钟内，保持 draft状态
        print("now - lastmodify:  ",end=''); print( (now - last_edit_time).seconds)
        if (now - last_edit_time).seconds < 60*draft_minutes:
            print("    未满draft保持时间，仍然保持draft，处理下一条")
            continue
        #add_time=this_draft.add_time.replace(tzinfo=None)
        #if add_time < datetime.datetime(2020, 2, 6, 0, 0, 0):
        #    continue
        order_money, overtime_money = (0, 0)
        if not this_draft.user.is_staff:
            try:
                order_money, overtime_money = OrderManager().order(this_draft.user, this_draft.start_time, this_draft.end_time, this_draft)
            except IndexError:
                if this_draft.user.email:
                    emails =email_list + [this_draft.user.email]
                mail = Mail()
                mail.receiver = ','.join(emails)
                mail.subject = u'预约失败，账户余额不足。%(username)s 提交了设备使用预约'% {'username': this_draft.user.username}
                mail.content = u'''
        %(username)s 于 %(last_edit_time)s 提交了设备使用预约申请，使用时间段为：
            %(start_time)s 到 %(end_time)s 。
        申请人IP地址 %(apply_ip)s 。由于账户余额不足，预约失败，已删除预约记录。
        ''' % {'username': this_draft.user.username,
            'last_edit_time': localtime(this_draft.last_edit_time).strftime('%Y-%m-%d %H:%M:%S'),
            'start_time': localtime(this_draft.start_time).strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': localtime(this_draft.end_time).strftime('%Y-%m-%d %H:%M:%S'),
            'apply_ip': this_draft.apply_ip,
            }
                # this_draft.set_draft(False) #代码重构了save(), 并添加了set_draft() 方法
                print("所有收件人的邮箱地址：",end='');print(emails)
                print(mail.subject)
                print(mail.content)
                mail.send('script')
                this_draft.delete()
                continue
        #最后修改时间已经满draft_minutes，发邮件并调整为非 draft状态
        if this_draft.user.email:
            emails = email_list + [this_draft.user.email]
        else:
            emails = email_list
        mail = Mail()
        mail.receiver = ','.join(emails)
        mail.subject = u'%(username)s 提交了设备使用预约'% {'username': this_draft.user.username}
        mail.content = u'''
%(username)s 于 %(last_edit_time)s 提交了设备使用预约申请，使用时间段为：
    %(start_time)s 到 %(end_time)s 。共花费 %(money)s，其中预约费%(order_money)s，加班费%(overtime_money)s。
申请人IP地址 %(apply_ip)s 。
''' % {'username': this_draft.user.username,
       'last_edit_time': localtime(this_draft.last_edit_time).strftime('%Y-%m-%d %H:%M:%S'),
       'start_time': localtime(this_draft.start_time).strftime('%Y-%m-%d %H:%M:%S'),
       'end_time': localtime(this_draft.end_time).strftime('%Y-%m-%d %H:%M:%S'),
       'apply_ip': this_draft.apply_ip,
       'money': order_money + overtime_money,
       'overtime_money': overtime_money,
       'order_money': order_money, 
        }   
        this_draft.set_draft(False) #代码重构了save(), 并添加了set_draft() 方法
        print("所有收件人的邮箱地址：",end='');print(emails)
        print(mail.subject)
        print(mail.content)
        mail.send('script')
