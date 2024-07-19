import json
import pytz
import requests
import datetime
from django.conf import settings
from django.http import JsonResponse
from django.forms.models import model_to_dict
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import *
from user.auth import MyJWTAuthentication, create_token


# 创建一个购物车项
class create_cart(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def post(self,request,*args,**kwargs):
        userid = request.user['userid']
        info = json.loads(request.body)
        try:
            
            typ = info['type']
            pid = info['pid']
            component = info['component']
            quantity = info['quantity']
            cost = info['cost']

            if typ == '挚礼':
                new_cart = Cart.objects.create(user_id=userid, typ=typ, gift_id=pid,
                                                component=component, quantity=quantity, cost=cost)
                return Response({'ret': 0, 'errmsg':None, 'id':new_cart.id})   
            elif typ == '珠':
                new_cart = Cart.objects.create(user_id=userid, typ=typ, gemstone_id=pid,
                                                component=component, quantity=quantity, cost=cost)
                return Response({'ret': 0, 'errmsg':None, 'id':new_cart.id})   
            elif typ == '手链':
                new_cart = Cart.objects.create(user_id=userid, typ=typ, bracelet_id=pid,
                                                component=component, quantity=quantity, cost=cost)
                return Response({'ret': 0, 'errmsg':None, 'id':new_cart.id})   

            else:
                return Response({'ret': 3, 'errmsg':'不存在的产品类型', 'id':None})   
        except Exception as e:
            print(repr(e))
            return Response({'ret': -1, 'errmsg':'请检查提交的数据是否标准', 'id':None})   


# 获取用户的所有购物车项
class get_all_cart(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def get(self,request,*args,**kwargs):
        userid = request.user['userid']
        found = Cart.objects.filter(user_id=userid)
        if found.count() == 0:
            return Response({'ret': -1, 'data': None})
        else:
            serializer = CartSerializer(instance=found, many=True)
            return Response({'ret': 0, 'data': list(serializer.data)})


# 修改购物车项的quantity
class update_cart_quantity(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def post(self,request,*args,**kwargs):
        userid = request.user['userid']
        info = json.loads(request.body)
        try:
            cid = info['id']
            quan = info['quantity']
            found = Cart.objects.get(user_id=userid, id=cid)
            found.quantity = quan
            found.save()
            return Response({'ret': 0, 'errmsg':None})
        except Exception as e:
            print(repr(e))
            return Response({'ret': -1, 'errmsg':'购物车项不存在'})


# 删除某个购物车项
class delete_cart(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def post(self,request,*args,**kwargs):
        userid = request.user['userid']
        info = json.loads(request.body)
        try:
            cid = info['id']
            found = Cart.objects.get(user_id=userid, id=cid)
            found.delete()
            return Response({'ret': 0, 'errmsg':None})
        except Exception as e:
            print(repr(e))
            return Response({'ret': -1, 'errmsg':'购物车项不存在'})

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
            found = Address.objects.get(user_id=userid, id=aid)
            found.recipient = recipient
            found.phone = phone
            found.detailed_address = detailed_address
            found.save()
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
            
            cart_list = []
            try:
                for cid in idlist:
                    found = Cart.objects.get(user_id=userid, id=cid)
                    
                    if found.is_ordered==True:
                        print('该购物车项已经下单，不要重复下单')
                        new.delete()  # 发生异常要删除刚才创建的订单
                        return Response({'ret': 5, 'errmsg':'该购物车项已经下单', 'id':None, 'order_number':None})

                    cart_list.append(found)
            except Exception as e:
                print(repr(e))
                new.delete()  # 发生异常要删除刚才创建的订单
                return Response({'ret': 7, 'errmsg':'不存在的购物车项', 'id':None, 'order_number':None})

            for cart in cart_list:
                cart.is_ordered = True
                cart.order = new
                cart.save()

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
            
            cart_list = []
            try:
                for cid in idlist:
                    found = Cart.objects.get(user_id=userid, id=cid)
                    
                    if found.is_ordered==True:
                        print('该购物车项已经下单，不要重复下单')
                        new.delete()  # 发生异常要删除刚才创建的订单
                        return Response({'ret': 5, 'errmsg':'该购物车项已经下单', 'id':None, 'order_number':None})

                    cart_list.append(found)
            except Exception as e:
                print(repr(e))
                new.delete()  # 发生异常要删除刚才创建的订单
                return Response({'ret': 7, 'errmsg':'不存在的购物车项', 'id':None, 'order_number':None})

            for cart in cart_list:
                cart.is_ordered = True
                cart.order = new
                cart.save()

            return Response({'ret': 0, 'errmsg':None, 'id': new.id, 'order_number':ordernumber})   
        except Exception as e:
            print(repr(e))
            return Response({'ret': -1, 'errmsg':'请检查提交的数据是否标准', 'id':None, 'order_number':None})
