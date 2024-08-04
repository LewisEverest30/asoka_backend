from django.db import models
from django.core.validators import MinValueValidator, RegexValidator
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

items_pattern = r'^(\d+\*[^\|]+\|)*(\d+\*[^\|]+)$'
Items_Validator = RegexValidator(items_pattern, '请用这样的格式来表示产品的组成: 3*塑料石|2*蓝宝石|1*玉髓手环')

# Create your models here.
class Gemstone(models.Model):
    
    Type_choices = [
        ('宝石', '宝石'),
        ('其他', '其他'),
    ]

    
    Symbol_choices = [
        ('财运', '财运'),
        ('姻缘', '姻缘'),
        ('健康', '健康'),
        ('学业', '学业'),
        ('事业', '事业'),
        ('好运', '好运'),
    ]

    Mat_choices = [
        ('玛瑙', '玛瑙'),

        ('其他', '其他'),
    ]

    name = models.CharField(verbose_name='名称', max_length=20, null=False, blank=False)
    typ = models.CharField(verbose_name='类别', max_length=20, 
                           choices=Type_choices, null=False, blank=False)
    
    symbol = models.CharField(verbose_name='寓意', max_length=20, 
                           choices=Symbol_choices, null=False, blank=False)
    
    material = models.CharField(verbose_name='材料', max_length=50, 
                        #    choices=Mat_choices, 
                           null=False, blank=False)
    
    cover = models.ImageField(verbose_name='封面图片（其他图片在下方关联模型里添加）', null=False, blank=False,
                            upload_to='gemstone/')
    
    detail = models.ImageField(verbose_name='详细介绍（长图）', null=False, blank=False,
                            upload_to='gemstone/')
    
    loc = models.CharField(verbose_name='产地', max_length=50, null=False, blank=False)
    intro = models.TextField(verbose_name='介绍', null=False, blank=False)
    price = models.DecimalField(verbose_name='单价', null=False, blank=False, max_digits=7, decimal_places=2,
                                validators=[MinValueValidator(1)])

    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "珠"
        verbose_name_plural = "珠"

class GemstonePic(models.Model):
    gemstone = models.ForeignKey(verbose_name='对应的珠', to=Gemstone, 
                                 null=False, blank=False, on_delete=models.CASCADE)
    pic = models.ImageField(verbose_name='图片', null=False, blank=False,
                            upload_to='gemstonepic/')

class GemstonePicSerializer(serializers.ModelSerializer):
    class Meta:
        model = GemstonePic

class GemstoneSerializer1(serializers.ModelSerializer):
    type = serializers.CharField(source='typ')
    class Meta:
        model = Gemstone
        fields = ['id', 'name', 'type', 'cover']
        # exclude = ['user', 'evalcontent']

class GemstoneSerializer2(serializers.ModelSerializer):
    type = serializers.CharField(source='typ')
    pics = serializers.SerializerMethodField()
    
    def get_pics(self, obj):
        found = GemstonePic.objects.filter(gemstone_id=obj.id)
        if found.count() > 0:
            serializer = GemstonePicSerializer(instance=found, many=True)            
            return serializer.data
        else:
            return None

    class Meta:
        model = Gemstone
        exclude = ['typ']



# Create your models here.
class Bracelet(models.Model):
    
    Type_choices = [
        ('单圈', '单圈'),
        ('双圈', '双圈'),
        ('其他', '其他'),
    ]

    
    Symbol_choices = [
        ('财运', '财运'),
        ('姻缘', '姻缘'),
        ('健康', '健康'),
        ('学业', '学业'),
        ('事业', '事业'),
        ('好运', '好运'),
    ]

    Mat_choices = [
        ('玛瑙', '玛瑙'),

        ('其他', '其他'),
    ]

    name = models.CharField(verbose_name='名称', max_length=20, null=False, blank=False)
    typ = models.CharField(verbose_name='类别', max_length=20, 
                           choices=Type_choices, null=False, blank=False)
    
    symbol = models.CharField(verbose_name='寓意', max_length=20, 
                           choices=Symbol_choices, null=False, blank=False)
    
    material = models.CharField(verbose_name='材料', max_length=50, 
                        #    choices=Mat_choices, 
                           null=False, blank=False)
    
    cover = models.ImageField(verbose_name='封面图片（其他图片在下方关联模型里添加）', null=False, blank=False,
                            upload_to='bracelet/')
    
    detail = models.ImageField(verbose_name='详细介绍（长图）', null=False, blank=False,
                            upload_to='bracelet/')
    
    loc = models.CharField(verbose_name='产地', max_length=50, null=False, blank=False)
    intro = models.TextField(verbose_name='介绍', null=False, blank=False)
    price = models.DecimalField(verbose_name='单价', null=False, blank=False, max_digits=7, decimal_places=2,
                                validators=[MinValueValidator(1)])

    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "手链"
        verbose_name_plural = "手链"

class BraceletPic(models.Model):
    bracelet = models.ForeignKey(verbose_name='对应的手链', to=Bracelet, 
                                 null=False, blank=False, on_delete=models.CASCADE)
    pic = models.ImageField(verbose_name='图片', null=False, blank=False,
                            upload_to='braceletpic/')

class BraceletPicSerializer(serializers.ModelSerializer):
    class Meta:
        model = BraceletPic


class BraceletSerializer1(serializers.ModelSerializer):
    type = serializers.CharField(source='typ')
    class Meta:
        model = Bracelet
        fields = ['id', 'name', 'type', 'cover']
        # exclude = ['user', 'evalcontent']

class BraceletSerializer2(serializers.ModelSerializer):
    type = serializers.CharField(source='typ')
    pics = serializers.SerializerMethodField()
    
    def get_pics(self, obj):
        found = BraceletPic.objects.filter(bracelet_id=obj.id)
        if found.count() > 0:
            serializer = BraceletPicSerializer(instance=found, many=True)            
            return serializer.data
        else:
            return None

    class Meta:
        model = Bracelet
        exclude = ['typ']



class Gift(models.Model):

    Type_choices = [
        ('财运', '财运'),
        ('姻缘', '姻缘'),
        ('健康', '健康'),
        ('学业', '学业'),
        ('事业', '事业'),
        ('好运', '好运'),

    ]

    # class Type_choices(models.CharChoices):
    #     cai = 1, _('财运')
    #     yin = 2, _('姻缘')
    #     jian = 3, _('健康')
    #     xue = 4, _('学业')
    #     shi = 5, _('事业')
    #     hao = 6, _('好运')
    
    name = models.CharField(verbose_name='名称', max_length=20, null=False, blank=False)
    # typ = models.IntegerField(verbose_name='类别', choices=Type_choices.choices, null=False, blank=False)
    typ = models.CharField(verbose_name='寓意', max_length=20, 
                           choices=Type_choices, null=False, blank=False)

    cover = models.ImageField(verbose_name='封面图片（其他图片在下方关联模型里添加）', null=False, blank=False,
                            upload_to='gift/')
    
    intro = models.CharField(verbose_name='简介', max_length=100, null=False, blank=False)
    detail = models.ImageField(verbose_name='详细介绍（长图）', null=False, blank=False,
                            upload_to='gift/')
    price = models.DecimalField(verbose_name='单价', null=False, blank=False, max_digits=7, decimal_places=2,
                                validators=[MinValueValidator(1)])
    sales = models.IntegerField(verbose_name='销量', default=0, null=False, blank=False, validators=[MinValueValidator(0)])
    component = models.CharField(verbose_name='组成\n (示例: 3*塑料石|2*蓝宝石|1*玉髓手环)', max_length=200, null=False, blank=False,
                                 validators=[Items_Validator])

    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "挚礼"
        verbose_name_plural = "挚礼"

class GiftPic(models.Model):
    gift = models.ForeignKey(verbose_name='对应的挚礼', to=Gift, 
                                 null=False, blank=False, on_delete=models.CASCADE)
    pic = models.ImageField(verbose_name='图片', null=False, blank=False,
                            upload_to='giftpic/')

class GiftPicSerializer(serializers.ModelSerializer):
    class Meta:
        model = GiftPic

class GiftSerializer1(serializers.ModelSerializer):
    type = serializers.CharField(source='typ')
    class Meta:
        model = Gift
        fields = ['id', 'name', 'type', 'cover', 'intro', 'price', 'sales']
        # exclude = ['user', 'evalcontent']

class GiftSerializer2(serializers.ModelSerializer):
    type = serializers.CharField(source='typ')
    pics = serializers.SerializerMethodField()
    
    def get_pics(self, obj):
        found = GiftPic.objects.filter(gift_id=obj.id)
        if found.count() > 0:
            serializer = GiftPicSerializer(instance=found, many=True)            
            return serializer.data
        else:
            return None


    class Meta:
        model = Gift
        exclude = ['typ']
