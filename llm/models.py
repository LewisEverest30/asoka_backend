from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

from user.models import User
from product.models import Gemstone


def decode_wish(wish):
    all_wish_list = ['事业', '学业', '财富', '爱情', '健康', '安全', '家庭', '快乐', '万事顺意']
    wish_list = ['' for _ in range(3)]
    wish_list_index = 0
    for i, char in enumerate(wish):
        if int(char) == 1:
            # wish += all_wish_list[i]
            # wish += ' '
            wish_list[wish_list_index] = all_wish_list[i]
            wish_list_index += 1
    return wish_list


# todo-f pic地址可能需要调整？？
REPORT_INFO_DIC = {
    "祖母绿": {
        "enname": "Emerald",
        "symbol": "祖母绿是成长与繁荣的象征，代表仁慈与承诺，是坚韧的守护者。",
        "pic": settings.MEDIA_URL + "/report/emerald.png",
        "subtitle1": "成长",
        "subtitle2": "承诺",
        "subtitle3": "坚韧",
    },
    "翡翠": {
        "enname": "Jadeite",
        "symbol": "翡翠是和谐与自然的代表，象征着平衡与尊重，守护与责任感。",
        "pic": settings.MEDIA_URL + "/report/jadeite.png",
        "subtitle1": "平衡",
        "subtitle2": "责任",
        "subtitle3": "守护",
    },
    "金红石": {
        "enname": "Rutile",
        "symbol": "金红石是个人力量的体现，代表目标和决心，有积极能量的变革者。",
        "pic": settings.MEDIA_URL + "/report/rutile.png",
        "subtitle1": "力量",
        "subtitle2": "乐观",
        "subtitle3": "变革",    
    },
    "琥珀": {
        "enname": "Amber",
        "symbol": "琥珀象征热情与活力，代表对未知世界的好奇心和探索欲，拥有灵活的适应力。",
        "pic": settings.MEDIA_URL + "/report/amber.png",
        "subtitle1": "活力",
        "subtitle2": "探索",
        "subtitle3": "灵活",    
    },
    "绿松石": {
        "enname": "Turquoise",
        "symbol": "绿松石象征理想主义，代表对和平与共存的追求，直觉和创造力，慈悲与包容。",
        "pic": settings.MEDIA_URL + "/report/turquoise.png",
        "subtitle1": "理想",
        "subtitle2": "和平",
        "subtitle3": "慈悲",    
    },
    "海蓝石": {
        "enname": "Aquamarine",
        "symbol": "海蓝石是一种代表对世界的深刻洞察，是创造力的源泉，象征慈悲与理解。",
        "pic": settings.MEDIA_URL + "/report/aquamarine.png",
        "subtitle1": "洞察",
        "subtitle2": "慈悲",
        "subtitle3": "创造",    
    },
    "紫珍珠": {
        "enname": "Purple pearl",
        "symbol": "紫珍珠象征着冷静的智慧启迪、感性的共鸣以及内心世界的平衡。",
        "pic": settings.MEDIA_URL + "/report/purplepearl.png",
        "subtitle1": "智慧",
        "subtitle2": "共鸣",
        "subtitle3": "平衡",    
    },
    "堇青石": {
        "enname": "Cordierite",
        "symbol": "堇青石是一种代表智慧、清晰和忠诚的宝石，象征理性智慧，心灵启迪和深情厚谊。",
        "pic": settings.MEDIA_URL + "/report/cordierite.png",
        "subtitle1": "智慧",
        "subtitle2": "清晰",
        "subtitle3": "忠诚",    
    },
}


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
        # unique_together = (("user", "name", "forself"),)
        unique_together = (("user", "name"),)


class EvalcontentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Evalcontent
        # fields = '__all__'
        exclude = ['user']






class Evalreport(models.Model):
    
    class Gender_choices(models.IntegerChoices):
        male = 0, _('男')
        female = 1, _('女')
    

    user = models.ForeignKey(verbose_name='用户', to=User, on_delete=models.CASCADE)
    evalcontent = models.OneToOneField(verbose_name='测评内容', to=Evalcontent, on_delete=models.PROTECT)

    # 报告内容
    title = models.CharField(verbose_name='标题', max_length=50, null=False)
    overall_1 = models.CharField(verbose_name='整体解读-关键词1', max_length=2000, null=False, default="......")
    overall_2 = models.CharField(verbose_name='整体解读-关键词2', max_length=2000, null=False, default="......")
    overall_3 = models.CharField(verbose_name='整体解读-关键词3', max_length=2000, null=False, default="......")

    # todo-f 等待llm对齐字段wish1,2,3
    wish_1 = models.CharField(verbose_name='心愿解读-1', max_length=1000, null=True)
    wish_2 = models.CharField(verbose_name='心愿解读-2', max_length=1000, null=True)
    wish_3 = models.CharField(verbose_name='心愿解读-3', max_length=1000, null=True)


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
    template = serializers.SerializerMethodField()
    wish_list = serializers.SerializerMethodField()
    overall_1 = serializers.SerializerMethodField()
    overall_2 = serializers.SerializerMethodField()
    overall_3 = serializers.SerializerMethodField()

    def get_template(self, obj):
        default_value = {
            "enname": "",
            "symbol": "",
            "pic": "",
            "subtitle1": "整体解读",
            "subtitle2": "心愿",
            "subtitle3": "建议",
        }
        tpl = REPORT_INFO_DIC.get(obj.title, default_value)
        return tpl

    # todo-f 三个心愿
    def get_wish_list(self, obj):
        wish_list = decode_wish(obj.evalcontent.wish)
        detail_list = [obj.wish_1, obj.wish_2, obj.wish_3]

        wish_list_return = []
        for i, w in enumerate(wish_list):
            if w == '':
                break
            
            index = detail_list[i].find("$")
            wish_list_return.append(
                {
                    'wish': wish_list[i],
                    'wenyan': detail_list[i][:index],
                    'baihua': detail_list[i][index+1:]
                }
            )

        return wish_list_return
        
    def get_overall_1(self, obj):
        overall = obj.overall_1
        index = overall.find("$")
        ret = {
            'wenyan': overall[:index],
            'baihua': overall[index+1:]
        }
        return ret
    def get_overall_2(self, obj):
        overall = obj.overall_2
        index = overall.find("$")
        ret = {
            'wenyan': overall[:index],
            'baihua': overall[index+1:]
        }
        return ret
    def get_overall_3(self, obj):
        overall = obj.overall_3
        index = overall.find("$")
        ret = {
            'wenyan': overall[:index],
            'baihua': overall[index+1:]
        }
        return ret



    class Meta:
        model = Evalreport
        # fields = '__all__'
        exclude = ['user', 'evalcontent', 'wish_1', 'wish_2', 'wish_3']





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
    type = serializers.SerializerMethodField()

    def get_type(self, obj):
        return 0
    
    class Meta:
        model = Chathistory
        # fields = '__all__'
        fields = ['talker', 'msg', 'create_time', 'type']





class Advice(models.Model):
    user = models.ForeignKey(verbose_name='用户', to=User, on_delete=models.CASCADE)
    person_name = models.CharField(verbose_name='人名', max_length=15, null=False, blank=False)

    gem_name = models.CharField(verbose_name='珠名称', max_length=20, null=False, blank=False)
    
    mark = models.IntegerField(verbose_name='匹配度',  null=False, blank=False,
                               validators=[MinValueValidator(0), MaxValueValidator(100)])
    reason = models.CharField(verbose_name='解释', max_length=1000, null=False, blank=False, default='')

    # def __str__(self):
    #     return f"{self.person_name} - {self.gem_name}"

    class Meta:
        verbose_name = "珠推荐"
        verbose_name_plural = "珠推荐"
        unique_together = (("user", "person_name", "gem_name"),)


class AdviceSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()
    symbol = serializers.SerializerMethodField()

    def get_symbol(self, obj):
        gem = Gemstone.objects.filter(name=obj.gem_name)
        if gem.count() == 0:
            return ''
        else:
            # print(gem[0].symbol)
            return gem[0].symbol


    def get_thumbnail(self, obj):
        gem = Gemstone.objects.filter(name=obj.gem_name)
        if gem.count() == 0:
            return ''
        else:
            # print(gem[0].thumbnail)
            return str(gem[0].thumbnail)
    
    class Meta:
        model = Advice
        exclude = ['user', 'person_name']