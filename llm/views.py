import json
from django.db import IntegrityError
import requests
import datetime
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import *
from user.auth import MyJWTAuthentication, create_token
from volcenginesdkarkruntime import Ark

from bazi.lunar import Lunar

# ftodo mbti
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

            # 获取八字信息
            try:
                
                bdt = datetime.datetime.fromisoformat(birthdt)
                eightchar = Lunar(bdt)
                bazi_part = {
                    '八字': ' '.join([eightchar.year8Char, eightchar.month8Char, eightchar.day8Char, eightchar.twohour8Char]),
                    '性别': '男' if gender==0 else '女',
                    '纳音': eightchar.get_nayin(),
                }
                bazi_str = str(bazi_part)
                # print('bazi '+bazi_str)
            except Exception as e:
                print(repr(e))
                return Response({'ret': 7, 'errmsg': '获取八字失败'})   
            

            if forself == True:
                forself_found = Evalcontent.objects.filter(user_id=userid, forself=True)
                if forself_found.count() == 0:
                    newc_content = Evalcontent.objects.create(user_id=userid, forself=forself, name=name, gender=gender,
                                                            birthdt=birthdt, birthloc=birthloc, liveloc=liveloc,
                                                            job=job, belief=belief, mood=mood, question1=question1,
                                                            question2=question2, question3=question3,
                                                            question4=question4, wish=wish, bazi=bazi_str)
     
                else:
                    forself_found.update(name=name, gender=gender, birthdt=birthdt, birthloc=birthloc,
                                                            liveloc=liveloc, job=job, belief=belief, mood=mood, question1=question1,
                                                            question2=question2, question3=question3,
                                                            question4=question4, wish=wish, bazi=bazi_str,
                                                            update_time=datetime.datetime.now())
            else:
                content_found = Evalcontent.objects.filter(user_id=userid, name=name, forself=False)
                # 已存在则更新，不存在则创建
                if content_found.count() == 0:  # 尝试创建一条数据
                    newc_content = Evalcontent.objects.create(user_id=userid, forself=forself, name=name, gender=gender,
                                                            birthdt=birthdt, job=job, bazi=bazi_str)
                else:  # 已有该数据, 更新
                    content_found.update(name=name, gender=gender, birthdt=birthdt, 
                                                            job=job, bazi=bazi_str,
                                                            update_time=datetime.datetime.now())
        except IntegrityError as e:
            return Response({'ret': 5, 'errmsg': '同一个用户涉及的测评中出现重名'})   
        except Exception as e:
            print(repr(e))
            return Response({'ret': -1, 'errmsg': '请检查提交的数据是否标准'})   

        # 为自己测，将测评数据同步到个人信息
        if forself==True:
            mbti = ''
            if question1 == 1:
                mbti += 'E'
            else:
                mbti += 'I'
            if question2 == 1:
                mbti += 'S'
            else:
                mbti += 'N'
            if question3 == 1:
                mbti += 'T'
            else:
                mbti += 'F'
            if question4 == 1:
                mbti += 'P'
            else:
                mbti += 'J'

            User.objects.filter(id=userid).update(name=name, gender=gender, birthdt=birthdt,
                                                birthloc=birthloc, liveloc=liveloc,
                                                job=job, belief=belief, mbti=mbti,
                                                update_time=datetime.datetime.now())
                
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



class start_chat(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    client = Ark(api_key=settings.VOLCENGINE_API_KEY)

    def fetch_non_stream_response(self, messages):
        stream = self.client.chat.completions.create(
            model="ep-20240726181421-rfxtl",
            messages=messages,
            stream=False
        )
        return {
            "role": "assistant",
            "content": stream.choices[0].message.content
        }

    def get(self,request,*args,**kwargs):
        userid = request.user['userid']
        try:

            chathis_found = Chathistory.objects.filter(user_id=userid).order_by('create_time')
            
            # 没有历史记录可开始
            if chathis_found.count() == 0:
                new_msgs = [{"role": "system", "content": settings.CHAT_PROMPT}, ]
                # 获取测评内容
                try:
                    evalcont_found = Evalcontent.objects.get(user_id=userid, forself=True)
                except Exception as e:
                    print(repr(e))
                    return Response({'ret': 5, 'errmsg': '该用户尚未对自己做测评', 'llm_msg':None})
                
                # 将八字信息作为第一条发给gpt
                new_msgs.append({"role": "user", "content": settings.CHAT_FIRST_MSG.format(evalcont_found.bazi)})
                
                try:
                    # print('对话大模型中')
                    llm_result = self.fetch_non_stream_response(new_msgs)
                    print(llm_result)
                except Exception as e:
                    return Response({'ret': 7, 'errmsg': '大模型故障', 'llm_msg':None})
                
                Chathistory.objects.create(user_id=userid, talker=0, msg=llm_result['content'])
                return Response({'ret': 0, 'errmsg': None, 'llm_msg':llm_result['content']})
            # 有历史记录不可开始
            else:
                return Response({'ret': 3, 'errmsg': '已存在聊天历史记录，请继续聊天或清空历史记录再开始新的聊天', 'llm_msg':None})
        except Exception as e:
            print(repr(e))
            return Response({'ret': -1, 'errmsg': '请检查提交的数据是否标准', 'llm_msg':None})


class continue_chat(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    client = Ark(api_key=settings.VOLCENGINE_API_KEY)

    def fetch_non_stream_response(self, messages):
        stream = self.client.chat.completions.create(
            model="ep-20240726181421-rfxtl",
            messages=messages,
            stream=False
        )
        return {
            "role": "assistant",
            "content": stream.choices[0].message.content
        }
    
    def post(self,request,*args,**kwargs):
        userid = request.user['userid']
        info = json.loads(request.body)
        try:
            msg = info['msg']
            new_msgs = [{"role": "system", "content": settings.CHAT_PROMPT}, ]

            chathis_found = Chathistory.objects.filter(user_id=userid).order_by('create_time')
            # 无历史，需开启新聊天
            if chathis_found.count() == 0:
                return Response({'ret': 3, 'errmsg': '无历史聊天记录，请开始一个聊天', 'llm_msg':None})
            # 有历史，可继续聊天
            else:
                # 把这次用户说的存下来，注意不在chathis_found中
                Chathistory.objects.create(user_id=userid, talker=1, msg=msg)

                # 将八字信息作为第一条user消息（不在数据库中，但是实际的第一条消息）
                try:
                    evalcont_found = Evalcontent.objects.get(user_id=userid, forself=True)
                except Exception as e:
                    print(repr(e))
                    return Response({'ret': 5, 'errmsg': '该用户尚未对自己做测评', 'llm_msg':None})
                new_msgs.append({"role": "user", "content": settings.CHAT_FIRST_MSG.format(evalcont_found.bazi)})

                # 从库中载入后续消息
                for his in chathis_found:
                    role = 'assistant' if his.talker==0 else 'user'
                    new_msgs.append({'role':role, 'content':his.msg})

                # 添加当前这条消息
                new_msgs.append({'role':'user', 'content':msg})
                
                # 与llm对话
                try:
                    # print('对话大模型中')
                    llm_result = self.fetch_non_stream_response(new_msgs)
                    print(llm_result)
                except Exception as e:
                    return Response({'ret': 7, 'errmsg': '大模型故障', 'llm_msg':None})
                
                Chathistory.objects.create(user_id=userid, talker=0, msg=llm_result['content'])
                return Response({'ret': 0, 'errmsg': None, 'llm_msg':llm_result['content']})
        except Exception as e:
            print(repr(e))
            return Response({'ret': -1, 'errmsg': '请检查提交的数据是否标准', 'llm_msg':None})


# class save_message(APIView):
#     authentication_classes = [MyJWTAuthentication, ]
#     def post(self,request,*args,**kwargs):
#         userid = request.user['userid']
#         info = json.loads(request.body)
#         try:
#             talker = info['talker']
#             msg = info['msg']
#             Chathistory.objects.create(user_id=userid, talker=talker, msg=msg)
#             return Response({'ret': 0, 'errmsg': None})
#         except Exception as e:
#             print(repr(e))
#             return Response({'ret': -1, 'errmsg': '请检查提交的数据是否标准'})


class get_chat_history(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def get_report(self, userid):
        try:
            report = Evalreport.objects.get(user_id=userid, evalcontent__forself=True)
            serializer = EvalreportSerializer2(instance=report, many=False)
            return serializer.data
        except Exception as e:
            print(repr(e))
            return None

    def get(self,request,*args,**kwargs):
        userid = request.user['userid']

        his_found = Chathistory.objects.filter(user_id=userid).order_by('create_time')
        if his_found.count() == 0:
            # 没有聊天记录
            return Response({'ret': 44101, 'errmsg': '无聊天记录', 'data': None, 'report': None})
        else:
            report = self.get_report(userid)
            serializer = ChathistorySerializer(instance=his_found, many=True)
            if report is None:
                return Response({'ret': 44102, 'errmsg': '有聊天记录，但未生成测评报告', 'data': list(serializer.data), 'report':None})
            return Response({'ret': 0, 'errmsg': None, 'data': list(serializer.data), 'report':report})


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


# todo 同时生成珠推荐信息 advice
class generate_eval_report(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    client = Ark(api_key=settings.VOLCENGINE_API_KEY)

    def fetch_non_stream_response(self, messages):
        stream = self.client.chat.completions.create(
            model="ep-20240726181421-rfxtl",
            messages=messages,
            stream=False
        )
        return {
            "role": "assistant",
            "content": stream.choices[0].message.content
        }

    def post(self,request,*args,**kwargs):
        userid = request.user['userid']
        info = json.loads(request.body)
        try:
            name = info['name']
            # 检查对应的测评内容是否记录下来了
            content_found = Evalcontent.objects.filter(user_id=userid, name=name)
            if content_found.count() == 0:
                return Response({'ret': 3, 'errmsg':'对应的的测评内容未被记录', 'data':None})

            # 获取MBTI
            try:
                mbti = User.objects.get(id=userid).mbti
            except Exception as e:
                print(repr(e))
                return Response({'ret': 13, 'errmsg': '获取MBTI失败', 'data':None})


            # 获取测评内容
            try:
                bazi_dic = json.loads(content_found[0].bazi.replace("'", '"'))
            except Exception as e:
                print(repr(e))
                print(content_found[0].bazi)
                return Response({'ret': 5, 'errmsg': '八字信息存在格式问题', 'data':None})
            
            wish_list = ['事业', '学业', '财富', '爱情', '健康', '安全', '家庭', '快乐', '万事顺意']
            wish = ''
            for i, char in enumerate(content_found[0].wish):
                if int(char) == 1:
                    wish += wish_list[i]
                    wish += ' '
            
            eval_dict = {
                "生日": f"{content_found[0].birthdt.year}年{content_found[0].birthdt.month}月{content_found[0].birthdt.day}日{content_found[0].birthdt.hour}时{content_found[0].birthdt.minute}分",
                "八字": bazi_dic["八字"],
                "性别": bazi_dic["性别"],
                "纳音": bazi_dic["纳音"],
                "MBTI": mbti,
            }
            # print(eval_dict)

            # 将eval_dict信息作为第一条发给gpt
            new_msgs = [{"role": "system", "content": settings.EVALREPORT_PROMPT}, ]
            new_msgs.append({"role": "user", "content": str(eval_dict)})
            
            try:
                # print('对话大模型中')
                llm_result = self.fetch_non_stream_response(new_msgs)
                # print(llm_result)
            except Exception as e:
                print(repr(e))
                return Response({'ret': 7, 'errmsg': '大模型故障', 'data':None})

            # 从llm输出中提取报告内容
            print(llm_result['content'])
            parts = llm_result['content'].split('###')  # 测评报告的各个部分
            gem = parts[0].strip()[5:-1]
            report_parts = []
            for s in parts[1:]:
                report_parts.append(s.strip()[17:])

            report_found = Evalreport.objects.filter(user_id=userid, evalcontent__name=name)
            # 已存在则更新，不存在则创建
            if report_found.count() == 0:  # 尝试创建一条数据
                
                # todo 等待llm对齐字段advice
                # newc_report = Evalreport.objects.create(user_id=userid, evalcontent=content_found[0],
                #                                         title=report_parts[1], overall=report_parts[2], 
                #                                         wish=report_parts[3], advice=report_parts[4])
                newc_report = Evalreport.objects.create(user_id=userid, evalcontent=content_found[0],
                                                        title=gem, overall_1=report_parts[0], 
                                                        overall_2=report_parts[1], overall_3=report_parts[2],
                                                        advice='TODO')
                serializer = EvalreportSerializer2(instance=newc_report, many=False)
                
            else:  # 已有该数据, 更新

                # todo 等待llm对齐字段advice
                report_found.update(title=gem, overall_1=report_parts[0], 
                                    overall_2=report_parts[1], overall_3=report_parts[2],
                                    advice='TODO',
                                    update_time=datetime.datetime.now())
                
                serializer = EvalreportSerializer2(instance=report_found[0], many=False)
            return Response({'ret': 0, 'errmsg':None, 'data':serializer.data})
        except Exception as e:
            print(repr(e))
            return Response({'ret': -1, 'errmsg':'请检查提交的数据是否标准', 'data':None})   


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
            # report_id = info['id']
            name = info['name']
            report_found = Evalreport.objects.filter(evalcontent__name=name)
            serializer = EvalreportSerializer2(instance=report_found[0], many=False)
            return Response({'ret': 0, 'data': serializer.data})

        except Exception as e:
            print(repr(e))
            return Response({'ret': -1, 'data':None})   
                
