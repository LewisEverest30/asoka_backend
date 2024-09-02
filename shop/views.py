import json
import requests
import datetime
from django.conf import settings
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import F
from django.db.models import Q
from django.forms.models import model_to_dict

from .models import *
from user.auth import MyJWTAuthentication, create_token


# 将一个Cart实例
def cart_to_dict(cart_obj):
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


# 创建购物车项（从商城散件，包括珠、链、印章）
class create_cart_from_parts(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def post(self,request,*args,**kwargs):
        userid = request.user['userid']
        info = json.loads(request.body)
        try:
            
            typ = info['product_type']  
            pid = info['product_id']
            quantity = info['quantity']
            # cost = info['cost']

            if typ not in [i[0] for i in Cart.product_type_choices]:
                return Response({'ret': 40103, 'errmsg':'不存在的产品类型', 'cart_id':None})   


            if typ == '珠':
                new_cart = Cart.objects.create(user_id=userid, product_type=typ, gemstone_id=pid, quantity=quantity, group_type='散件')
                return Response({'ret': 0, 'errmsg':None, 'cart_id':new_cart.id})   
            elif typ == '手链':
                new_cart = Cart.objects.create(user_id=userid, product_type=typ, bracelet_id=pid, quantity=quantity, group_type='散件')
                return Response({'ret': 0, 'errmsg':None, 'cart_id':new_cart.id})   
            elif typ == '印章':
                letter = info['letter']  # 刻字
                new_cart = Cart.objects.create(user_id=userid, product_type=typ, stamp_id=pid, quantity=quantity, group_type='散件', letter=letter)
                return Response({'ret': 0, 'errmsg':None, 'cart_id':new_cart.id})   
            # else:
            #     return Response({'ret': 4003, 'errmsg':'不存在的产品类型', 'cart_id':None})   
        except Exception as e:
            print(repr(e))
            return Response({'ret': 40101, 'errmsg':'请检查提交的数据是否标准', 'cart_id':None})   


# 创建购物车项（从挚礼）
class create_cart_from_gift(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def post(self,request,*args,**kwargs):
        userid = request.user['userid']
        info = json.loads(request.body)
        try:
            
            gift_id = info['gift_id']  
            component = info['component']  # list of dics {'product_type':product_type, 'product_id': pid, 'quantity': quantity}
            
            # 检查零件产品类型
            for item in component:
                if item['product_type'] not in [i[0] for i in Cart.product_type_choices]:
                    return Response({'ret': 40203, 'errmsg':'不存在的产品类型', 'group_id':None, 'cart_id_list':None})   

            # 创建组合-挚礼
            try:
                new_giftgroup = CartGroupGift.objects.create(user_id=userid, gift_id=gift_id)
            except Exception as e:
                print(repr(e))
                return Response({'ret': 40205, 'errmsg':'不存在的挚礼', 'group_id':None, 'cart_id_list':None})   

            # 创建零件
            cart_id_list = []
            for item in component:
                typ = item['product_type']
                if typ == '珠':
                    new_cart = Cart.objects.create(user_id=userid, product_type=typ, gemstone_id=item['product_id'], quantity=item['quantity'], group_type='挚礼', gift_group=new_giftgroup)
                    cart_id_list.append(new_cart.id)
                elif typ == '手链':
                    new_cart = Cart.objects.create(user_id=userid, product_type=typ, bracelet_id=item['product_id'], quantity=item['quantity'], group_type='挚礼', gift_group=new_giftgroup)
                    cart_id_list.append(new_cart.id)
                elif typ == '印章':
                    new_cart = Cart.objects.create(user_id=userid, product_type=typ, stamp_id=item['product_id'], quantity=item['quantity'], group_type='挚礼', gift_group=new_giftgroup,
                                                   letter=item['letter'])
                    cart_id_list.append(new_cart.id)
                
            return Response({'ret': 0, 'errmsg':None, 'group_id':new_giftgroup.id, 'cart_id_list':cart_id_list})   

        except Exception as e:
            print(repr(e))
            return Response({'ret': 40201, 'errmsg':'请检查提交的数据是否标准', 'group_id':None, 'cart_id_list':None})   


# 创建一个购物车项（从方案）
class create_cart_from_scheme(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def post(self,request,*args,**kwargs):
        userid = request.user['userid']
        info = json.loads(request.body)
        try:
            name = info['name']
            scheme_type = info['scheme_type']  # suixin or muban
            scheme_id = info['scheme_id']  
            component = info['component']  # list of dics {'product_type':product_type, 'product_id': pid, 'quantity': quantity}
            gem_location = info['gem_location']


            # 检查零件产品类型
            for item in component:
                if item['product_type'] not in [i[0] for i in Cart.product_type_choices]:
                    return Response({'ret': 40303, 'errmsg':'不存在的产品类型', 'group_id':None, 'cart_id_list':None})   


            # 创建组合-方案
            try:
                new_schemegroup = CartGroupScheme.objects.create(user_id=userid, typ=scheme_type, scheme_id=scheme_id,
                                                                 gem_location=gem_location, name=name)
            except Exception as e:
                print(repr(e))
                return Response({'ret': 40305, 'errmsg':'创建方案组合失败，检查与方案基本信息有关的数据', 'group_id':None, 'cart_id_list':None})   

            # 创建零件
            cart_id_list = []
            for item in component:
                typ = item['product_type']
                if typ == '珠':
                    new_cart = Cart.objects.create(user_id=userid, product_type=typ, gemstone_id=item['product_id'], quantity=item['quantity'], group_type='方案', scheme_group=new_schemegroup)
                    cart_id_list.append(new_cart.id)
                elif typ == '手链':
                    new_cart = Cart.objects.create(user_id=userid, product_type=typ, bracelet_id=item['product_id'], quantity=item['quantity'], group_type='方案', scheme_group=new_schemegroup)
                    cart_id_list.append(new_cart.id)
                elif typ == '印章':
                    new_cart = Cart.objects.create(user_id=userid, product_type=typ, stamp_id=item['product_id'], quantity=item['quantity'], group_type='方案', scheme_group=new_schemegroup,
                                                   letter=item['letter'])
                    cart_id_list.append(new_cart.id)
                
            return Response({'ret': 0, 'errmsg':None, 'group_id':new_schemegroup.id, 'cart_id_list':cart_id_list})   

        except Exception as e:
            print(repr(e))
            return Response({'ret': 40301, 'errmsg':'请检查提交的数据是否标准', 'group_id':None, 'cart_id_list':None})   




# 获取用户的所有购物车项(不含已下单的)
class get_all_cart(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def get(self,request,*args,**kwargs):
        userid = request.user['userid']

        # 获取所有数据项
        all_cart_items = Cart.objects.filter(user_id=userid, is_ordered=False)


        # 获取所有group情况
        # unique_groups = (
        #     all_cart_items
        #     .values('group_type', 'gift_group', 'scheme_group')
        #     .distinct()
        # )
        # print(unique_groups)

        # 将数据组织成字典形式
        grouped_items = {}
        for item in all_cart_items:
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
            
            grouped_items[key]['carts'].append(cart_to_dict(item))

        # 转换为列表
        # print(grouped_items)
        result = list(grouped_items.values())
        result.sort(key=lambda x:x['group_create_time'], reverse=True)

        # print(result)
        if len(result) == 0:
            return Response({'ret': 40401, 'errmsg':'购物车为空', 'data': None})
        else:
            return Response({'ret': 0, 'errmsg':None, 'data': result})


# 修改购物车项的quantity
class update_cart_quantity(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def post(self,request,*args,**kwargs):
        userid = request.user['userid']
        info = json.loads(request.body)
        try:
            cid = info['id']
            quan = info['quantity']
            found = Cart.objects.filter(user_id=userid, id=cid)
            found.update(quantity=quan)
            return Response({'ret': 0, 'errmsg':None, 'quantity':found[0].quantity})
        except Exception as e:
            print(repr(e))
            return Response({'ret': 40501, 'errmsg':'购物车项不存在', 'quantity':None})


# 删除某个购物车项
class delete_cart(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def post(self,request,*args,**kwargs):
        userid = request.user['userid']
        info = json.loads(request.body)

        # todo 每次都要检查group

        try:
            id_list = info['cart_id_list']
            found = Cart.objects.filter(user_id=userid, id__in=id_list, is_ordered=False)
            if found.count()==0:
                return Response({'ret': 40602, 'errmsg':'提交的购物车项均不存在'})

            unique_groups = list(found.values('group_type', 'gift_group', 'scheme_group').distinct())
            found.delete()  # 删除购物车项

            try:
                print(unique_groups)
                # 判断涉及到的组合，需要删的删除
                for group in unique_groups:
                    if group['group_type']=='散件':
                        continue
                    cart_num_of_this_group = Cart.objects.filter(user_id=userid, is_ordered=False, group_type=group['group_type'],
                                                                gift_group=group['gift_group'], scheme_group=group['scheme_group']).count()
                    print(cart_num_of_this_group)
                    if cart_num_of_this_group==0:
                        if group['group_type']=='挚礼':
                            print('DELETE GIFT GROUP: ' + str(group['gift_group']))
                            CartGroupGift.objects.filter(id=group['gift_group']).delete()
                        elif group['group_type']=='方案':
                            print('DELETE SCHEME GROUP: ' + str(group['scheme_group']))
                            CartGroupScheme.objects.filter(id=group['scheme_group']).delete()
            except Exception as e:
                print(repr(e))
                return Response({'ret': 50602, 'errmsg':'删除group失败'})

            return Response({'ret': 0, 'errmsg':None})
        except Exception as e:
            print(repr(e))
            return Response({'ret': 50601, 'errmsg':'服务器内部未知错误'})

# 清空购物车
class clear_cart(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def get(self,request,*args,**kwargs):
        userid = request.user['userid']
        try:
            found = Cart.objects.filter(user_id=userid)
            found.delete()
            return Response({'ret': 0})
        except Exception as e:
            print(repr(e))
            return Response({'ret': -1})
        



################################################################################################


# 创建一个地址
class create_address(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def post(self,request,*args,**kwargs):
        userid = request.user['userid']
        info = json.loads(request.body)
        try:
            recipient = info['recipient']
            phone = info['phone']
            detailed_address = info['detailed_address']
            new = Address.objects.create(user_id=userid, recipient=recipient, phone=phone,
                                            detailed_address=detailed_address)
            return Response({'ret': 0, 'errmsg':None, 'id': new.id})   
        except Exception as e:
            print(repr(e))
            return Response({'ret': -1, 'errmsg':'请检查提交的数据是否标准', 'id':None})   


# 获取用户的所有地址
class get_all_address(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def get(self,request,*args,**kwargs):
        userid = request.user['userid']
        found = Address.objects.filter(user_id=userid)
        if found.count() == 0:
            return Response({'ret': -1, 'data': None})
        else:
            serializer = AddressSerializer(instance=found, many=True)
            return Response({'ret': 0, 'data': list(serializer.data)})


# 修改地址
class update_address(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def post(self,request,*args,**kwargs):
        userid = request.user['userid']
        info = json.loads(request.body)
        try:
            aid = info['id']
            recipient = info['recipient']
            phone = info['phone']
            detailed_address = info['detailed_address']
            found = Address.objects.filter(user_id=userid, id=aid)
            found.update(recipient=recipient, phone=phone, detailed_address=detailed_address)
            return Response({'ret': 0, 'errmsg':None})   
        except Exception as e:
            print(repr(e))
            return Response({'ret': -1, 'errmsg':'请检查提交的数据是否标准'})   

# 修改地址
class delete_address(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def post(self,request,*args,**kwargs):
        userid = request.user['userid']
        info = json.loads(request.body)
        try:
            aid = info['id']
            found = Address.objects.get(user_id=userid, id=aid)
            found.delete()
            return Response({'ret': 0, 'errmsg':None})
        except Exception as e:
            print(repr(e))
            return Response({'ret': -1, 'errmsg':'地址项不存在'})
        


###############################################################################

# 获取用户的所有订单(不包括已取消的订单
class get_all_order(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def get(self,request,*args,**kwargs):
        userid = request.user['userid']
        found = Order.objects.filter(Q(user_id=userid) & ~Q(status=0))  # 不包括已取消的订单
        if found.count() == 0:
            return Response({'ret': -1, 'data': None})
        else:
            serializer = OrderSerializer1(instance=found, many=True)
            return Response({'ret': 0, 'data': list(serializer.data)})


# 获取某个订单具体信息
class get_certain_order(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def post(self,request,*args,**kwargs):
        userid = request.user['userid']
        info = json.loads(request.body)

        try:
            o_id = info['id']
            found = Order.objects.get(id=o_id)
            serializer = OrderSerializer2(instance=found, many=False)
            return Response({'ret': 0, 'data': serializer.data})

        except Exception as e:
            print(repr(e))
            return Response({'ret': -1, 'data':None})   

# 从购物车创建一个订单
class create_order_from_cart(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def post(self,request,*args,**kwargs):
        userid = request.user['userid']
        info = json.loads(request.body)
        try:
            idlist = info['cart_id']
            address_id = info['address_id']
            total_cost = info['total_cost']
            ordernumber = str(userid).zfill(6)+str(datetime.datetime.now())[:24].replace(' ', '').replace('-', '').replace(':', '').replace('.', '')

            try:
                addr = Address.objects.get(id=address_id)
            except Exception as e:
                print(repr(e))
                return Response({'ret': 3, 'errmsg':'不存在的地址项', 'id':None, 'order_number':None})

            new = Order.objects.create(user_id=userid, order_number=ordernumber, total_cost=total_cost,
                                       recipient=addr.recipient, phone=addr.phone, detailed_address=addr.detailed_address)
            
            try:
                for cid in idlist:
                    found = Cart.objects.get(user_id=userid, id=cid)
                    if found.is_ordered==True:
                        # print('该购物车项已经下单，不要重复下单')
                        new.delete()  # 发生异常要删除刚才创建的订单
                        return Response({'ret': 5, 'errmsg':'该购物车项已经下单', 'id':None, 'order_number':None})
            except Exception as e:
                print(repr(e))
                new.delete()  # 发生异常要删除刚才创建的订单
                return Response({'ret': 7, 'errmsg':'不存在的购物车项', 'id':None, 'order_number':None})

            cart_list = Cart.objects.filter(user__id=userid, id__in=idlist)
            cart_list.update(is_ordered=True, order=new)

            return Response({'ret': 0, 'errmsg':None, 'id': new.id, 'order_number':ordernumber})   
        except Exception as e:
            print(repr(e))
            return Response({'ret': -1, 'errmsg':'请检查提交的数据是否标准', 'id':None, 'order_number':None})


# 直接从商品创建一个订单
class create_order_from_product(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def post(self,request,*args,**kwargs):
        userid = request.user['userid']
        info = json.loads(request.body)
        try:
            typ = info['type']
            pid = info['pid']
            component = info['component']
            quantity = info['quantity']
            cost = info['total_cost']
            address_id = info['address_id']

            if typ == '挚礼':
                new_cart = Cart.objects.create(user_id=userid, typ=typ, gift_id=pid,
                                                component=component, quantity=quantity, cost=cost)
            elif typ == '珠':
                new_cart = Cart.objects.create(user_id=userid, typ=typ, gemstone_id=pid,
                                                component=component, quantity=quantity, cost=cost)
            elif typ == '手链':
                new_cart = Cart.objects.create(user_id=userid, typ=typ, bracelet_id=pid,
                                                component=component, quantity=quantity, cost=cost)
            else:
                return Response({'ret': 7, 'errmsg':'不存在的产品类型', 'id':None, 'order_number':None})   

            try:
                addr = Address.objects.get(id=address_id)
            except Exception as e:
                print(repr(e))
                new_cart.delete()
                return Response({'ret': 3, 'errmsg':'不存在的地址项', 'id':None, 'order_number':None})


            ordernumber = str(userid).zfill(6)+str(datetime.datetime.now())[:24].replace(' ', '').replace('-', '').replace(':', '').replace('.', '')
            new_order = Order.objects.create(user_id=userid, order_number=ordernumber, total_cost=cost,
                                       recipient=addr.recipient, phone=addr.phone, detailed_address=addr.detailed_address)
            
            new_cart.is_ordered = True
            new_cart.order = new_order
            new_cart.save()

            return Response({'ret': 0, 'errmsg':None, 'id': new_order.id, 'order_number':ordernumber})   
        except Exception as e:
            print(repr(e))
            return Response({'ret': -1, 'errmsg':'请检查提交的数据是否标准', 'id':None, 'order_number':None})


# 将订单设为已支付
class set_order_paid(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def post(self,request,*args,**kwargs):
        userid = request.user['userid']
        info = json.loads(request.body)

        try:
            order_id = info['id']
            order_found = Order.objects.filter(id=order_id, user_id=userid)

            if order_found[0].status != Order.Status_choices.pending_payment:
                return Response({'ret': 3, 'errmsg': '订单不处于待付款状态'})
            
            cart_found = Cart.objects.filter(order_id=order_id, typ='挚礼')
            for cart in cart_found:
                # if cart.typ == '挚礼':
                cart.gift.sales = F('sales') + cart.quantity  # 销量+
                cart.gift.save()

            order_found.update(status=Order.Status_choices.pending_shipment,
                           paid_dt=timezone.now())
            # order_found.status = Order.Status_choices.pending_shipment
            # order_found.paid_dt = timezone.now()
            # order_found.save()

            return Response({'ret': 0, 'errmsg': None})
        except Exception as e:
            print(repr(e))
            return Response({'ret': -1, 'errmsg': '订单不存在'})


# 取消订单，返回购物车
class cancel_order(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def post(self,request,*args,**kwargs):
        userid = request.user['userid']
        info = json.loads(request.body)

        try:
            order_id = info['id']
            order_found = Order.objects.filter(id=order_id, user_id=userid)
            
            # 只有下单之后尚未支付的情况下可以取消
            if order_found[0].status != Order.Status_choices.pending_payment:
                return Response({'ret': 3, 'errmsg': '订单不可取消'})

            # 购物车返回
            cart_found = Cart.objects.filter(is_ordered=True, order_id=order_id)
            cart_found.update(order=None, is_ordered=False)

            # 更新订单状态
            order_found.update(status=Order.Status_choices.cancelled)

            return Response({'ret': 0, 'errmsg': None})
        except Exception as e:
            print(repr(e))
            return Response({'ret': -1, 'errmsg': '订单不存在'})


# 发起售后
class refund_order(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def post(self,request,*args,**kwargs):
        userid = request.user['userid']
        info = json.loads(request.body)

        try:
            order_id = info['id']
            order_found = Order.objects.filter(id=order_id, user_id=userid)
            
            # 不可售后的条件
            if order_found[0].status in [0, 1, 5, 6]:
                return Response({'ret': 3, 'errmsg': '订单不可申请售后'})

            # 更新订单状态
            order_found.update(status=Order.Status_choices.refund)

            return Response({'ret': 0, 'errmsg': None})
        except Exception as e:
            print(repr(e))
            return Response({'ret': -1, 'errmsg': '订单不存在'})
