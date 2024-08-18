from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from user.models import User

# Create your models here.
class Evalcontent(models.Model):
    
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
        up = 1, _('选项一')
        down = 2, _('选项二')

    # class Wish_choices(models.IntegerChoices):
    #     career = 1, _('事业')
    #     study = 2, _('学业')
    #     wealth = 3, _('财富')
    #     love = 4, _('爱情')
    #     health = 5, _('健康')
    #     safety = 6, _('安全')
    #     family = 7, _('家庭')
    #     happiness = 8, _('快乐')
    #     shunyi = 9, _('万事顺意')

    user = models.ForeignKey(verbose_name='用户', to=User, on_delete=models.CASCADE)
    forself = models.BooleanField(verbose_name='为自己测', default=True)

    # 基本信息
    name = models.CharField(verbose_name='被测人姓名', max_length=15, null=False)
    gender = models.IntegerField(verbose_name='性别', choices=Gender_choices.choices, null=False)
    birthdt = models.DateTimeField(verbose_name='出生时间', null=False)
    birthloc = models.CharField(verbose_name='出生地', max_length=30, null=True)
    liveloc = models.CharField(verbose_name='现居地', max_length=30, null=True)
    job = models.CharField(verbose_name='职业', max_length=15, null=True)
    belief = models.IntegerField(verbose_name='信仰', choices=Belief_choices.choices, null=True)
    mood = models.IntegerField(verbose_name='心情', choices=Mood_choices.choices, null=True)

    # 性格测评
    question1 = models.IntegerField(verbose_name='问题1', choices=Question_choices_two.choices, null=True)
    question2 = models.IntegerField(verbose_name='问题2', choices=Question_choices_two.choices, null=True)
    question3 = models.IntegerField(verbose_name='问题3', choices=Question_choices_two.choices, null=True)
    question4 = models.IntegerField(verbose_name='问题4', choices=Question_choices_two.choices, null=True)
    wish = models.CharField(verbose_name='心愿', max_length=9, null=False)

    bazi = models.CharField(verbose_name='八字', max_length=200, null=False)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True) 
    update_time = models.DateTimeField(verbose_name='修改时间', auto_now=True)


    def __str__(self) -> str:
        return self.name + ' 的测评内容'

    class Meta:
        verbose_name = "测评内容"
        verbose_name_plural = "测评内容"
        unique_together = (("user", "name"),)


class EvalcontentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Evalcontent
        # fields = '__all__'
        exclude = ['user']


class Chathistory(models.Model):
    
    class Talker_choices(models.IntegerChoices):
        llm = 0, _('大模型')
        user = 1, _('用户')

    user = models.ForeignKey(verbose_name='用户', to=User, on_delete=models.CASCADE)
    talker = models.IntegerField(verbose_name='说话人', choices=Talker_choices.choices, null=False)
    msg = models.CharField(verbose_name='信息', max_length=3000, null=False)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True) 


    def __str__(self) -> str:
        return self.user.name + '_' + str(self.create_time)

    class Meta:
        verbose_name = "大模型对话记录"
        verbose_name_plural = "大模型对话记录"


class ChathistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Chathistory
        # fields = '__all__'
        fields = ['talker', 'msg', 'create_time']


class Evalreport(models.Model):
    
    class Gender_choices(models.IntegerChoices):
        male = 0, _('男')
        female = 1, _('女')
    

    user = models.ForeignKey(verbose_name='用户', to=User, on_delete=models.CASCADE)
    evalcontent = models.OneToOneField(verbose_name='测评内容', to=Evalcontent, on_delete=models.PROTECT)

    # 报告内容
    title = models.CharField(verbose_name='标题', max_length=50, null=False)
    overall = models.CharField(verbose_name='整体解读', max_length=2000, null=False)
    wish = models.CharField(verbose_name='心愿', max_length=1000, null=False)
    advice = models.CharField(verbose_name='建议', max_length=1000, null=False)

    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True) 
    update_time = models.DateTimeField(verbose_name='修改时间', auto_now=True)


    def __str__(self) -> str:
        return self.evalcontent.name + ' 的测评报告'

    class Meta:
        verbose_name = "测评报告"
        verbose_name_plural = "测评报告"


class EvalreportSerializer1(serializers.ModelSerializer):
    report_id = serializers.IntegerField(source='id')
    name = serializers.CharField(source='evalcontent.name')
    class Meta:
        model = Evalreport
        fields = ['report_id', 'name']
        # exclude = ['user', 'evalcontent']

class EvalreportSerializer2(serializers.ModelSerializer):
    evalcontent_id = serializers.IntegerField(source='evalcontent.id')
    name = serializers.CharField(source='evalcontent.name')
    class Meta:
        model = Evalreport
        # fields = '__all__'
        exclude = ['user', 'evalcontent']