from django.db import models
from django.core.validators import MinValueValidator, RegexValidator
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from user.models import *

# pattern_component = r'^(\d+\*[^\|\*]+\|)*(\d+\*[^\|\*]+)$'
pattern_component = r'^(\d+\*(珠|手链)\-\d+ )*(\d+\*(珠|手链)\-\d+)$'
# Items_Validator_component = RegexValidator(pattern_component, '请用这样的格式来表示产品的组成: 3*塑料石|2*蓝宝石|1*玉髓手环')
Items_Validator_component = RegexValidator(pattern_component, '请用这样的格式来表示产品的组成: 个数*珠/手链-id 个数*珠/手链-id。例如: 3*珠-1 2*珠-2 1*手链-1')


pattern_symbol = r'^(财运|姻缘|健康|学业|事业|转运|平安|解忧)( (财运|姻缘|健康|学业|事业|转运|平安|解忧))*$'
Items_Validator_symbol = RegexValidator(pattern_symbol, '请用这样的格式来表示寓意: 健康 学业 事业。\n可选的寓意有: 财运、姻缘、健康、学业、事业、转运、平安、解忧。')

pattern_structure = r'^(1|2|3|4)( (1|2|3|4))*$'
Items_Validator_structure = RegexValidator(pattern_structure, "从顶珠开始顺时针记录, 用数字表示该位置的珠子类型, 空格分隔, 顶珠-1、腰珠-2、子珠-3、配珠-4 \n  \
                                    例如: 1 2 3 2 3 2 3 2 3 2 3 2 3 2")



# 珠 模型
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
    Wu_choices = [
        ('金', '金'),
        ('木', '木'),
        ('水', '水'),
        ('火', '火'),
        ('土', '土'),
    ]
    Pos_choices = [
        ('顶珠', '顶珠'),
        ('腰珠', '腰珠'),
        ('子珠', '子珠'),
        ('配珠', '配珠'),
        ('其他', '其他'),
    ]


    name = models.CharField(verbose_name='名称', max_length=20, null=False, blank=False, db_index=True)
    typ = models.CharField(verbose_name='类别', max_length=20, 
                           choices=Type_choices, null=False, blank=False)
    
    symbol = models.CharField(verbose_name='寓意', max_length=50, 
                        #    choices=Symbol_choices, 
                           help_text='请用这样的格式来表示寓意: 健康 学业 事业。\n可选的寓意有: 财运、姻缘、健康、学业、事业、转运、平安、解忧。',
                           validators=[Items_Validator_symbol],
                           null=True, blank=False)
    
    wuxing = models.CharField(verbose_name='五行/色系', max_length=20, 
                           choices=Wu_choices, null=True, blank=False)
    
    material = models.CharField(verbose_name='材料', max_length=50, 
                        #    choices=Mat_choices, 
                           null=True, blank=False)
    
    position = models.CharField(verbose_name='位置', max_length=20, 
                           choices=Pos_choices, 
                           null=True, blank=False)
    size = models.IntegerField(verbose_name='尺寸（单位：毫米）', null=True, blank=True, validators=[MinValueValidator(0)])

    cover = models.ImageField(verbose_name='封面图片（其他图片在下方产品摄影里添加）', null=True, blank=False,
                            upload_to='gemstone/')
    thumbnail = models.ImageField(verbose_name='缩略图', null=True, blank=False,
                            upload_to='gemstone/thumbnail/')
    detail = models.ImageField(verbose_name='详细介绍（长图）', null=True, blank=False,
                            upload_to='gemstone/')
    
    loc = models.CharField(verbose_name='产地', max_length=50, null=False, blank=False)
    intro = models.TextField(verbose_name='介绍', null=False, blank=False)
    price = models.DecimalField(verbose_name='单价', null=False, blank=False, max_digits=7, decimal_places=2,
                                validators=[MinValueValidator(1)])
    
    is_recommended = models.BooleanField(verbose_name="是否为推荐商品", null=False, blank=False, default=False)
    inventory = models.IntegerField(verbose_name='库存数量', null=False, blank=False, default=0, validators=[MinValueValidator(0)])

    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True, null=True) 
    update_time = models.DateTimeField(verbose_name='修改时间', auto_now=True, null=True)


    def __str__(self):
        return self.name + '_' + self.position + '_' + str(self.size) + 'mm'
    class Meta:
        verbose_name = "珠"
        verbose_name_plural = "珠"


# 手链 模型
class Bracelet(models.Model):
    Type_choices = [
        # ('单圈', '单圈'),
        # ('双圈', '双圈'),
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
    Wu_choices = [
        ('金', '金'),
        ('木', '木'),
        ('水', '水'),
        ('火', '火'),
        ('土', '土'),
    ]

    name = models.CharField(verbose_name='名称', max_length=20, null=False, blank=False)
    typ = models.CharField(verbose_name='类别', max_length=20, 
                           choices=Type_choices, null=False, blank=False)
    
    symbol = models.CharField(verbose_name='寓意', max_length=50, 
                        #    choices=Symbol_choices, 
                           help_text='请用这样的格式来表示寓意: 健康 学业 事业。\n可选的寓意有: 财运、姻缘、健康、学业、事业、转运、平安、解忧。',
                           validators=[Items_Validator_symbol],
                           null=True, blank=False)
    
    wuxing = models.CharField(verbose_name='五行/色系', max_length=20, 
                           choices=Wu_choices, null=True, blank=False)

    material = models.CharField(verbose_name='材料', max_length=50, 
                        #    choices=Mat_choices, 
                           null=True, blank=False)
    size = models.IntegerField(verbose_name='尺寸', null=True, blank=True, validators=[MinValueValidator(0)])
   
    cover = models.ImageField(verbose_name='封面图片（其他图片在下方产品摄影里添加）', null=True, blank=False,
                            upload_to='bracelet/')
    thumbnail = models.ImageField(verbose_name='缩略图', null=True, blank=False,
                            upload_to='bracelet/thumbnail/')
    detail = models.ImageField(verbose_name='详细介绍（长图）', null=True, blank=False,
                            upload_to='bracelet/')
    
    loc = models.CharField(verbose_name='产地', max_length=50, null=False, blank=False)
    intro = models.TextField(verbose_name='介绍', null=False, blank=False)
    price = models.DecimalField(verbose_name='单价', null=False, blank=False, max_digits=7, decimal_places=2,
                                validators=[MinValueValidator(1)])
    
    is_recommended = models.BooleanField(verbose_name="是否为推荐商品", null=False, blank=False, default=False)
    inventory = models.IntegerField(verbose_name='库存数量', null=False, blank=False, default=0, validators=[MinValueValidator(0)])

    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True, null=True) 
    update_time = models.DateTimeField(verbose_name='修改时间', auto_now=True, null=True)


    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "手链"
        verbose_name_plural = "手链"


# 印章 模型
class Stamp(models.Model):
    Type_choices = [
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
    Wu_choices = [
        ('金', '金'),
        ('木', '木'),
        ('水', '水'),
        ('火', '火'),
        ('土', '土'),
    ]

    name = models.CharField(verbose_name='名称', max_length=20, null=False, blank=False)
    typ = models.CharField(verbose_name='类别', max_length=20, 
                           choices=Type_choices, null=False, blank=False)
    
    symbol = models.CharField(verbose_name='寓意', max_length=50, 
                        #    choices=Symbol_choices, 
                           help_text='请用这样的格式来表示寓意: 健康 学业 事业。\n可选的寓意有: 财运、姻缘、健康、学业、事业、转运、平安、解忧。',
                           validators=[Items_Validator_symbol],
                           null=True, blank=False)
    
    wuxing = models.CharField(verbose_name='五行/色系', max_length=20, 
                           choices=Wu_choices, null=True, blank=False)

    material = models.CharField(verbose_name='材料', max_length=50, 
                        #    choices=Mat_choices, 
                           null=True, blank=False)
    size = models.IntegerField(verbose_name='尺寸', null=True, blank=True, validators=[MinValueValidator(0)])


    size = models.IntegerField(verbose_name='尺寸（单位：毫米）', null=True, blank=True, validators=[MinValueValidator(0)])

    cover = models.ImageField(verbose_name='封面图片（其他图片在下方产品摄影里添加）', null=True, blank=False,
                            upload_to='stamp/')
    thumbnail = models.ImageField(verbose_name='缩略图', null=True, blank=False,
                            upload_to='stamp/thumbnail/')
    detail = models.ImageField(verbose_name='详细介绍（长图）', null=True, blank=False,
                            upload_to='stamp/')
    
    loc = models.CharField(verbose_name='产地', max_length=50, null=False, blank=False)
    intro = models.TextField(verbose_name='介绍', null=False, blank=False)
    price = models.DecimalField(verbose_name='单价', null=False, blank=False, max_digits=7, decimal_places=2,
                                validators=[MinValueValidator(1)])
    
    is_recommended = models.BooleanField(verbose_name="是否为推荐商品", null=False, blank=False, default=False)
    inventory = models.IntegerField(verbose_name='库存数量', null=False, blank=False, default=0, validators=[MinValueValidator(0)])

    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True, null=True) 
    update_time = models.DateTimeField(verbose_name='修改时间', auto_now=True, null=True)


    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "印章"
        verbose_name_plural = "印章"


# 挚礼 模型
class Gift(models.Model):
    Type_choices = [
        ('财运', '财运'),
        ('姻缘', '姻缘'),
        ('健康', '健康'),
        ('学业', '学业'),
        ('事业', '事业'),
        ('好运', '好运'),
    ]
    Wu_choices = [
        ('金', '金'),
        ('木', '木'),
        ('水', '水'),
        ('火', '火'),
        ('土', '土'),
    ]
    

    name = models.CharField(verbose_name='名称', max_length=20, null=False, blank=False)
    
    symbol = models.CharField(verbose_name='寓意', max_length=50, 
                        #    choices=Symbol_choices, 
                           help_text='请用这样的格式来表示寓意: 健康 学业 事业。\n可选的寓意有: 财运、姻缘、健康、学业、事业、转运、平安、解忧。',
                           validators=[Items_Validator_symbol],
                           null=True, blank=False)
    
    wuxing = models.CharField(verbose_name='五行/色系', max_length=20, 
                           choices=Wu_choices, null=True, blank=False)
    
    cover = models.ImageField(verbose_name='封面图片（其他图片在下方产品摄影里添加）', null=True, blank=False,
                            upload_to='gift/')
    thumbnail = models.ImageField(verbose_name='缩略图', null=True, blank=False,
                            upload_to='gift/thumbnail/')
    detail = models.ImageField(verbose_name='详细介绍（长图）', null=True, blank=False,
                            upload_to='gift/')

    intro = models.TextField(verbose_name='介绍', null=False, blank=False)
    
    price = models.DecimalField(verbose_name='单价', null=False, blank=False, max_digits=7, decimal_places=2,
                                validators=[MinValueValidator(1)])
    sales = models.IntegerField(verbose_name='销量', default=0, null=False, blank=False, validators=[MinValueValidator(0)])
    
    component = models.CharField(verbose_name='组成 ', max_length=200, null=False, blank=False,
                                 help_text='请用这样的格式来表示产品的组成: 个数*珠/手链-id 个数*珠/手链-id。例如: 3*珠-1 2*珠-2 1*手链-1',
                                 validators=[Items_Validator_component])

    is_recommended = models.BooleanField(verbose_name="是否为推荐商品", null=False, blank=False, default=False)

    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True, null=True) 
    update_time = models.DateTimeField(verbose_name='修改时间', auto_now=True, null=True)


    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "挚礼"
        verbose_name_plural = "挚礼"




# 方案模板 模型
class Scheme_Template(models.Model):
    Pos_choices = [
        ('顶珠', '顶珠'),
        # ('侧珠', '侧珠'),
        ('腰珠', '腰珠'),
        ('子珠', '子珠'),
        ('配珠', '配珠'),
        ('其他', '其他'),
    ]

    name = models.CharField(verbose_name='名称', max_length=20, null=False, blank=False)
    
    is_user_defined = models.BooleanField(verbose_name='是否为用户自定义的', default=False, blank=True)
    user = models.ForeignKey(verbose_name='用户', to=User, on_delete=models.CASCADE, null=True, blank=True)
    
    # todo 是否需要区分人名。目前看不需要
    # name = models.

    dingzhu = models.IntegerField(verbose_name='顶珠个数', null=False, blank=False, default=0, validators=[MinValueValidator(0)])
    yaozhu = models.IntegerField(verbose_name='腰珠个数', null=False, blank=False, default=0, validators=[MinValueValidator(0)])
    zizhu = models.IntegerField(verbose_name='子珠个数', null=False, blank=False, default=0, validators=[MinValueValidator(0)])
    peizhu = models.IntegerField(verbose_name='配珠个数', null=False, blank=False, default=0, validators=[MinValueValidator(0)])

    structure = models.CharField(verbose_name='模板结构描述',
                                help_text="从顶珠开始顺时针记录, 用数字表示该位置的珠子类型, 空格分隔, 顶珠-1、腰珠-2、子珠-3、配珠-4。 \n  \
                                    例如: 1 2 3 2 3 2 3 2 3 2 3 2 3 2", 
                                max_length=100,
                                validators=[Items_Validator_structure],
                                null=True, blank=False)

    thumbnail = models.ImageField(verbose_name='示意图', null=True, blank=False, upload_to='scheme/thumbnail/')
    
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True, null=True) 
    update_time = models.DateTimeField(verbose_name='修改时间', auto_now=True, null=True)


    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "方案模板"
        verbose_name_plural = "方案模板"




# ----------------------------------------------------------------------------------------------------

# 珠 产品摄影
class GemstonePic(models.Model):
    gemstone = models.ForeignKey(verbose_name='对应的珠', to=Gemstone, 
                                 null=False, blank=False, on_delete=models.CASCADE)
    pic = models.ImageField(verbose_name='图片', null=False, blank=False,
                            upload_to='gemstonepic/')
    class Meta:
        verbose_name = "珠的产品摄影"
        verbose_name_plural = "珠的产品摄影"

class GemstonePicSerializer(serializers.ModelSerializer):
    class Meta:
        model = GemstonePic
        exclude = ['id', 'gemstone']


# 手链 产品摄影
class BraceletPic(models.Model):
    bracelet = models.ForeignKey(verbose_name='对应的手链', to=Bracelet, 
                                 null=False, blank=False, on_delete=models.CASCADE)
    pic = models.ImageField(verbose_name='图片', null=False, blank=False,
                            upload_to='braceletpic/')
    class Meta:
        verbose_name = "手链的产品摄影"
        verbose_name_plural = "手链的产品摄影"

class BraceletPicSerializer(serializers.ModelSerializer):
    class Meta:
        model = BraceletPic
        exclude = ['id', 'bracelet']


# 印章 产品摄影
class StampPic(models.Model):
    stamp = models.ForeignKey(verbose_name='对应的印章', to=Stamp, 
                                 null=False, blank=False, on_delete=models.CASCADE)
    pic = models.ImageField(verbose_name='图片', null=False, blank=False,
                            upload_to='stamppic/')
    class Meta:
        verbose_name = "印章的产品摄影"
        verbose_name_plural = "印章的产品摄影"

class StampPicSerializer(serializers.ModelSerializer):
    class Meta:
        model = StampPic
        exclude = ['id', 'stamp']


# 挚礼 产品摄影
class GiftPic(models.Model):
    gift = models.ForeignKey(verbose_name='对应的挚礼', to=Gift, 
                                 null=False, blank=False, on_delete=models.CASCADE)
    pic = models.ImageField(verbose_name='图片', null=False, blank=False,
                            upload_to='giftpic/')
    class Meta:
        verbose_name = "挚礼的产品摄影"
        verbose_name_plural = "挚礼的产品摄影"

class GiftPicSerializer(serializers.ModelSerializer):
    class Meta:
        model = GiftPic
        exclude = ['id', 'gift']



# --------------------------------------------------------------------------------------------

# 珠 序列化器
class GemstoneSerializer1(serializers.ModelSerializer):
    # type = serializers.CharField(source='typ')
    class Meta:
        model = Gemstone
        fields = ['id', 'name', 'symbol', 'position', 'size', 'thumbnail', 'cover', 'intro', 'price']
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
        exclude = ['typ', 'create_time', 'update_time']

class GemstoneSerializer3(serializers.ModelSerializer):
    product_type = serializers.SerializerMethodField()
    
    def get_product_type(self, obj):
        return 'gemstone'

    class Meta:
        model = Gemstone
        fields = ['product_type', 'id', 'name', 'cover', 'intro', 'price']



# 链 序列化器
class BraceletSerializer1(serializers.ModelSerializer):
    type = serializers.CharField(source='typ')
    class Meta:
        model = Bracelet
        fields = ['id', 'name', 'type', 'symbol', 'thumbnail', 'cover', 'intro', 'price']
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
        exclude = ['typ', 'create_time', 'update_time']

class BraceletSerializer3(serializers.ModelSerializer):
    product_type = serializers.SerializerMethodField()
    
    def get_product_type(self, obj):
        return 'bracelet'

    class Meta:
        model = Bracelet
        fields = ['product_type', 'id', 'name', 'cover', 'intro', 'price']


# 印章 序列化器
class StampSerializer1(serializers.ModelSerializer):
    type = serializers.CharField(source='typ')
    class Meta:
        model = Stamp
        fields = ['id', 'name', 'type', 'symbol', 'thumbnail', 'cover', 'intro', 'price']
        # exclude = ['user', 'evalcontent']

class StampSerializer2(serializers.ModelSerializer):
    type = serializers.CharField(source='typ')
    pics = serializers.SerializerMethodField()
    
    def get_pics(self, obj):
        found = StampPic.objects.filter(stamp_id=obj.id)
        if found.count() > 0:
            serializer = StampPicSerializer(instance=found, many=True)            
            return serializer.data
        else:
            return None

    class Meta:
        model = Stamp
        exclude = ['typ', 'create_time', 'update_time']

class StampSerializer3(serializers.ModelSerializer):
    product_type = serializers.SerializerMethodField()
    
    def get_product_type(self, obj):
        return 'stamp'

    class Meta:
        model = Stamp
        fields = ['product_type', 'id', 'name', 'cover', 'intro', 'price']


# 挚礼 序列化器
class GiftSerializer1(serializers.ModelSerializer):
    class Meta:
        model = Gift
        fields = ['id', 'name', 'symbol', 'cover', 'intro', 'price', 'sales']
        # exclude = ['user', 'evalcontent']

class GiftSerializer2(serializers.ModelSerializer):
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
        # fields = '__all__'
        exclude = ['create_time', 'update_time']

class GiftSerializer3(serializers.ModelSerializer):
    product_type = serializers.SerializerMethodField()
    
    def get_product_type(self, obj):
        return 'gift'

    class Meta:
        model = Gift
        fields = ['product_type', 'id', 'name', 'cover', 'intro', 'price']




# 模板 序列化器
class Scheme_TemplateSerializer1(serializers.ModelSerializer):
    # type = serializers.CharField(source='typ')
    class Meta:
        model = Scheme_Template
        # fields = []
        exclude = ['user', 'create_time', 'update_time', 'is_user_defined']
