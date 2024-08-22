import json
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import *
from user.auth import MyJWTAuthentication, create_token

# 获取所有宝石
class get_all_gem(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def get(self,request,*args,**kwargs):

        found = Gemstone.objects.filter()
        if found.count() == 0:
            return Response({'ret': -1, 'data': None})
        else:
            serializer = GemstoneSerializer1(instance=found, many=True)
            return Response({'ret': 0, 'data': list(serializer.data)})

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



class get_recommended_product(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    
    def get(self,request,*args,**kwargs):

        recom_gem = Gemstone.objects.filter(is_recommended=True)
        recom_brac = Bracelet.objects.filter(is_recommended=True)
        recom_stamp = Stamp.objects.filter(is_recommended=True)
        recom_gift = Gift.objects.filter(is_recommended=True)

        serializer_gem = GemstoneSerializer1(instance=recom_gem, many=True)
        serializer_brac = BraceletSerializer1(instance=recom_brac, many=True)
        serializer_stamp = StampSerializer1(instance=recom_stamp, many=True)
        serializer_gift = GiftSerializer1(instance=recom_gift, many=True)

        return Response({
            'ret': 0, 
            'gemstone': list(serializer_gem.data),
            'bracelet': list(serializer_brac.data),
            'stamp': list(serializer_stamp.data),
            'gift': list(serializer_gift.data),
            })

        # if found.count() == 0:
        #     return Response({'ret': -1, 'data': None})
        # else:
        #     serializer = GiftSerializer1(instance=found, many=True)
        #     return Response({'ret': 0, 'data': list(serializer.data)})