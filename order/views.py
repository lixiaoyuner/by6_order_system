from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.timezone import localtime

from order.models import Chargetype, Charge, Pay, PayType
from appointment.models import Appointment
from django.contrib.auth import get_user_model

from datetime import datetime, timedelta

User = get_user_model()
# Create your views here.
@login_required
def charge(request):
    if request.method == 'GET':
        users = User.objects.all()
        # print(request.user.__class__)
        types = Chargetype.objects.all()
        return render(request, 'charge.html', {'users': users, 'types': types})
    elif request.method == 'POST':
        data = {}
        user = User.objects.get(id=int(request.POST.get('user_id')))
        type = Chargetype.objects.get(id=int(request.POST.get('type_id')))
        money = request.POST.get('money')
        if not money.isnumeric():
            data['ok'] = False
            data['msg'] = '请输入正确的金额'
            return JsonResponse(data)
        money = int(money)
        remark = request.POST.get('remark')
        contract = request.POST.get('contract')
        project = request.POST.get('project')
        header = request.POST.get('header')
        try:
            Charge.objects.create(user=user, type=type, money=money, rest_money=money, remarks=remark, contract=contract, project=project, header=header)
            data['ok'] = True
            data['msg'] = '成功充值'
        except Exception as error:
            data['ok'] = False
            data['msg'] = '数据库写入失败' + str(error)
        return JsonResponse(data)

@login_required
def charge_record(request):
    if request.method == 'GET':
        charges = Charge.objects.all().order_by('-time')
        return render(request, 'charge_record.html', {'charges': charges})
    elif request.method == 'POST':
        pass

@login_required
def my_charge_record(request):
    if request.method == 'GET':
        charges = Charge.objects.filter(user=request.user).order_by('-time')
        rest_money = sum([charge.rest_money for charge in charges if charge.rest_money > 0])
        return render(request, 'my_charge_record.html', {'charges': charges, 'rest_money': rest_money})
    elif request.method == 'POST':
        res, string = {}, ''
        id = int(request.POST.get('id'))
        charge = Charge.objects.get(id=id)
        pays = Pay.objects.filter(charge=charge)
        appointment_ids = set([pay.appointment.id for pay in pays if pay.appointment])
        appointments = []
        for appointment_id in appointment_ids:
            appointments.append(Appointment.objects.get(id=appointment_id))
        appointments.sort(key=lambda x: x.start_time)
        for appointment in appointments:   
            start_time = localtime(appointment.start_time).strftime('%Y-%m-%d %H:%M:%S')
            end_time = localtime(appointment.end_time).strftime('%H:%M:%S')
            string += f'<div>{start_time}--{end_time}  花费{appointment.money}元</div>'

        res['data'] = string

        return JsonResponse(res)

@login_required
def deduct(request):
    if request.method == 'GET':
        users = User.objects.all()
        appointments = Appointment.objects.filter(start_time__gt=datetime.now()-timedelta(days=30)).order_by('-start_time')
        types = PayType.objects.all()
        return render(request, 'deduct.html', {'appointments': appointments, 'types': types, 'users':users})
    elif request.method == 'POST':
        res = {}
        user_id = request.POST.get('user_id')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        remark = request.POST.get('remark')
        start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M')
        end_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M')
        if start_time > end_time:
            res['ok'], res['msg'] = False, '时间选择有误'
            return JsonResponse(res)
        try:
            Appointment.objects.create(user_id=user_id, start_time=start_time, end_time=end_time, remark=remark, last_edit_time=datetime.now())
            # appointment = Appointment.objects.get(id=appointment_id)
            # pay = Pay.objects.filter(appointment=appointment)[0]
            # type = PayType.objects.get(id=type_id)
            # pay.charge.rest_money -= money
            # pay.charge.save()
            # Pay.objects.create(money=money, charge=pay.charge, appointment=appointment, type=type, remarks=remark)
            # res['ok'], res['msg'] = True, '补缴成功'
        except Exception as error:
            print(str(error))
            res['ok'], res['msg'] = False, '数据库写入失败'

        return JsonResponse(res)
