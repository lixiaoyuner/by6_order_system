from appointment.models import Appointment
from site_parameter.models import Parameter
from .models import Pay, Charge, PayType, Overtime

from django.utils.timezone import localtime
from django.contrib.auth.models import Group

class OrderError(Exception):
    '''
    网络错误类型定义
    '''
    def __init__(self, code:int=0, msg:str='', err=None):
        '''
        :param code: 错误码
        :param msg: 错误信息
        :param err: 错误对象
        '''
        self.code = code
        self.msg = msg
        self.err = err

    def __str__(self):
        return self.detail()

    def detail(self):
        '''错误详情'''
        if self.msg:
            return self.msg

        if self.err:
            return str(self.err)

        return '未知的错误'

class OrderManager():
    def can_order(self, user):
        try:
            groups = Group.objects.filter(user=user)
            charges = Charge.objects.filter(group__in=groups, rest_money__gt=0)
        except:
            return False, '可用充值卡查询失败'

        if not charges:
            return False, '无可用余额'
        else:
            return True, charges[0]

    def order(self, user, start_time, end_time, appointment):
        try:
            # print('--------', user, start_time, end_time, appointment)
            flag, charges = self.can_order(user)
            if flag:
                charge = charges
            elif appointment.status == 1:
                groups = Group.objects.filter(user=user)
                charge = Charge.objects.filter(group__in=groups)[0]
            else:
                raise IndexError
            price = charge.type.value // 12
            # print((start_time - end_time).seconds, '------')
            times = (end_time - start_time).seconds // 60 // 5
            pay_money = price * times
            charge.rest_money -= pay_money
            self.create_pay(money=pay_money, appointment=appointment, charge=charge, type=PayType.objects.get(id=4))
            overtime_money = self.is_overtime(start_time, end_time)
            if overtime_money:
                charge.rest_money -= overtime_money
                self.create_pay(money=overtime_money, appointment=appointment, charge=charge, type=PayType.objects.get(id=1))
            charge.save()
        except IndexError as error:
            raise IndexError
        except Exception as error:
            raise OrderError(msg='报错' + str(error))
        return pay_money, overtime_money

    def create_pay(self, money, charge, appointment, type):
        try:
            Pay.objects.create(money=money, appointment=appointment, charge=charge, type=type)
        except Exception as error:
            raise OrderError(msg='创建支付订单失败')
        return

    def is_overtime(self, start_time, end_time):
        on_time = [*map(int, Parameter.objects.get(id=1).value.split(':'))]
        
        on_time = on_time[0] * 60 + on_time[1]
        out_time = [*map(int, Parameter.objects.get(id=2).value.split(':'))]
        out_time = out_time[0] * 60 + out_time[1]
        on_price = int(Parameter.objects.get(id=3).value) / 60
        
        morning_minutes = localtime(start_time).hour * 60 + localtime(start_time).minute
        afternoon_minute = localtime(end_time).hour * 60 + localtime(end_time).minute

        mor_minutes = on_time - morning_minutes if on_time > morning_minutes else 0
        aft_minute = afternoon_minute - out_time if afternoon_minute > out_time else 0
        flag = start_time.weekday() == 5 or start_time.weekday() == 6
        # print(flag)
        flag = flag and not Overtime.objects.filter(date=start_time.date(), on=False)
        # print(flag, '0000000')
        if Overtime.objects.filter(date=start_time.date(), on=True) or flag:
            minutes = (end_time-start_time).seconds // 60
        else:
            minutes = mor_minutes + aft_minute
        money = on_price * minutes
        
        return round(money)


        
