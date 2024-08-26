from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from django.core.validators import MinValueValidator, MaxValueValidator


class Accesstoken(models.Model):
    access_token = models.CharField(max_length=1024, unique=True)
    expire_time = models.DateTimeField()


class User(models.Model):
    
    class Gender_choices(models.IntegerChoices):
        male = 0, _('男')
        female = 1, _('女')
    
    class Belief_choices(models.IntegerChoices):
        other = 0, _('其他')
        fo = 1, _('佛教')

    class Identity_choices(models.IntegerChoices):
        ordinary = 0, _('普通')
        vip = 1, _('VIP')


    # 登录
    openid = models.CharField(verbose_name='openid', max_length=28, unique=True, db_index=True)

    # 基本信息
    name = models.CharField(verbose_name='姓名', max_length=15, null=True, blank=True)
    gender = models.IntegerField(verbose_name='性别', choices=Gender_choices.choices, null=True, blank=True)
    birthdt = models.DateTimeField(verbose_name='出生时间', null=True, blank=True)
    birthloc = models.CharField(verbose_name='出生地', max_length=30, null=True, blank=True)
    liveloc = models.CharField(verbose_name='现居地', max_length=30, null=True, blank=True)
    job = models.CharField(verbose_name='职业', max_length=15, null=True, blank=True)
    belief = models.IntegerField(verbose_name='信仰', choices=Belief_choices.choices, null=True, blank=True)
    mbti = models.CharField(verbose_name='MBTI', max_length=4, null=True, blank=True)

    # 其他信息
    identity = models.IntegerField(verbose_name='用户身份', choices=Identity_choices.choices, default=0)
    phone = models.CharField(verbose_name='手机号', max_length=11, null=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True) 
    update_time = models.DateTimeField(verbose_name='修改时间', auto_now=True)
    is_active = models.BooleanField(verbose_name='是否激活', default=True)


    def __str__(self) -> str:
        return f'{self.name}'

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = "用户"

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class Address(models.Model):
    user = models.ForeignKey(verbose_name='用户', to=User, on_delete=models.CASCADE)
    recipient = models.CharField(verbose_name='收货人', max_length=15, null=False, blank=False)
    phone = models.CharField(verbose_name='收货人手机号', max_length=11, null=False, blank=False)
    detailed_address = models.TextField(verbose_name='详细地址', null=False, blank=False)

    def __str__(self):
        return f"{self.user.name} - {self.recipient}"
    
    class Meta:
        verbose_name = "地址"
        verbose_name_plural = "地址"
    
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        # fields = '__all__'
        exclude = ['user']


class Advice(models.Model):
    user = models.ForeignKey(verbose_name='用户', to=User, on_delete=models.CASCADE)
    person_name = models.CharField(verbose_name='人名', max_length=15, null=False, blank=False)

    gem_name = models.CharField(verbose_name='珠名称', max_length=20, null=False, blank=False)
    
    mark = models.IntegerField(verbose_name='匹配度',  null=False, blank=False,
                               validators=[MinValueValidator(0), MaxValueValidator(100)])


class AdviceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Advice
        exclude = ['user', 'person_name']