import json
import datetime
from django.conf import settings
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import F
from django.db.models import Q

from .models import *
from user.auth import MyJWTAuthentication, create_token
from .utils import Group_Carts_full, Check_Update_Inventory, Recover_Inventory


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
            return Response({'ret': 40101, 'errmsg':'其他错误', 'cart_id':None})   


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
            return Response({'ret': 40201, 'errmsg':'其他错误', 'group_id':None, 'cart_id_list':None})   


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
            return Response({'ret': 40301, 'errmsg':'其他错误', 'group_id':None, 'cart_id_list':None})   



# 获取用户的所有购物车项(不含已下单的)
class get_all_cart(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def get(self,request,*args,**kwargs):
        userid = request.user['userid']

        # 获取所有数据项
        all_cart_items = Cart.objects.filter(user_id=userid, is_ordered=False)

        # 将数据组织成字典形式
        grouped_items_dict = Group_Carts_full(cart_items=all_cart_items)

        # 转换为列表
        # print(grouped_items)
        result = list(grouped_items_dict.values())
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

        # 每次都要检查group
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
'''
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
'''



###############################################################################

# 获取用户的所有订单(不包括已取消的订单
class get_order_by_type(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def post(self,request,*args,**kwargs):
        userid = request.user['userid']
        info = json.loads(request.body)
        try:
            order_type = info['type']
            if order_type == '全部':
                found = Order.objects.filter(Q(user_id=userid) & ~Q(status=0))  # 不包括已取消的订单
            else:
                sta_dict = {
                    '待付款': 1,
                    '待发货': 2,
                    '待收货': 3,
                    '退款/售后': 5
                }
                status = sta_dict[order_type]
                found = Order.objects.filter(Q(user_id=userid) & Q(status=status))  # 不包括已取消的订单
            if found.count() == 0:
                return Response({'ret': 42501, 'errmsg':'无该类订单', 'data': None})
            else:
                serializer = OrderSerializer1(instance=found, many=True)
                return Response({'ret': 0, 'errmsg': None, 'data': list(serializer.data)})
        except Exception as e:
            print(repr(e))
            return Response({'ret': 52501, 'errmsg':'服务器内部未知错误', 'data':None})


# 获取某个订单具体信息
class get_certain_order_by_id(APIView):
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
            return Response({'ret': 42601, 'data':None})   

# 从购物车创建一个订单
class create_order(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def post(self,request,*args,**kwargs):
        userid = request.user['userid']
        info = json.loads(request.body)
        try:
            idlist = info['cart_id_list']
            address_id = info['address_id']
            total_cost = info['total_cost']
            notes = info['notes']
            package = info['package']
            self_design = info['self_design']

            # 地址合法检查
            try:
                addr = Address.objects.get(id=address_id)
            except Exception as e:
                print(repr(e))
                return Response({'ret': 42703, 'errmsg':'不存在的地址项', 'id':None, 'order_number':None})

            # 购物车项合法检查
            try:
                for cid in idlist:
                    found = Cart.objects.get(user_id=userid, id=cid)
                    if found.is_ordered==True:
                        return Response({'ret': 42705, 'errmsg':'提交的购物车项中包含已经下单的购物车项', 'id':None, 'order_number':None})
            except Exception as e:
                print(repr(e))
                return Response({'ret': 42707, 'errmsg':'提交的购物车项中包含不存在的购物车项', 'id':None, 'order_number':None})

            carts_found = Cart.objects.filter(user__id=userid, id__in=idlist)

            # 库存检查 and 更新
            try:
                Check_Update_Inventory(carts_found)
            except ValueError as e:
                print(repr(e))
                return Response({'ret': 52702, 'errmsg':'库存不足，无法下单('+str(e)+')', 'id':None, 'order_number':None})


            ordernumber = str(userid).zfill(6)+str(datetime.datetime.now())[:24].replace(' ', '').replace('-', '').replace(':', '').replace('.', '')
            new_order = Order.objects.create(user_id=userid, order_number=ordernumber, total_cost=total_cost,
                                       recipient=addr.recipient, phone=addr.phone, detailed_address=addr.detailed_address,
                                       notes=notes, package=package, self_design=self_design)

            carts_found.update(is_ordered=True, order=new_order)

            return Response({'ret': 0, 'errmsg':None, 'id': new_order.id, 'order_number':ordernumber})   
        except Exception as e:
            print(repr(e))
            return Response({'ret': 42701, 'errmsg':'其他错误', 'id':None, 'order_number':None})


# 直接从商品创建一个订单
'''
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
            return Response({'ret': -1, 'errmsg':'其他错误', 'id':None, 'order_number':None})

'''

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
                return Response({'ret': 42803, 'errmsg': '订单不处于待付款状态'})
            
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
            return Response({'ret': 42801, 'errmsg': '订单不存在'})


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
                return Response({'ret': 42903, 'errmsg': '订单不可取消'})

            cart_found = Cart.objects.filter(is_ordered=True, order_id=order_id)
            # 恢复库存量
            Recover_Inventory(cart_found)
            # 购物车返回         
            cart_found.update(order=None, is_ordered=False)
            # 更新订单状态
            order_found.update(status=Order.Status_choices.cancelled)

            return Response({'ret': 0, 'errmsg': None})
        except Exception as e:
            print(repr(e))
            return Response({'ret': 42901, 'errmsg': '订单不存在'})


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
            return Response({'ret': -1, 'errmsg':'其他错误', 'id':None})   


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
            return Response({'ret': -1, 'errmsg':'其他错误'})   

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
        

