from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from user.models import *
from product.models import *


class Order(models.Model):
    class Status_choices(models.IntegerChoices):
        cancelled = 0, _('已取消')
        pending_payment = 1, _('待付款')
        pending_shipment = 2, _('待发货')
        pending_receipt = 3, _('待收货')
        finished = 4, _('已完成')
        refund = 5, _('退款/售后中')
        refund_fin = 6, _('完成退款/售后')

    # STATUS_CHOICES = [
    #     ('cancelled', '已取消'),
    #     ('pending_payment', '待付款'),
    #     ('pending_shipment', '待发货'),
    #     ('pending_receipt', '待收货'),
    #     ('refund_after_sale', '退款/售后')
    # ]

    order_number = models.CharField(verbose_name='订单号', null=False, max_length=50, unique=True)
    user = models.ForeignKey(verbose_name='用户', to=User, on_delete=models.CASCADE)
    total_cost = models.DecimalField(verbose_name='总金额', null=False, blank=False, 
                                max_digits=10, decimal_places=2, validators=[MinValueValidator(1)])
    
    ordered_dt = models.DateTimeField(verbose_name='下单时间', auto_now_add=True)
    paid_dt = models.DateTimeField(verbose_name='支付时间', null=True, blank=True)
    delivery_dt = models.DateTimeField(verbose_name='发货时间', null=True, blank=True)
    
    status = models.IntegerField(verbose_name='订单状态', null=False, default=1, choices=Status_choices.choices)

    recipient = models.CharField(verbose_name='收货人', max_length=15, null=False, blank=False)
    phone = models.CharField(verbose_name='手机号', max_length=11, null=False, blank=False)
    detailed_address = models.TextField(verbose_name='详细地址', null=False, blank=False)

    tracking_number = models.CharField(verbose_name='快递单号', null=True, blank=False, max_length=255)

    def __str__(self):
        return self.order_number

    class Meta:
        verbose_name = "订单"
        verbose_name_plural = "订单"



class Cart(models.Model):
    Type_choices = [
        ('挚礼', '挚礼'),
        ('珠', '珠'),
        ('手链', '手链'),
    ]
    user = models.ForeignKey(verbose_name='用户', to=User, on_delete=models.CASCADE)
    
    typ = models.CharField(verbose_name='类别', max_length=20, default='挚礼',
                           choices=Type_choices, null=False, blank=False)
    gemstone = models.ForeignKey(verbose_name='珠', to=Gemstone, 
                                 null=True, blank=True, on_delete=models.SET_NULL)
    bracelet = models.ForeignKey(verbose_name='链', to=Bracelet, 
                                 null=True, blank=True, on_delete=models.SET_NULL)
    gift = models.ForeignKey(verbose_name='挚礼', to=Gift, 
                                 null=True, blank=True, on_delete=models.SET_NULL)
    
    component = models.CharField(verbose_name='组成', max_length=200, null=False, blank=False,
                                 validators=[Items_Validator_component])
    quantity = models.IntegerField(verbose_name='数量', null=False, blank=False, validators=[MinValueValidator(0)])
    cost = models.DecimalField(verbose_name='金额', null=False, blank=False, 
                                max_digits=10, decimal_places=2, validators=[MinValueValidator(1)])

    # 未下单 -- 作为传统意义的购物车项，删除直接删
    # 已下单 -- 作为订单内容
        # 完成订单
    is_ordered = models.BooleanField(verbose_name='是否下单', null=False, blank=False, default=False)
    order = models.ForeignKey(verbose_name='所属订单', to=Order, null=True, on_delete=models.PROTECT)

    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True) 

    def __str__(self):
        return f"{self.user.name} - {self.create_time}"

    class Meta:
        verbose_name = "购物车"
        verbose_name_plural = "购物车"


class CartSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='typ')
    product_id = serializers.SerializerMethodField()
    pic = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    intro = serializers.SerializerMethodField()

    def get_product_id(self, obj):
        if obj.gemstone is not None:
            return obj.gemstone.id
        elif obj.bracelet is not None:
            return obj.bracelet.id
        elif obj.gift is not None:
            return obj.gift.id
        else:
            return None
    
    def get_pic(self, obj):
        if obj.gemstone is not None:
            return str(obj.gemstone.pic)
        elif obj.bracelet is not None:
            return str(obj.bracelet.pic)
        elif obj.gift is not None:
            return str(obj.gift.pic)
        else:
            return None
    
    def get_name(self, obj):
        if obj.gemstone is not None:
            return obj.gemstone.name
        elif obj.bracelet is not None:
            return obj.bracelet.name
        elif obj.gift is not None:
            return obj.gift.name
        else:
            return None

    def get_intro(self, obj):
        if obj.gemstone is not None:
            return obj.gemstone.intro
        elif obj.bracelet is not None:
            return obj.bracelet.intro
        elif obj.gift is not None:
            return obj.gift.intro
        else:
            return None

    class Meta:
        model = Cart
        fields = ['id', 'type', 'product_id', 'name', 'pic', 'intro', 'component', 'quantity', 'cost']
        # fields = ['id', 'type', 'product_id', 'name', 'intro', 'quantity', 'cost']
        # exclude = ['user', 'evalcontent']



class OrderSerializer1(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()

    def get_status(self, obj):
        sta_choices = ['已取消', '待付款', '待发货', '待收货', '已完成', '退款/售后中', '完成退款/售后']
        return sta_choices[int(obj.status)]
    
    def get_items(self, obj):
        cart_found = Cart.objects.filter(order_id=obj.id)
        serializer = CartSerializer(instance=cart_found, many=True)            
        return list(serializer.data)
    
    class Meta:
        model = Order
        # fields = '__all__'
        # fields = ['id', 'type', 'product_id', 'name', 'pic', 'intro', 'component', 'quantity', 'cost']
        # exclude = ['user', 'evalcontent']
        fields = ['id', 'order_number', 'total_cost', 'status', 'items']


class OrderSerializer2(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()

    def get_status(self, obj):
        sta_choices = ['已取消', '待付款', '待发货', '待收货', '已完成', '退款/售后中', '完成退款/售后']
        return sta_choices[int(obj.status)]
    
    def get_items(self, obj):
        cart_found = Cart.objects.filter(order_id=obj.id)
        serializer = CartSerializer(instance=cart_found, many=True)            
        return list(serializer.data)
    
    class Meta:
        model = Order
        # fields = '__all__'
        # fields = ['id', 'type', 'product_id', 'name', 'pic', 'intro', 'component', 'quantity', 'cost']
        exclude = ['user']
        # fields = ['id', 'order_number', 'total_cost', 'status', 'items']


# class Coupontype(models.Model):
#     name = models.CharField(verbose_name='名称', max_length=30, null=False)
#     discount = models.CharField(verbose_name='折扣方式', max_length=50, null=False)

#     def __str__(self):
#         return self.description + '-' + self.discount
    
#     class Meta:
#         verbose_name = "优惠券类型"
#         verbose_name_plural = "优惠券类型"


# class Coupon(models.Model):
#     user = models.ForeignKey(verbose_name='用户', to=User, on_delete=models.CASCADE)
#     coupontype = models.ForeignKey(verbose_name='优惠券类型', to=Coupontype, on_delete=models.CASCADE)
#     ddl = models.DateTimeField(verbose_name='创建时间', null=True) 

#     def __str__(self):
#         return self.user.name + '-' + self.coupontype.name

#     class Meta:
#         verbose_name = "优惠券拥有情况"
#         verbose_name_plural = "优惠券拥有情况"



# class Refund(models.Model):
#     class Type_choices(models.IntegerChoices):
#         refund = 0, _('退货退款')
#         change = 1, _('换货')

#     order = models.ForeignKey(verbose_name='所属订单', to=Order, on_delete=models.CASCADE)
#     reason = models.TextField(verbose_name='退货理由', null=False, blank=False)
#     typ = models.IntegerField(verbose_name='类别', choices=Type_choices.choices, null=False, blank=False)
#     pic = models.ImageField(verbose_name='图片', null=True, blank=True,
#                             upload_to='refund/')

