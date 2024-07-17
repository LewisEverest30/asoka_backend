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
class get_gift_by_type(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def post(self,request,*args,**kwargs):
        userid = request.user['userid']
        info = json.loads(request.body)
        typ = info['type']
        found = Gift.objects.filter(typ=typ)
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


