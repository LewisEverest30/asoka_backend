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



class save_eval_content(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def post(self,request,*args,**kwargs):
        userid = request.user['userid']
        info = json.loads(request.body)
        try:
            forself = info['forself']
            name = info['name']
            gender = info['gender']
            birthdt = info['birthdt']
            birthloc = info['birthloc']
            liveloc = info['liveloc']
            job = info['job']
            belief = info['belief']
            mood = info['mood']
            question1 = info['question1']
            question2 = info['question2']
            question3 = info['question3']
            question4 = info['question4']
            wish = info['wish']
            
            content_found = Evalcontent.objects.filter(user_id=userid, name=name)
            # 已存在则更新，不存在则创建
            if content_found.count() == 0:  # 尝试创建一条数据
                newc_content = Evalcontent.objects.create(user_id=userid, forself=forself, name=name, gender=gender,
                                                        birthdt=birthdt, birthloc=birthloc, liveloc=liveloc,
                                                        job=job, belief=belief, mood=mood, question1=question1,
                                                        question2=question2, question3=question3,
                                                        question4=question4, wish=wish)
            else:  # 已有该数据, 更新
                content_found.update(name=name, forself=forself, gender=gender, birthdt=birthdt, birthloc=birthloc,
                                                        liveloc=liveloc, job=job, belief=belief, mood=mood, question1=question1,
                                                        question2=question2, question3=question3,
                                                        question4=question4, wish=wish)
        except Exception as e:
            print(repr(e))
            return Response({'ret': -1, 'errmsg': '请检查提交的数据是否标准'})   

        # 为自己测，将测评数据同步到个人信息
        if forself==True:
            User.objects.filter(id=userid).update(name=name, gender=gender, birthdt=birthdt,
                                                birthloc=birthloc, liveloc=liveloc,
                                                job=job, belief=belief)
                
        return Response({'ret': 0, 'errmsg': None})


class get_eval_content(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def post(self,request,*args,**kwargs):
        userid = request.user['userid']
        info = json.loads(request.body)
        name = info['name']
        try:
            content = Evalcontent.objects.get(user_id=userid, name=name)
        except Exception as e:
            print(repr(e))
            return Response({'ret': -1, 'data': None})
        serializer = EvalcontentSerializer(instance=content, many=False)
        return Response({'ret': 0, 'data': serializer.data})



class save_message(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def post(self,request,*args,**kwargs):
        userid = request.user['userid']
        info = json.loads(request.body)
        try:
            talker = info['talker']
            msg = info['msg']
            Chathistory.objects.create(user_id=userid, talker=talker, msg=msg)
            return Response({'ret': 0, 'errmsg': None})
        except Exception as e:
            print(repr(e))
            return Response({'ret': -1, 'errmsg': '请检查提交的数据是否标准'})


class get_chat_history(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def get(self,request,*args,**kwargs):
        userid = request.user['userid']

        his_found = Chathistory.objects.filter(user_id=userid).order_by('create_time')
        if his_found.count() == 0:
            # 没有聊天记录
            return Response({'ret': -1, 'data': None})
        else:
            serializer = ChathistorySerializer(instance=his_found, many=True)
            return Response({'ret': 0, 'data': list(serializer.data)})


class clear_chat_history(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def get(self,request,*args,**kwargs):
        userid = request.user['userid']
        try:
            his_found = Chathistory.objects.filter(user_id=userid)
            his_found.delete()
            return Response({'ret': 0})
        except Exception as e:
            print(repr(e))
            return Response({'ret': -1})



class save_eval_report(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def post(self,request,*args,**kwargs):
        userid = request.user['userid']
        info = json.loads(request.body)
        try:
            name = info['name']
            # 先检查对应的测评内容是否记录下来了
            content_found = Evalcontent.objects.filter(user_id=userid, name=name)
            if content_found.count() == 0:
                return Response({'ret': 3, 'errmsg':'对应的的测评内容未被记录'})
            
            title = info['title']
            overall = info['overall']
            wish = info['wish']
            advice = info['advice']

            report_found = Evalreport.objects.filter(user_id=userid, evalcontent__name=name)
            # 已存在则更新，不存在则创建
            if report_found.count() == 0:  # 尝试创建一条数据
                newc_report = Evalreport.objects.create(user_id=userid, evalcontent=content_found[0],
                                                        title=title, overall=overall, wish=wish, advice=advice)
            else:  # 已有该数据, 更新
                report_found.update(title=title, overall=overall, wish=wish, advice=advice)
        except Exception as e:
            print(repr(e))
            return Response({'ret': -1, 'errmsg':'请检查提交的数据是否标准'})   
                
        return Response({'ret': 0, 'errmsg':None})


class get_all_eval_report(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def get(self,request,*args,**kwargs):
        userid = request.user['userid']

        report_found = Evalreport.objects.filter(user_id=userid)
        if report_found.count() == 0:
            # 没有聊天记录
            return Response({'ret': -1, 'data': None})
        else:
            serializer = EvalreportSerializer1(instance=report_found, many=True)
            return Response({'ret': 0, 'data': list(serializer.data)})
        

class get_certain_eval_report(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def post(self,request,*args,**kwargs):
        userid = request.user['userid']
        info = json.loads(request.body)

        try:
            report_id = info['id']
            report_found = Evalreport.objects.get(id=report_id)
            serializer = EvalreportSerializer2(instance=report_found, many=False)
            return Response({'ret': 0, 'data': serializer.data})

        except Exception as e:
            print(repr(e))
            return Response({'ret': -1, 'data':None})   
                
