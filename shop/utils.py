import django
import datetime
from django.forms.models import model_to_dict
from django.db import transaction

from .models import *


# 将一个Cart实例重新组织成字典
def cart_to_dict_full(cart_obj) -> dict:
    raw_dict = model_to_dict(cart_obj)
    product_obj = None
    if raw_dict['product_type'] == '珠':
        product_obj = Gemstone.objects.filter(id=raw_dict['gemstone'])[0]
    elif raw_dict['product_type'] == '手链':
        product_obj = Bracelet.objects.filter(id=raw_dict['bracelet'])[0]
    elif raw_dict['product_type'] == '印章':
        product_obj = Stamp.objects.filter(id=raw_dict['stamp'])[0]
  
    # id, thumbnail, name, loc, intro,price
    if product_obj is not None:
        raw_dict['product_id'] = product_obj.id
        raw_dict['thumbnail'] = str(product_obj.thumbnail)
        raw_dict['product_name'] = str(product_obj.name)
        raw_dict['loc'] = str(product_obj.loc)
        raw_dict['intro'] = str(product_obj.intro)
        raw_dict['price'] = str(product_obj.price)
    else:
        raw_dict['product_id'] = None
        raw_dict['thumbnail'] = None
        raw_dict['product_name'] = None
        raw_dict['loc'] = None
        raw_dict['intro'] = None
        raw_dict['price'] = None     
    
    del raw_dict['user']
    del raw_dict['gemstone']
    del raw_dict['bracelet']
    del raw_dict['stamp']
    del raw_dict['group_type']
    del raw_dict['gift_group']
    del raw_dict['scheme_group']
    del raw_dict['is_ordered']
    del raw_dict['order']

    # print(raw_dict)
    return raw_dict


# 将一个Cart实例重新组织成字典
def cart_to_dict_lite(cart_obj) -> dict:
    raw_dict = model_to_dict(cart_obj)
    product_obj = None
    if raw_dict['product_type'] == '珠':
        product_obj = Gemstone.objects.filter(id=raw_dict['gemstone'])[0]
    elif raw_dict['product_type'] == '手链':
        product_obj = Bracelet.objects.filter(id=raw_dict['bracelet'])[0]
    elif raw_dict['product_type'] == '印章':
        product_obj = Stamp.objects.filter(id=raw_dict['stamp'])[0]
  
    # id, thumbnail, name, loc, intro,price
    # 精简掉产地
    if product_obj is not None:
        raw_dict['product_id'] = product_obj.id
        raw_dict['thumbnail'] = str(product_obj.thumbnail)
        raw_dict['product_name'] = str(product_obj.name)
        raw_dict['intro'] = str(product_obj.intro)
        raw_dict['price'] = str(product_obj.price)
    else:
        raw_dict['product_id'] = None
        raw_dict['thumbnail'] = None
        raw_dict['product_name'] = None
        raw_dict['intro'] = None
        raw_dict['price'] = None     
    
    del raw_dict['user']
    del raw_dict['gemstone']
    del raw_dict['bracelet']
    del raw_dict['stamp']
    del raw_dict['group_type']
    del raw_dict['gift_group']
    del raw_dict['scheme_group']
    del raw_dict['is_ordered']
    del raw_dict['order']

    # print(raw_dict)
    return raw_dict


def Group_Carts_full(cart_items: django.db.models.query.QuerySet) -> dict:
    grouped_items = {}
    for item in cart_items:
        key = (item.group_type, item.gift_group, item.scheme_group)
        if key not in grouped_items:
            group_name = ''
            group_create_time = None
            if item.group_type == '散件':
                group_name = '散件'
                group_create_time = datetime.datetime.fromisoformat('2000-01-01T12:00:00')
            elif item.group_type == '挚礼':
                giftgroup = CartGroupGift.objects.filter(id=item.gift_group.id)
                group_name = '挚礼——' + str(giftgroup[0].gift.name)
                group_create_time = giftgroup[0].create_time
            elif item.group_type == '方案':
                schemegroup = CartGroupScheme.objects.filter(id=item.scheme_group.id)
                if schemegroup[0].typ == '基于模板':
                    group_name = str(schemegroup[0].name) + '·方案——' + str(schemegroup[0].scheme.name)                       
                else:
                    group_name = str(schemegroup[0].name) + '·方案——' + '随心自选'
                group_create_time = schemegroup[0].create_time
            grouped_items[key] = {
                'group_type': item.group_type,
                'group_title': group_name,
                'group_create_time': group_create_time,
                'carts': [],
            }
        
        grouped_items[key]['carts'].append(cart_to_dict_full(item))
    return grouped_items


def Group_Carts_lite(cart_items: django.db.models.query.QuerySet) -> dict:
    grouped_items = {}
    for item in cart_items:
        key = (item.group_type, item.gift_group, item.scheme_group)
        if key not in grouped_items:
            group_name = ''
            group_create_time = None
            if item.group_type == '散件':
                group_name = '散件'
                group_create_time = datetime.datetime.fromisoformat('2000-01-01T12:00:00')
            elif item.group_type == '挚礼':
                giftgroup = CartGroupGift.objects.filter(id=item.gift_group.id)
                group_name = '挚礼——' + str(giftgroup[0].gift.name)
                group_create_time = giftgroup[0].create_time
            elif item.group_type == '方案':
                schemegroup = CartGroupScheme.objects.filter(id=item.scheme_group.id)
                if schemegroup[0].typ == '基于模板':
                    group_name = str(schemegroup[0].name) + '·方案——' + str(schemegroup[0].scheme.name)                       
                else:
                    group_name = str(schemegroup[0].name) + '·方案——' + '随心自选'
                group_create_time = schemegroup[0].create_time
            grouped_items[key] = {
                'group_type': item.group_type,
                'group_title': group_name,
                'group_create_time': group_create_time,
                'carts': [],
            }
        
        grouped_items[key]['carts'].append(cart_to_dict_lite(item))
    return grouped_items



def Check_Update_Inventory(cart_items: django.db.models.query.QuerySet):
    # 合并产品购买数量
    gem_integrated_items = {}   # id: quantity
    brace_integrated_items = {}
    stamp_integrated_items = {}
    for item in cart_items:
        if item.product_type == '珠':
            key = item.gemstone.id
            if key not in gem_integrated_items:
                gem_integrated_items[key] = int(item.quantity)
            else:
                gem_integrated_items[key] += int(item.quantity)
        elif item.product_type == '手链':
            key = item.bracelet.id
            if key not in brace_integrated_items:
                brace_integrated_items[key] = int(item.quantity)
            else:
                brace_integrated_items[key] += int(item.quantity)
        elif item.product_type == '印章':
            key = item.stamp.id
            if key not in stamp_integrated_items:
                stamp_integrated_items[key] = int(item.quantity)
            else:
                stamp_integrated_items[key] += int(item.quantity)

        # key = (item.product_type, item.gemstone, item.barcelet, item.stamp)

    with transaction.atomic():
        gem_found = Gemstone.objects.select_for_update().filter(id__in=list(gem_integrated_items.keys()))
        brace_found = Bracelet.objects.select_for_update().filter(id__in=list(brace_integrated_items.keys()))
        stamp_found = Stamp.objects.select_for_update().filter(id__in=list(stamp_integrated_items.keys()))

        for item in gem_found:
            if item.inventory < gem_integrated_items[item.id]:  # 库存量 < 下单量
                raise ValueError("珠"+str(item.id)+"库存不足")
            item.inventory -= gem_integrated_items[item.id]  # 更新库存量
            item.save()

        for item in brace_found:
            if item.inventory < brace_integrated_items[item.id]:  # 库存量 < 下单量
                raise ValueError("手链"+str(item.id)+"库存不足")
            item.inventory -= brace_integrated_items[item.id]  # 更新库存量
            item.save()
        
        for item in stamp_found:
            if item.inventory < stamp_integrated_items[item.id]:  # 库存量 < 下单量
                raise ValueError("印章"+str(item.id)+"库存不足")
            item.inventory -= stamp_integrated_items[item.id]  # 更新库存量
            item.save()


def Recover_Inventory(cart_items: django.db.models.query.QuerySet):
    # 合并产品购买数量
    # print(cart_items)
    gem_integrated_items = {}   # id: quantity
    brace_integrated_items = {}
    stamp_integrated_items = {}
    for item in cart_items:
        if item.product_type == '珠':
            key = item.gemstone.id
            if key not in gem_integrated_items:
                gem_integrated_items[key] = int(item.quantity)
            else:
                gem_integrated_items[key] += int(item.quantity)
        elif item.product_type == '手链':
            key = item.bracelet.id
            if key not in brace_integrated_items:
                brace_integrated_items[key] = int(item.quantity)
            else:
                brace_integrated_items[key] += int(item.quantity)
        elif item.product_type == '印章':
            key = item.stamp.id
            if key not in stamp_integrated_items:
                stamp_integrated_items[key] = int(item.quantity)
            else:
                stamp_integrated_items[key] += int(item.quantity)

        # key = (item.product_type, item.gemstone, item.barcelet, item.stamp)

    with transaction.atomic():
        gem_found = Gemstone.objects.select_for_update().filter(id__in=list(gem_integrated_items.keys()))
        brace_found = Bracelet.objects.select_for_update().filter(id__in=list(brace_integrated_items.keys()))
        stamp_found = Stamp.objects.select_for_update().filter(id__in=list(stamp_integrated_items.keys()))

        # print(gem_found)
        # print(brace_found)

        for item in gem_found:
            item.inventory += gem_integrated_items[item.id]  # 更新库存量
            item.save()

        for item in brace_found:
            item.inventory += brace_integrated_items[item.id]  # 更新库存量
            item.save()
        
        for item in stamp_found:
            item.inventory += stamp_integrated_items[item.id]  # 更新库存量
            item.save()
        