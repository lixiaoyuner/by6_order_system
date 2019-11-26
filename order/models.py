from django.db import models
from django.contrib.auth.models import User
from appointment.models import Appointment

# Create your models here.

class Chargetype(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField('类型名称', max_length=100, unique=True)
    value = models.IntegerField('扣费方式，*元/小时')

    def __str__(self):
        return self.name + ' | ' + str(self.value) + '元/小时'

    class Meta:
        verbose_name = '充值类型'
        verbose_name_plural = '充值类型列表'


class Charge(models.Model):
    id = models.AutoField(primary_key=True)
    time = models.DateTimeField('充值时间', auto_now_add=True)
    money = models.IntegerField('充值金额')
    rest_money = models.IntegerField('剩余金额')
    user = models.ForeignKey(User, verbose_name='申请用户', on_delete=models.PROTECT)
    type = models.ForeignKey(Chargetype, on_delete=models.PROTECT, verbose_name='类型')
    contract = models.CharField('合同编号', max_length=100, null=True, blank=True,default='')
    project = models.CharField('项目名称', max_length=200, null=True, blank=True,default='')
    header = models.CharField('负责人', max_length=100, null=True, blank=True,default='')
    remarks = models.TextField('备注',default='', null=True, blank=True)

    def __str__(self):
        return f'序号{self.id} | 时间{self.time} | 金额{self.money}'
    
    @property
    def charge_type(self):
        return self.type.name

    class Meta:
        verbose_name = '充值'
        verbose_name_plural = '充值列表'


class PayType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField('类型名称', max_length=100, unique=True)
    value = models.IntegerField('加班费单价（维护），*元/小时', default=1)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '消费类型'
        verbose_name_plural = '消费类型列表'

class Pay(models.Model):
    id = models.AutoField(primary_key=True)
    time = models.DateTimeField('消费时间', auto_now_add=True)
    money = models.IntegerField('消费金额')
    appointment = models.ForeignKey(Appointment, related_name='pay', verbose_name='预约记录', on_delete=models.SET_NULL, blank=True, null=True)
    charge = models.ForeignKey(Charge, verbose_name='充值记录', on_delete=models.PROTECT)
    type = models.ForeignKey(PayType, on_delete=models.PROTECT, verbose_name='类型')
    remarks = models.TextField('备注', default='')

    def __str__(self):
        return f'序号{self.id} | 时间{self.time} | 金额{self.money}'
        
    class Meta:
        verbose_name = '消费'
        verbose_name_plural = '消费列表'

class Overtime(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField('日期')
    on = models.BooleanField('是否加班日', default=True)

    class Meta:
        verbose_name = '加班日期'
        verbose_name_plural = '加班日期表'