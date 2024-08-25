import json
import django
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import *
from llm.models import *
from user.auth import MyJWTAuthentication, create_token


# todo 按名称整合queryset中的珠
def Integrate_Gem_full(queryset: django.db.models.query.QuerySet):
    def get_gem_pics(gem_id):
        found = GemstonePic.objects.filter(gemstone_id=gem_id)
        if found.count() > 0:
            print("有")
            serializer = GemstonePicSerializer(instance=found, many=True)            
            return serializer.data
        else:
            print("无")
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
            if gem_dict[gem_name]['pics'] is None:
                gem_dict[gem_name]['pics'] = get_gem_pics(gem['id'])
            gem_dict[gem_name]['category'].append(
                {
                    'id': gem['id'],
                    'position': gem['position'],
                    'size': gem['size'],
                    'price': gem['price'],
 
                }
            )
        else:  # 第一次查到某一个珠
            gem_dict[gem_name] = gem
            position = gem_dict[gem_name].pop('position')
            gid = gem_dict[gem_name].pop('id')
            size = gem_dict[gem_name].pop('size')
            price = gem_dict[gem_name].pop('price')
            gem_dict[gem_name]['category'] = [
                {
                    'id': gid,
                    'position': position,
                    'size': size,
                    'price': price,
                },
            ]
            gem_dict[gem_name]['pics'] = get_gem_pics(gid)  # 尝试获取产品摄影
            print("gem_dict[gem_name]['pics']", gem_dict[gem_name]['pics'])

    return gem_dict.values()


def Integrate_Gem_lite(queryset: django.db.models.query.QuerySet):
    all_gem = queryset.values()  # 由dict构成的queryset
    
    gem_dict = {}  
    # '珠名'：dict
        # 这类珠子的共同信息字典
        # 'category': list
            # 每类的体征信息字典
                # id、position、size、price
    for gem in all_gem:
        gem_name = gem['name']
        print(gem_name)
        
        if gem_name not in gem_dict:
            gem_dict[gem_name] = gem
            del gem_dict[gem_name]['position']
            del gem_dict[gem_name]['id']
            del gem_dict[gem_name]['size']
            del gem_dict[gem_name]['detail']
            del gem_dict[gem_name]['typ']
            del gem_dict[gem_name]['wuxing']
            del gem_dict[gem_name]['material']
            del gem_dict[gem_name]['thumbnail']
            del gem_dict[gem_name]['loc']
            del gem_dict[gem_name]['is_recommended']
            del gem_dict[gem_name]['create_time']
            del gem_dict[gem_name]['update_time']

    return gem_dict.values()



# 获取所有宝石
class get_all_gem(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def get(self,request,*args,**kwargs):

        found = Gemstone.objects.filter()
        # 合并
        found_integrate = Integrate_Gem_lite(found)
        # found_integrate = Integrate_Gem_full(found)

        if found.count() == 0:
            return Response({'ret': -1, 'data': None})
        else:
            # serializer = GemstoneSerializer1(instance=found, many=True)
            # return Response({'ret': 0, 'data': list(serializer.data)})
            return Response({'ret': 0, 'data': found_integrate})

# 通过id获取具体的某个宝石
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

# 通过name获取某个宝石(合并不同的尺寸后
class get_certain_gem_byname(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def post(self,request,*args,**kwargs):
        userid = request.user['userid']
        info = json.loads(request.body)

        try:
            gem_name = info['name']
            found = Gemstone.objects.filter(name=gem_name)
            # 合并
            found_integrate = Integrate_Gem_full(found)
            

            return Response({'ret': 0, 'data': found_integrate})

        except Exception as e:
            print(repr(e))
            return Response({'ret': -1, 'data':None})   



# 获取所有手链
class get_all_bracelet(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def get(self,request,*args,**kwargs):

        found = Bracelet.objects.filter()
        if found.count() == 0:
            return Response({'ret': -1, 'data': None})
        else:
            serializer = BraceletSerializer1(instance=found, many=True)
            return Response({'ret': 0, 'data': list(serializer.data)})

# 通过id获取具体的某个手链
class get_certain_bracelet(APIView):
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
            return Response({'ret': -1, 'data':None})   


class get_all_stamp(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def get(self,request,*args,**kwargs):

        found = Stamp.objects.filter()
        if found.count() == 0:
            return Response({'ret': -1, 'data': None})
        else:
            serializer = StampSerializer1(instance=found, many=True)
            return Response({'ret': 0, 'data': list(serializer.data)})

class get_certain_stamp(APIView):
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
            return Response({'ret': -1, 'data':None})   


# 获取所有挚礼
class get_all_gift(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def get(self,request,*args,**kwargs):

        found = Gift.objects.filter()
        if found.count() == 0:
            return Response({'ret': -1, 'data': None})
        else:
            serializer = GiftSerializer1(instance=found, many=True)
            return Response({'ret': 0, 'data': list(serializer.data)})

# 获取某个类别的挚礼
class get_gift_by_symbol(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def post(self,request,*args,**kwargs):
        userid = request.user['userid']
        info = json.loads(request.body)
        typ = info['symbol']
        
        found = Gift.objects.filter(symbol__contains=typ)

        if found.count() == 0:
            return Response({'ret': -1, 'data': None})
        else:
            serializer = GiftSerializer1(instance=found, many=True)
            return Response({'ret': 0, 'data': list(serializer.data)})

# 通过id获取具体的某个挚礼
class get_certain_gift(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def post(self,request,*args,**kwargs):
        userid = request.user['userid']
        info = json.loads(request.body)

        try:
            gid = info['id']
            found = Gift.objects.get(id=gid)
            serializer = GiftSerializer2(instance=found, many=False)
            return Response({'ret': 0, 'data': serializer.data})

        except Exception as e:
            print(repr(e))
            return Response({'ret': -1, 'data':None})  


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


# 获取所有模版
class get_all_scheme_template(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    
    def get(self,request,*args,**kwargs):
        userid = request.user['userid']

        # 获取当前账号测评过的所有名字
        # 生成过测评报告才会有推荐信息，就是那个advice
        # todo 从测评报告里查 or 从advice里查
        person_names = Evalreport.objects.filter(user_id=userid).values('evalcontent__name').distinct()
        person_names = list(person_names.values_list('evalcontent__name', flat=True))  # queryset转为list是字典list，这行是想要的那一列的值list
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