from django.db import models
from django.core.validators import MinValueValidator, RegexValidator
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

items_pattern = r'^(\d+\*[^\|]+\|)*(\d+\*[^\|]+)$'

# item_pattern = r'^\d+\*[^\|]+$'
# items_pattern = r'^({item_pattern}\|)*{item_pattern}$'.format(item_pattern=item_pattern)

Items_Validator = RegexValidator(items_pattern, '请用这样的格式来表示产品的组成: 3*塑料石|2*蓝宝石|1*玉髓手环')


# Create your models here.
class Component(models.Model):
    
    class Type_choices(models.IntegerChoices):
        zhu = 0, _('珠')
        lian = 1, _('链')
        qita = 2, _('其他')
    
    name = models.CharField(verbose_name='名称', max_length=10, null=False, blank=False)
    typ = models.IntegerField(verbose_name='类别', choices=Type_choices.choices, null=False, blank=False)
    pic = models.ImageField(verbose_name='图片', null=False, blank=False,
                            upload_to='component/')
    loc = models.CharField(verbose_name='产地', max_length=50, null=False, blank=False)
    intro = models.TextField(verbose_name='介绍', null=False, blank=False)
    price = models.DecimalField(verbose_name='单价', null=False, blank=False, max_digits=7, decimal_places=2,
                                validators=[MinValueValidator(1)])

    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "零件"
        verbose_name_plural = "零件"



class Product(models.Model):
    
    name = models.CharField(verbose_name='名称', max_length=10, null=False, blank=False)
    pic = models.ImageField(verbose_name='图片', null=False, blank=False,
                            upload_to='product/')
    intro = models.TextField(verbose_name='介绍', null=False, blank=False)
    price = models.DecimalField(verbose_name='单价', null=False, blank=False, max_digits=7, decimal_places=2,
                                validators=[MinValueValidator(1)])
    sales = models.IntegerField(verbose_name='销量', default=0, null=False, blank=False)
    component = models.CharField(verbose_name='零件组成\n示例：3*塑料石|2*蓝宝石|1*玉髓手环', max_length=200, null=False, blank=False,
                                 validators=[Items_Validator])

    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "成品"
        verbose_name_plural = "成品"