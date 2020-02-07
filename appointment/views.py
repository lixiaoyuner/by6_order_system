#coding=utf-8
from datetime import datetime, timedelta

from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models.query import QuerySet
from django.utils.timezone import localtime
from dateutil.relativedelta import relativedelta

from utils import render_to_response_json
from .models import  Appointment, OnceDisablePeriod, DailyDisablePeriod, WeeklyDisablePeriod, HourRange, WeekdayRange, Punishment
from order.managers import OrderManager
from order.models import Pay, Charge, PayType, Chargetype

import xlwt
import hashlib
from io import BytesIO
from message.models import Mail
from django.utils.encoding import escape_uri_path
from django.contrib.auth import get_user_model
User = get_user_model()

@login_required
def home(request):
    dicts = {}
    # dicts['appointments'] = get_appointments(request)
    dicts['oncedisable'] = OnceDisablePeriod.objects.all()
    dicts['dailydisable'] = DailyDisablePeriod.objects.all()
    dicts['weeklydisable'] = WeeklyDisablePeriod.objects.all()
    dicts['hourrange'] = HourRange.objects.all()[0]
    dicts['weekdayrange'] = WeekdayRange.objects.all()[0]
    return render(request, 'home.html', dicts)

def _allow_add(user, start_time, end_time, force=False):
    '''
    判断是否有权限添加一条指定的记录（包含新添加以及修改到这个时间段）
    '''
    if start_time >= end_time:
        return False, '起始时间必须小于结束时间'

    now = datetime.now()
    if force is True and user.is_staff:  # 管理员可以在任意时间做任意操作
        # print '[ADMIN] ADD', start_time, end_time, now, (start_time - now).total_seconds(), (start_time - now).seconds
        return True, ''
    else:  
        # print '[USER] ADD', start_time, end_time, now, (start_time - now).total_seconds(), (start_time - now).seconds
        # 历史数据不能修改
        if start_time < now:
            return False, '历史数据不能修改! '

        # 预约至少提前2小时
        pre_hours = 2
        if (start_time - now).total_seconds() < 3600 * pre_hours:
            return False, '请至少提前%d小时提交预约！' % (pre_hours, )
        
        # 预约必须在最远可预约时间范围内
        if (end_time - now).total_seconds() > user.most_available_days * 24 * 3600:
            return False, '最多只能提交%d天之内的预约申请' % user.most_available_days

    return True, ''

def  _alterable(user, appointment, force=False):
    '''判断是否有权限更改一条指定记录'''
    start_time     = appointment.start_time.replace(tzinfo=None)
    end_time       = appointment.end_time.replace(tzinfo=None)
    last_edit_time = appointment.last_edit_time.replace(tzinfo=None)
    #localtime(appointment.start_time).replace(tzinfo=None) #把数据库的utc时间转为本django时区设置时间
    if force:# or user.is_staff: # 强制操作或管理员可以任意时间做操作
        return True, ''

    now = datetime.utcnow()
    # 历史数据不能修改
    if start_time < now:
       return False, '历史数据不能修改! '

    remedial_miniutes = 3      # 上次修改后，这个分钟内可以补救修改
    if last_edit_time > now:
        #print(now); print(last_edit_time)
        return False, '最后修改时间记录超前，不正常！' 
    #print("now - lastmodify:  ",end=''); print( (now - last_edit_time).seconds)
    if (now - last_edit_time).total_seconds() < 60*remedial_miniutes: #在补救期内
        return True, ''

    pre_hours         = 48     # 修改记录至少提前48小时
    if (start_time - now).total_seconds() < 3600 * pre_hours:
        return False, '请至少提前%d小时进行该操作！' % (pre_hours, )

    return True, ''

def _during_punishment(user):
    now = datetime.now()
    objs = Punishment.objects.filter(user = user, is_active = True, start_time__lte = now, end_time__gte = now).order_by('-end_time')
    if objs.exists():
        return True, objs[0].end_time
    return False, None

@login_required
def add(request):
    # 是否在惩罚期间
    if not request.user.is_staff:
        in_punishment, punish_end_time = _during_punishment(request.user)
        if in_punishment:
            return render_to_response_json({'res': False, 'msg': '由于您近期多次爽约，预约权限被暂时取消。 处罚截止日期：【' 
                + localtime(punish_end_time).strftime('%Y-%m-%d %H:%M:%S') + '】'})
    ok, res = OrderManager().can_order(request.user)
    print('-------', ok, res)
    if not ok:
        return render_to_response_json({'res': ok, 'msg': res})
    id = request.POST.get('id', None)
    start_time = request.POST.get('start_date', None)
    end_time = request.POST.get('end_date', None)
    remarks = request.POST.get('remarks')
    force = request.POST.get('force', False)
    if force == '1':
        force = True 
    else:
        force = False

    print ('[debug]', request.POST)
    if not id or not start_time or not end_time:
        return render_to_response_json({'res':False})

    ap = Appointment()
    ap.id = id
    ap.user = request.user
    ap.start_time = datetime.strptime(start_time,'%Y-%m-%d %H:%M:%S')
    ap.end_time = datetime.strptime(end_time,'%Y-%m-%d %H:%M:%S')
    ap.status = 0
    ap.remarks = remarks
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        ap.apply_ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ap.apply_ip = request.META['REMOTE_ADDR']
    
    res, msg = _allow_add(request.user, ap.start_time, ap.end_time, force=False)
    print ('[debug]', res, msg)
    if not res:
        # if request.user.is_staff:
        #     return render_to_response_json({'res': True, 'confirm': True, 'confirm_msg': msg, 'data': {
        #         'id': id,
        #         'start_date': start_time,
        #         'end_date': end_time,
        #         'remarks': remarks
        #         }})
        return render_to_response_json({'res': res, 'msg': msg})

    res, msg = ap.safe_save(request)
    return render_to_response_json({'res':res, 'msg': msg})

@login_required
def update(request):
    id = request.POST.get('id', None)
    start_time = request.POST.get('start_date', None)
    end_time = request.POST.get('end_date', None)
    remarks = request.POST.get('remarks')
    force = request.POST.get('force', False)
    
    if force == '1':
        force = True 
    else:
        force = False

    if not id or not start_time or not end_time:
        return render_to_response_json({'res':False})

    try:
        obj = Appointment.objects.get(pk=id)
    except:
        return render_to_response_json({'res':False, 'msg':'参数有误'})

    if (obj.user != request.user) and (not request.user.is_staff):
        result_data = {'res':False, 'msg': '您没有权限修改该记录'}
        return render_to_response_json(result_data)

    if obj.status == 1:
        return render_to_response_json({'res':False, 'msg':'管理员已锁定的预约不能修改'})

    start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    end_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')

    res_d, msg_d = _alterable(request.user, obj, force=False)
    if not res_d:
        return render_to_response_json({'res':False, 'msg': msg_d})
    
    res_a, msg_a = _allow_add(request.user, start_time, end_time, force=force)
    if not res_a:
        if request.user.is_staff:
            return render_to_response_json(
                {'res': True, 'confirm': True, 'confirm_msg': msg_a, 'data': {
                    'id': request.POST.get('id', None),
                    'start_date': request.POST.get('start_date', None),
                    'end_date': request.POST.get('end_date', None),
                    'remarks': request.POST.get('remarks', None)}
                })
        return render_to_response_json({'res':False, 'msg': msg_a})

    obj.start_time = start_time
    obj.end_time = end_time
    obj.remarks = remarks
    res, msg = obj.safe_save(request)
    pays = Pay.objects.filter(appointment=obj)
    back_money = 0
    charge = 0
    # print('fjadks----')
    for pay in pays:
        back_money += pay.money
        charge = pay.charge
        pay.delete()
    if pays:
        charge.rest_money += back_money
        charge.save()
    return render_to_response_json({'res':res, 'msg': msg})

@login_required
def delete(request):
    id = request.POST.get('id')
    force = request.POST.get('force', False)
    
    if force == '1':
        force = True 
    else:
        force = False

    obj = Appointment.objects.filter(pk=id)
    if not id or not obj:
        return render_to_response_json({'res':-1})

    obj = obj[0]
    if not request.user.is_staff and obj.user != request.user:
        return render_to_response_json({'res':False, 'msg':'您没有权限删除该记录'})

    if obj.status == 1:
        return render_to_response_json({'res':False, 'msg':'管理员已锁定的预约不能删除'})

    res, msg = _alterable(request.user, obj, force=False)
    if res: 
        try:
            pays = Pay.objects.filter(appointment=obj)
            back_money = 0
            charge = 0
            # print('fjadks----')
            for pay in pays:
                back_money += pay.money
                charge = pay.charge
                pay.delete()
            if pays:
                charge.rest_money += back_money
                charge.save()
            obj.delete()
            return render_to_response_json({'res':True, 'msg':'删除成功'})
        except:
            return render_to_response_json({'res':False, 'msg':'删除失败'}) 
    else:
        # if request.user.is_staff:
        #     return render_to_response_json({'res': True, 'confirm': True, 'confirm_msg': msg, 'data': {
        #         'id': request.POST.get('id', None)
        #         }})
        return render_to_response_json({'res':False, 'msg': msg})

@login_required
def load(request):
    mode = request.GET.get('mode')
    t = request.GET.get('t')

    try:
        t = int(t) / 1000
    except:
        t = None

    if mode == 'day':
        if t:
            start_time = datetime.fromtimestamp(t)
        else:
            now = datetime.now()
            start_time = datetime(now.year, now.month, now.day, 0, 0)
        end_time = start_time + relativedelta(days=1)
    elif mode == 'week':
        if t:
            start_time = datetime.fromtimestamp(t)
        else:
            now = datetime.now()
            start_time = datetime(now.year, now.month, now.day, 0, 0) + relativedelta(days=(-1*now.weekday()))
        end_time = start_time + relativedelta(weeks=1)
    elif mode == 'month':
        if t:
            start_time = datetime.fromtimestamp(t)
        else:
            now = datetime.now()
            start_time = datetime(now.year, now.month, 1, 0, 0)
        end_time = start_time + relativedelta(months=1)
    elif mode == 'timeline':
        if t:
            start_time = datetime.fromtimestamp(t)
        else:
            now = datetime.now()
            start_time = datetime(now.year, now.month, now.day, 0, 0) + relativedelta(days=(-1*now.weekday()))
        end_time = start_time + relativedelta(weeks=1)
    else:
        return render_to_response_json([])

    objs = Appointment.objects.filter(start_time__lte = end_time, end_time__gt = start_time)

    ev = []
    for obj in objs:
        if request.user.is_staff or obj.user == request.user:
            if obj.status == 1:
                readonly = True
                color = "green"
            else:
                readonly = False
                color = None
        else:
            readonly = True
            color = "#CCCCCC"
        ev.append({
            'id':obj.id, 
            'text':obj.remarks,
            'start_date': localtime(obj.start_time).strftime('%m/%d/%Y %H:%M'),
            'end_date': localtime(obj.end_time).strftime('%m/%d/%Y %H:%M'),
            'readonly': readonly,
            'color': color,
            'section_id': 1,
            'is_break': obj.is_break

            })

    return render_to_response_json(ev)

def get_appointments(request):
    now = datetime.now()
    year = int(now.strftime('%Y'))
    month = int(now.strftime('%m'))
    month_start = datetime(year, month, 1)
    month_end = month_start + relativedelta(months = 1) 
    appointments = Appointment.objects.filter(start_time__gte= now + relativedelta(months=-3))#filter(end_time__gt = month_start, start_time__lt = month_end).order_by('start_time')
    res = []
    for a in appointments:
        if request.user.is_staff or a.user == request.user:
            a.readonly = False
        else:
            a.readonly = True       #其他用户的  
            res.append(a)
            continue

        if localtime(a.start_time).strftime('%Y-%m-%d') == now.strftime('%Y-%m-%d'):  #当天的
            if not request.user.is_staff:
                a.readonly = True
        elif localtime(a.start_time).replace(tzinfo=None) < now:  #历史记录
            a.readonly = True
        
        res.append(a)
    return res


@login_required
def stats(request):
    '''总预约统计视图函数'''
    if not request.user.is_staff:
        return HttpResponseRedirect('/')

    start_time, end_time = get_start_end_time(request)
    objs = Appointment.objects.filter(start_time__gte = start_time, start_time__lte = end_time).all()
    dicts = stats_data(objs)
    dicts['start_time'] = start_time
    dicts['end_time'] = end_time
    return render(request, 'stats_all.html', dicts)


@login_required
def my_appointment(request):
    '''我的预约统计视图函数'''
    if request.method == 'GET':
        start_time, end_time = get_start_end_time(request)
        print(start_time, end_time)
        objs = Appointment.objects.filter(user=request.user, start_time__gte=start_time).filter(start_time__lte=end_time).all().order_by('start_time')
        dicts = stats_data(objs)
        dicts['start_time'] = start_time
        dicts['end_time'] = end_time
        return render(request, 'stats.html', dicts)

    elif request.method == 'POST':
        res, string = {}, ''
        id = request.POST.get('id')
        appointment = Appointment.objects.get(id=id)
        pays = Pay.objects.filter(appointment=appointment)
        for pay in pays:
            time = localtime(pay.time).strftime('%Y-%m-%d %H:%M:%S')
            string += f'<div>{time}---{pay.money}元---{pay.type} {pay.remarks}</div>'
        res['data'] = string
        return JsonResponse(res)

@login_required
def export(request):
    start_time, end_time = get_start_end_time(request)
    appointments = Appointment.objects.filter(start_time__gte=start_time, start_time__lte=end_time, draft=False)
    chargetypes = Chargetype.objects.all()
    paytype = PayType.objects.get(id=1)
    res = {chargetype.name: [0, chargetype.value] for chargetype in chargetypes}
    res['加班费用'] = [0, paytype.value]
    for appointment in appointments:
        res[appointment.charge_type][0] += appointment.order_money
        res['加班费用'][0] += appointment.over_money
    # print(res)
    # print(sum(appointment.money for appointment in appointments))
    workbook = xlwt.Workbook()
    worksheet = workbook.add_sheet('sheet')
    # 合并第0行的第0列到第3列。
    start_time = start_time.strftime('%Y年%m月%d日')
    end_time = end_time.strftime('%Y年%m月%d日')
    filename = f'{start_time}-{end_time}MR750科研使用明细'
    # print(filename)
    worksheet.write_merge(0, 0, 0, 3, filename)
    # worksheet=excelTabel.add_sheet('lagou',cell_overwrite_ok=True)
    worksheet.write(1,0,'分类')#公司名
    worksheet.write(1,1,'使用时间（小时）')#城市
    worksheet.write(1,2,'单价（元/小时')#地区
    worksheet.write(1,3,'金额（元）')#全职/简直
    i = 2
    for key,value in res.items():
        worksheet.write(i,0, key)#公司名
        worksheet.write(i,1, round(value[0]/int(value[1]), 1))#城市
        worksheet.write(i,2, value[1])#地区
        worksheet.write(i,3, value[0])#全职/简直
        i += 1
    worksheet.write(i,0, '总计')#全职/简直
    worksheet.write_merge(i, i, 1, 3, sum(appointment.money for appointment in appointments))
    i += 1
    worksheet.write(i,0,'填表人')#公司名
    # worksheet.write(i,1,'系统')#城市
    worksheet.write(i,2,'审核人')#地区
    # worksheet.write(i,3,'金额（元）')#全职/简直
    i += 1
    worksheet.write(i,0,'科室负责人')#公司名
    # worksheet.write(i,1,'系统')#城市
    worksheet.write(i,2,'填表日期')#地区
    # worksheet.write(i,3,'金额（元）')#全职/简直
    # response = HttpResponse(content_type='APPLICATION/OCTET-STREAM')
    # response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    # output = BytesIO()
    # workbook.save(output)
    # output.seek(0)
    # response.write(output.getvalue())
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = "attachment; filename*=utf-8''{}.xls".format(escape_uri_path(filename))
    workbook.save(response)
    return response

def get_start_end_time(request):
    '''
    获取开始和结束时间

    :param request:
    :return:
        （start, end）# type; datetime
    '''
    start_time = request.GET.get('start_time')
    end_time = request.GET.get('end_time')

    try:
        end_time = datetime.strptime(end_time, '%Y-%m-%d')
    except:
        end_time = datetime.now().date() + relativedelta(months=1)

    try:
        start_time = datetime.strptime(start_time, '%Y-%m-%d')
    except:
        start_time = datetime.now().date()

    return start_time, end_time

def stats_data(objs:QuerySet):
    '''
    '''
    res = {}
    total_time = timedelta()
    for obj in objs:
        time_span = obj.end_time - obj.start_time
        total_time += time_span
        if obj.user_id in res:
            res[obj.user_id]['apps'].append((obj.start_time, obj.end_time, obj.end_time - obj.start_time, obj.money, obj.order_money, obj.over_money, obj.id))
            res[obj.user_id]['count'] += time_span
        else:
            res[obj.user_id] = {
                'user': obj.user,
                'apps': [(obj.start_time, obj.end_time, obj.end_time - obj.start_time, obj.money, obj.order_money, obj.over_money, obj.id)],
                'count': time_span,
            }

    dicts = {}
    dicts['total_time'] = total_time
    dicts['data'] = res
    return dicts


def mark_break(request):
    if not request.user.is_staff:
        return render_to_response_json({'res': False, 'msg': '操作失败：此操作需要管理员权限'})

    aid = request.POST.get('id', None)
    is_break = request.POST.get('break', None)    

    obj = Appointment.objects.filter(pk=aid)
    if not aid or not obj.exists():
        return render_to_response_json({'res':False, 'msg': '操作失败：参数有误'})

    obj = obj[0]

    if is_break != None:
        if is_break == '1':
            is_break = True 
        else:
            is_break = False 
    else:
        is_break = not obj.is_break

    now = datetime.now()
    end_time = localtime(obj.end_time).replace(tzinfo=None)
    if end_time > now:
        return render_to_response_json({'res': False, 'msg': '操作失败：只能对结束时间早于当前时刻的预约进行爽约标记'})

    try:
        punishment = obj.set_break(is_break)
    except:
        return render_to_response_json({'res': False, 'msg': '标记失败'})
    
    if is_break:
        msg = '爽约标记成功。'
        if punishment:
            msg += str(obj.user.username) + ' 的爽约次数达到惩罚标准，暂停预约权限时间：【' + punishment[0].strftime("%Y-%m-%d %H:%M:%S") +\
             ' ~ ' + punishment[1].strftime("%Y-%m-%d %H:%M:%S") + '】' 
    else:
        msg = '取消爽约标记成功'
    return render_to_response_json({'res': True, 'msg': msg})

def forget(request):
    return render(request, 'forget.html')

def forget_end(request):
    username = request.GET.get('username')
    try:
        user = User.objects.get(username=username)
        token = hashlib.md5()
        token.update(datetime.now().__str__().encode())
        token = token.hexdigest()
        user.token = token
        user.token_time = datetime.now()
        user.save()
        mail = Mail()
        mail.receiver = user.email
        mail.subject = '密码找回'
        mail.content = f'请访问以下地址修改密码，有效期为一个小时\n http://159.226.91.141:8888/modify/?token={token}'
        mail.send('script')
        res = '修改密码链接已经发送至邮箱'
    except Exception:
        res = '查无此人'
    return render(request, 'forget_end.html', {'res': res})

def modify(request):
    if request.method == 'GET':
        return render(request, 'modify.html')
    if request.method == 'POST':
        token = request.GET.get('token')
        password = request.POST.get('password')
        try:
            user = User.objects.get(token=token)
        except Exception as error:
            return render(request, 'forget_end.html', {'res': '修改失败，该链接已失效，请重新申请'})
        token_time = localtime(user.token_time).replace(tzinfo=None)
        print(datetime.now(), token_time)
        if datetime.now() > token_time + timedelta(hours=1):
            res = '链接已超时'
        else:
            user.set_password(password)
            user.token = ''
            user.save()
            res = '修改成功'
        return render(request, 'forget_end.html', {'res': res})