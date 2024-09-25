import json
import django
from rest_framework.response import Response
from rest_framework.views import APIView
from functools import reduce
from django.db.models import Q
from django.conf import settings


from .models import *
from llm.models import *
from user.auth import MyJWTAuthentication, create_token

PRODUCT_EXAMPLE_NUM = 2  # 获取宝石的所有类别时展示几个示例
RELATED_PRODUCT_NUM = 3  # 相关商品展示个数

# 按名称整合queryset中的珠，详细信息
def Integrate_Gem_full(queryset: django.db.models.query.QuerySet) -> dict:
    def get_gem_pics(gem_id):
        found = GemstonePic.objects.filter(gemstone_id=gem_id)
        if found.count() > 0:
            # print("有")
            serializer = GemstonePicSerializer(instance=found, many=True)            
            return serializer.data
        else:
            # print("无")
            return None

    all_gem = queryset.values()  # 由dict构成的queryset
    
    gem_dict = {}  
    # '珠名'：dict
        # 这类珠子的共同信息字典
        # 'category': list
            # 每类的体征信息字典
                # id、position、size、price
    for gem in all_gem:
        gem_name = gem['name']


        if gem_name in gem_dict:  # 同一个珠已经查到其他尺寸
            if gem_dict[gem_name]['pics'] is None:  # 如果之前没存产品摄影
                gem_dict[gem_name]['pics'] = get_gem_pics(gem['id'])
            gem_dict[gem_name]['category'].append(
                {
                    'id': gem['id'],
                    'position': gem['position'],
                    'size': gem['size'],
                    'price': gem['price'],
                    'inventory': gem['inventory'],
                    'sales': gem['sales'],
 
                }
            )
            gem_dict[gem_name]['sales'] += gem['sales']  # 累计总销量
            if gem['price'] < gem_dict[gem_name]['price']:   # 尝试更新最低单价
                gem_dict[gem_name]['price'] = gem['price']

        else:  # 第一次查到某一个珠
            gem_dict[gem_name] = gem
            position = gem_dict[gem_name].pop('position')
            gid = gem_dict[gem_name].pop('id')
            size = gem_dict[gem_name].pop('size')
            price = gem_dict[gem_name].pop('price')
            inventory = gem_dict[gem_name].pop('inventory')
            sales = gem_dict[gem_name].pop('sales')

            # bug-f 图片地址加media前缀
            cover_raw = gem_dict[gem_name].pop('cover')
            thumbnail_raw = gem_dict[gem_name].pop('thumbnail')
            detail_raw = gem_dict[gem_name].pop('detail')
            gem_dict[gem_name]['cover'] = settings.MEDIA_URL + cover_raw
            gem_dict[gem_name]['thumbnail'] = settings.MEDIA_URL + thumbnail_raw
            gem_dict[gem_name]['detail'] = settings.MEDIA_URL + detail_raw

            gem_dict[gem_name]['category'] = [
                {
                    'id': gid,
                    'position': position,
                    'size': size,
                    'price': price,
                    'inventory': inventory,
                    'sales': sales,
                },
            ]
            gem_dict[gem_name]['sales'] = sales
            gem_dict[gem_name]['price'] = price
            gem_dict[gem_name]['pics'] = get_gem_pics(gid)  # 尝试获取产品摄影
            
            del gem_dict[gem_name]['is_recommended']
            del gem_dict[gem_name]['create_time']
            del gem_dict[gem_name]['update_time']

            # print("gem_dict[gem_name]['pics']", gem_dict[gem_name]['pics'])

    return gem_dict


# 按名称整合queryset中的珠，简要信息
def Integrate_Gem_lite_for_product(queryset: django.db.models.query.QuerySet) -> dict:
    all_gem = queryset.values()  # 由dict构成的queryset
    
    gem_dict = {}  
    # '珠名'：dict
        # 这类珠子的共同信息字典
        # 'category': list
            # 每类的体征信息字典
                # id、position、size、price
    for gem in all_gem:
        gem_name = gem['name']
        
        if gem_name not in gem_dict:
            gem_dict[gem_name] = gem
            gem_dict[gem_name]['sales'] = gem_dict[gem_name].pop('sales')
            gem_dict[gem_name]['price'] = gem_dict[gem_name].pop('price')

            del gem_dict[gem_name]['position']
            del gem_dict[gem_name]['id']
            del gem_dict[gem_name]['size']
            del gem_dict[gem_name]['detail']
            del gem_dict[gem_name]['typ']
            del gem_dict[gem_name]['wuxing']
            del gem_dict[gem_name]['material']
            del gem_dict[gem_name]['loc']
            del gem_dict[gem_name]['is_recommended']
            del gem_dict[gem_name]['create_time']
            del gem_dict[gem_name]['update_time']
            del gem_dict[gem_name]['inventory']
            del gem_dict[gem_name]['thumbnail']
            del gem_dict[gem_name]['intro']

            # bug-f 图片地址加media前缀
            cover_raw = gem_dict[gem_name].pop('cover')
            gem_dict[gem_name]['cover'] = settings.MEDIA_URL + cover_raw


        else:
            gem_dict[gem_name]['sales'] += gem['sales']  # 累计总销量
            if gem['price'] < gem_dict[gem_name]['price']:   # 尝试更新最低单价
                gem_dict[gem_name]['price'] = gem['price']

    return gem_dict


# （未使用）按名称整合queryset中的珠，用于推荐信息显示
def Integrate_Gem_lite_for_advice(queryset: django.db.models.query.QuerySet) -> dict:
    all_gem = queryset.values()  # 由dict构成的queryset
    
    gem_dict = {}  
    # '珠名'：dict
        # 这类珠子的共同信息字典
        # 'category': list
            # 每类的体征信息字典
                # id、position、size、price
    for gem in all_gem:
        gem_name = gem['name']
        
        if gem_name not in gem_dict:
            gem_dict[gem_name] = gem
            gem_dict[gem_name]['total_sales'] = gem_dict[gem_name].pop('sales')
            gem_dict[gem_name]['min_price'] = gem_dict[gem_name].pop('price')

            del gem_dict[gem_name]['position']
            del gem_dict[gem_name]['id']
            del gem_dict[gem_name]['size']
            del gem_dict[gem_name]['detail']
            del gem_dict[gem_name]['typ']
            del gem_dict[gem_name]['wuxing']
            del gem_dict[gem_name]['material']
            del gem_dict[gem_name]['loc']
            del gem_dict[gem_name]['is_recommended']
            del gem_dict[gem_name]['create_time']
            del gem_dict[gem_name]['update_time']
            del gem_dict[gem_name]['inventory']

            # bug-f 图片地址加media前缀
            cover_raw = gem_dict[gem_name].pop('cover')
            thumbnail_raw = gem_dict[gem_name].pop('thumbnail')
            gem_dict[gem_name]['cover'] = settings.MEDIA_URL + cover_raw
            gem_dict[gem_name]['thumbnail'] = settings.MEDIA_URL + thumbnail_raw

        else:
            gem_dict[gem_name]['sales'] += gem['sales']  # 累计总销量
            if gem['price'] < gem_dict[gem_name]['price']:   # 尝试更新最低单价
                gem_dict[gem_name]['price'] = gem['price']

    return gem_dict


# 按名称整合queryset中的珠，极简信息，只保留name，cover
def Integrate_Gem_mini(queryset: django.db.models.query.QuerySet) -> dict:
    all_gem = queryset.values()  # 由dict构成的queryset
    
    gem_dict = {}  
    # '珠名'：dict
        # 这类珠子的共同信息字典
        # 'category': list
            # 每类的体征信息字典
                # id、position、size、price
    for gem in all_gem:
        gem_name = gem['name']
        
        if gem_name not in gem_dict:
            gem_dict[gem_name] = gem
            del gem_dict[gem_name]['position']
            del gem_dict[gem_name]['id']
            del gem_dict[gem_name]['size']
            del gem_dict[gem_name]['detail']
            del gem_dict[gem_name]['typ']
            del gem_dict[gem_name]['wuxing']
            del gem_dict[gem_name]['material']
            del gem_dict[gem_name]['loc']
            del gem_dict[gem_name]['is_recommended']
            del gem_dict[gem_name]['create_time']
            del gem_dict[gem_name]['update_time']
            del gem_dict[gem_name]['symbol']
            del gem_dict[gem_name]['thumbnail']
            del gem_dict[gem_name]['price']
            del gem_dict[gem_name]['intro']
            del gem_dict[gem_name]['inventory']
            del gem_dict[gem_name]['sales']

            # bug-f 图片地址加media前缀
            cover_raw = gem_dict[gem_name].pop('cover')
            gem_dict[gem_name]['cover'] = settings.MEDIA_URL + cover_raw

    return gem_dict


# 按名称整合queryset中的珠，只保留name,symbol
def Integrate_Gem_only_name_symbol(queryset: django.db.models.query.QuerySet) -> dict:
    all_gem = queryset.values()  # 由dict构成的queryset
    
    gem_dict = {}  
    # '珠名'：dict
        # 这类珠子的共同信息字典
    for gem in all_gem:
        gem_name = gem['name']
        
        if gem_name not in gem_dict:
            gem_dict[gem_name] = gem
            del gem_dict[gem_name]['position']
            del gem_dict[gem_name]['id']
            del gem_dict[gem_name]['size']
            del gem_dict[gem_name]['detail']
            del gem_dict[gem_name]['typ']
            del gem_dict[gem_name]['wuxing']
            del gem_dict[gem_name]['material']
            del gem_dict[gem_name]['loc']
            del gem_dict[gem_name]['is_recommended']
            del gem_dict[gem_name]['create_time']
            del gem_dict[gem_name]['update_time']
            del gem_dict[gem_name]['thumbnail']
            del gem_dict[gem_name]['price']
            del gem_dict[gem_name]['intro']
            del gem_dict[gem_name]['inventory']
            del gem_dict[gem_name]['sales']
            del gem_dict[gem_name]['cover']

    return gem_dict


# -------------------------------------------------------------------
# 获取宝石的所有类别
# todo Redis
class get_gem_types(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def get(self,request,*args,**kwargs):
        # 全部
        result_list = []
        found_all = Gemstone.objects.filter().order_by('-is_recommended', '-create_time')
        found_all_integrate = list(Integrate_Gem_mini(found_all).values())    # 合并
        result_list.append({
            'type': '全部',
            'data': found_all_integrate if len(found_all_integrate) <= PRODUCT_EXAMPLE_NUM else found_all_integrate[:PRODUCT_EXAMPLE_NUM]  # 最多返回k个
        })

        # 其他各个类
        for choice in Gemstone.Pos_choices[:-1]:
            found = Gemstone.objects.filter(position=choice[0]).order_by('-is_recommended', '-create_time')
            found_integrate = list(Integrate_Gem_mini(found).values())    # 合并
            result_list.append({
                'type': choice[0],
                'data': found_integrate if len(found_integrate) <= PRODUCT_EXAMPLE_NUM else found_integrate[:PRODUCT_EXAMPLE_NUM]  # 最多返回k个
            })

        if len(result_list) == 0:
            return Response({'ret': 40701, 'data': None})
        else:
            # serializer = GemstoneSerializer1(instance=found, many=True)
            # return Response({'ret': 0, 'data': list(serializer.data)})
            return Response({'ret': 0, 'data': result_list})

# 获取某类的宝石
class get_gem_by_type(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def post(self,request,*args,**kwargs):
        info = json.loads(request.body)
        try:
            typ = info['type']
            if typ == '全部':
                found = Gemstone.objects.filter()
            elif typ not in [t[0] for t in Gemstone.Pos_choices[:-1]]:
                return Response({'ret': 40803, 'errmsg': '不存在的type', 'data': None})             
            else:
                found = Gemstone.objects.filter(position=typ)
            found_integrate = Integrate_Gem_lite_for_product(found).values()
            if len(found_integrate) == 0:
                return Response({'ret': 40802, 'errmsg': '无该type的商品', 'data': None})
            return Response({'ret': 0, 'errmsg': None, 'data': found_integrate})
        except Exception as e:
            print(repr(e))
            return Response({'ret': 40801, 'errmsg': '其他错误', 'data': None})

# 通过name和type获取某个宝石(合并不同的尺寸后
class get_certain_gem_by_name_type(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def post(self,request,*args,**kwargs):
        userid = request.user['userid']
        info = json.loads(request.body)

        try:
            gem_name = info['name']
            gem_pos = info['type']
            if gem_pos == '全部':
                found = Gemstone.objects.filter(name=gem_name)
            else:
                found = Gemstone.objects.filter(name=gem_name, position=gem_pos)

            # found_integrate = Integrate_Gem_full(found).values()
            found_integrate = Integrate_Gem_full(found)[gem_name]

            # todo-f 相关商品
            symbols_found = found_integrate['symbol'].split()
            reduce_filter = reduce(lambda x, y: x | y, [Q(symbol__icontains=sym) & ~Q(name=gem_name) for sym in symbols_found])  # 使用reduce对象组合多个查询条件Q
            related_prodcut = Gemstone.objects.filter(reduce_filter)
            related_integrate = list(Integrate_Gem_lite_for_product(related_prodcut).values())
            if len(related_integrate) > RELATED_PRODUCT_NUM:
                related_integrate = related_integrate[:RELATED_PRODUCT_NUM]
            found_integrate['related_product'] = related_integrate


            return Response({'ret': 0, 'data': found_integrate})

        except Exception as e:
            print(repr(e))
            return Response({'ret': 40901, 'data':None})   


# 获取所有宝石
'''
class get_all_gem(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def get(self,request,*args,**kwargs):

        found = Gemstone.objects.filter()
        # 合并
        found_integrate = Integrate_Gem_lite(found).values()
        # found_integrate = Integrate_Gem_full(found)

        if found.count() == 0:
            return Response({'ret': -1, 'data': None})
        else:
            # serializer = GemstoneSerializer1(instance=found, many=True)
            # return Response({'ret': 0, 'data': list(serializer.data)})
            return Response({'ret': 0, 'data': found_integrate})
'''
# 通过id获取具体的某个宝石
'''
class get_certain_gem(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def post(self,request,*args,**kwargs):
        userid = request.user['userid']
        info = json.loads(request.body)

        try:
            stone_id = info['id']
            found = Gemstone.objects.get(id=stone_id)
            serializer = GemstoneSerializer2(instance=found, many=False)
            return Response({'ret': 0, 'data': serializer.data})

        except Exception as e:
            print(repr(e))
            return Response({'ret': -1, 'data':None})   

'''

# -------------------------------------------------------------------
# 获取手链所有类别
class get_bracelet_types(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def get(self,request,*args,**kwargs):
        # 全部
        result_list = []
        found_all = Bracelet.objects.filter().order_by('-is_recommended', '-create_time')
        serializer_all = BraceletSerializer_mini(instance=found_all, many=True)
        ret_all = list(serializer_all.data)
        result_list.append({
            'type': '全部',
            'data': ret_all if len(ret_all) <= PRODUCT_EXAMPLE_NUM else ret_all[:PRODUCT_EXAMPLE_NUM]
        })

        # 其他各个类
        for choice in Bracelet.Type_choices[:-1]:
            found = Bracelet.objects.filter(typ=choice[0]).order_by('-is_recommended', '-create_time')
            serializer = BraceletSerializer_mini(instance=found, many=True)
            ret = list(serializer.data)
            result_list.append({
                'type': choice[0],
                'data': ret if len(ret) <= PRODUCT_EXAMPLE_NUM else ret[:PRODUCT_EXAMPLE_NUM]
            })

        if len(result_list) == 0:
            return Response({'ret': 41001, 'data': None})
        else:
            # serializer = GemstoneSerializer1(instance=found, many=True)
            # return Response({'ret': 0, 'data': list(serializer.data)})
            return Response({'ret': 0, 'data': result_list})

# 获取某类手链
class get_bracelet_by_type(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def post(self,request,*args,**kwargs):
        info = json.loads(request.body)
        try:
            typ = info['type']
            if typ == '全部':
                found = Bracelet.objects.filter()
            elif typ not in [t[0] for t in Bracelet.Type_choices[:-1]]:
                return Response({'ret': 41103, 'errmsg': '不存在的type', 'data': None})             
            else:
                found = Bracelet.objects.filter(typ=typ)

            serializer = BraceletSerializer1(instance=found, many=True)
            ret = list(serializer.data)
            if len(ret) == 0:
                return Response({'ret': 41102, 'errmsg': '无该type的商品', 'data': None})
            return Response({'ret': 0, 'errmsg': None, 'data': ret})
        except Exception as e:
            print(repr(e))
            return Response({'ret': 41101, 'errmsg': '其他错误', 'data': None})


# 通过id获取具体的某个手链
class get_certain_bracelet_by_id(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def post(self,request,*args,**kwargs):
        userid = request.user['userid']
        info = json.loads(request.body)

        try:
            bid = info['id']
            found = Bracelet.objects.get(id=bid)
            serializer = BraceletSerializer2(instance=found, many=False)
            return Response({'ret': 0, 'data': serializer.data})

        except Exception as e:
            print(repr(e))
            return Response({'ret': 41201, 'data':None})   


# 获取所有手链
'''
class get_all_bracelet(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def get(self,request,*args,**kwargs):

        found = Bracelet.objects.filter()
        if found.count() == 0:
            return Response({'ret': -1, 'data': None})
        else:
            serializer = BraceletSerializer1(instance=found, many=True)
            return Response({'ret': 0, 'data': list(serializer.data)})
'''

# -------------------------------------------------------------------
# 获取印章的类
class get_stamp_types(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def get(self,request,*args,**kwargs):
        # 全部
        result_list = []
        found_all = Stamp.objects.filter().order_by('-is_recommended', '-create_time')
        serializer_all = StampSerializer_mini(instance=found_all, many=True)
        ret_all = list(serializer_all.data)
        result_list.append({
            'type': '全部',
            'data': ret_all if len(ret_all) <= PRODUCT_EXAMPLE_NUM else ret_all[:PRODUCT_EXAMPLE_NUM]
        })
        # 其他各个类
        for choice in Stamp.Type_choices[:-1]:
            found = Stamp.objects.filter(typ=choice[0]).order_by('-is_recommended', '-create_time')
            serializer = StampSerializer_mini(instance=found, many=True)
            ret = list(serializer.data)
            result_list.append({
                'type': choice[0],
                'data': ret if len(ret) <= PRODUCT_EXAMPLE_NUM else ret[:PRODUCT_EXAMPLE_NUM]
            })

        if len(result_list) == 0:
            return Response({'ret': 41301, 'data': None})
        else:
            # serializer = GemstoneSerializer1(instance=found, many=True)
            # return Response({'ret': 0, 'data': list(serializer.data)})
            return Response({'ret': 0, 'data': result_list})

# 获取某类印章
class get_stamp_by_type(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def post(self,request,*args,**kwargs):
        info = json.loads(request.body)
        try:
            typ = info['type']
            if typ == '全部':
                found = Stamp.objects.filter()
            elif typ not in [t[0] for t in Stamp.Type_choices[:-1]]:
                return Response({'ret': 41403, 'errmsg': '不存在的type', 'data': None})             
            else:
                found = Stamp.objects.filter(typ=typ)

            serializer = StampSerializer1(instance=found, many=True)
            ret = list(serializer.data)
            if len(ret) == 0:
                return Response({'ret': 41402, 'errmsg': '无该type的商品', 'data': None})
            return Response({'ret': 0, 'errmsg': None, 'data': ret})
        except Exception as e:
            print(repr(e))
            return Response({'ret': 41401, 'errmsg': '其他错误', 'data': None})

class get_certain_stamp_by_id(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def post(self,request,*args,**kwargs):
        userid = request.user['userid']
        info = json.loads(request.body)

        try:
            s_id = info['id']
            found = Stamp.objects.get(id=s_id)
            serializer = StampSerializer2(instance=found, many=False)
            return Response({'ret': 0, 'data': serializer.data})

        except Exception as e:
            print(repr(e))
            return Response({'ret': 41501, 'data':None})   


'''
class get_all_stamp(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def get(self,request,*args,**kwargs):

        found = Stamp.objects.filter()
        if found.count() == 0:
            return Response({'ret': -1, 'data': None})
        else:
            serializer = StampSerializer1(instance=found, many=True)
            return Response({'ret': 0, 'data': list(serializer.data)})
'''

# -------------------------------------------------------------------
# 获取挚礼的类
class get_gift_types(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def get(self,request,*args,**kwargs):
        # 全部
        result_list = []
        found_all = Gift.objects.filter().order_by('-is_recommended', '-create_time')
        serializer_all = GiftSerializer_mini(instance=found_all, many=True)
        ret_all = list(serializer_all.data)
        result_list.append({
            'type': '全部',
            'data': ret_all if len(ret_all) <= PRODUCT_EXAMPLE_NUM else ret_all[:PRODUCT_EXAMPLE_NUM]
        })

        # 其他各个类
        for choice in Gift.Type_choices:
            found = Gift.objects.filter(symbol__contains=choice[0]).order_by('-is_recommended', '-create_time')
            serializer = GiftSerializer_mini(instance=found, many=True)
            ret = list(serializer.data)
            result_list.append({
                'type': choice[0],
                'data': ret if len(ret) <= PRODUCT_EXAMPLE_NUM else ret[:PRODUCT_EXAMPLE_NUM]
            })

        if len(result_list) == 0:
            return Response({'ret': 41601, 'data': None})
        else:
            # serializer = GemstoneSerializer1(instance=found, many=True)
            # return Response({'ret': 0, 'data': list(serializer.data)})
            return Response({'ret': 0, 'data': result_list})


# 获取某个类别的挚礼
class get_gift_by_type(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def post(self,request,*args,**kwargs):
        userid = request.user['userid']
        info = json.loads(request.body)
        typ = info['type']

        if typ == '全部':
            found = Gift.objects.filter()
        else:
            found = Gift.objects.filter(symbol__contains=typ)

        if found.count() == 0:
            return Response({'ret': 41701, 'data': None})
        else:
            serializer = GiftSerializer1(instance=found, many=True)
            return Response({'ret': 0, 'data': list(serializer.data)})

# 通过id获取具体的某个挚礼
class get_certain_gift_by_id(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def post(self,request,*args,**kwargs):
        userid = request.user['userid']
        info = json.loads(request.body)

        try:
            gid = info['id']
            found = Gift.objects.get(id=gid)
            try:
                serializer = GiftSerializer2(instance=found, many=False)
                ret = serializer.data
                return Response({'ret': 0, 'data': ret})
            except Exception as e:
                print(repr(e))
                return Response({'ret': 51802, 'errmsg': '挚礼序列化失败', 'data':None})  
            

        except Exception as e:
            print(repr(e))
            return Response({'ret': 41801, 'errmsg': '其他错误', 'data':None})  

# 获取所有挚礼
'''
class get_all_gift(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def get(self,request,*args,**kwargs):

        found = Gift.objects.filter()
        if found.count() == 0:
            return Response({'ret': -1, 'data': None})
        else:
            serializer = GiftSerializer1(instance=found, many=True)
            return Response({'ret': 0, 'data': list(serializer.data)})

'''

# -------------------------------------------------------------------

# 获取推荐商品
class get_recommended_product(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    
    def get(self,request,*args,**kwargs):

        recom_gem = Gemstone.objects.filter(is_recommended=True)
        recom_brac = Bracelet.objects.filter(is_recommended=True)
        recom_stamp = Stamp.objects.filter(is_recommended=True)
        recom_gift = Gift.objects.filter(is_recommended=True)

        serializer_gem = GemstoneSerializer3(instance=recom_gem, many=True)
        serializer_brac = BraceletSerializer3(instance=recom_brac, many=True)
        serializer_stamp = StampSerializer3(instance=recom_stamp, many=True)
        serializer_gift = GiftSerializer3(instance=recom_gift, many=True)

        return Response({
            'ret': 0, 
            # 'gemstone': list(serializer_gem.data),
            # 'bracelet': list(serializer_brac.data),
            # 'stamp': list(serializer_stamp.data),
            # 'gift': list(serializer_gift.data),
            'data': list(serializer_gem.data) + list(serializer_brac.data) + list(serializer_stamp.data) + list(serializer_gift.data)
            })

        # if found.count() == 0:
        #     return Response({'ret': -1, 'data': None})
        # else:
        #     serializer = GiftSerializer1(instance=found, many=True)
        #     return Response({'ret': 0, 'data': list(serializer.data)})



# -------------------------------------------------------------------

# 获取所有模版
class get_all_scheme_template(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    
    def get(self,request,*args,**kwargs):
        userid = request.user['userid']

        # 获取当前账号测评过的所有名字
        # 生成过测评报告才会有推荐信息，就是那个advice
        # todo 从测评报告里查 or 从advice里查
        person_names = Evalcontent.objects.filter(user_id=userid).values('name').distinct()
        person_names = list(person_names.values_list('name', flat=True))  # queryset转为list是字典list，这行是想要的那一列的值list
        # print(person_names)

        templates = Scheme_Template.objects.all()
        template_serializer = Scheme_TemplateSerializer1(instance=templates, many=True)

        return Response({
            'ret': 0, 
            'names': list(person_names),
            'templates': list(template_serializer.data),
            })

        # if found.count() == 0:
        #     return Response({'ret': -1, 'data': None})
        # else:
        #     serializer = GiftSerializer1(instance=found, many=True)
        #     return Response({'ret': 0, 'data': list(serializer.data)})