from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


# Create your models here.
class User(models.Model):
    
    class Gender_choices(models.IntegerChoices):
        male = 0, _('男')
        female = 1, _('女')
    
    class Belief_choices(models.IntegerChoices):
        other = 0, _('其他')
        fo = 1, _('佛教')

    class Mood_choices(models.IntegerChoices):
        good = 0, _('好')
        mid = 1, _('一般')
        bad = 2, _('不好')

    class Question_choices_two(models.IntegerChoices):
        up = 0, _('选项一')
        down = 1, _('选项二')

    class Wish_choices(models.IntegerChoices):
        career = 1, _('事业')
        study = 2, _('学业')
        wealth = 3, _('财富')
        love = 4, _('爱情')
        health = 5, _('健康')
        safety = 6, _('安全')
        family = 7, _('家庭')
        happiness = 8, _('快乐')
        shunyi = 9, _('万事顺意')

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
    identity = models.IntegerField(verbose_name='用户身份', choices=Identity_choices.choices, null=True, blank=True)
    
    phone = models.CharField(verbose_name='手机号', max_length=11)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True) 
    update_time = models.DateTimeField(verbose_name='修改时间', auto_now=True)
    is_active = models.BooleanField(verbose_name='是否激活', default=True)


    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = "用户"
