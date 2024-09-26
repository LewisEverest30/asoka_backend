import json
import re
from django.db import IntegrityError
import datetime
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q, F, Value
from django.db.models.functions import Concat
from django.db.models import Case, When, F
from volcenginesdkarkruntime import Ark


from .models import *
from user.auth import MyJWTAuthentication, create_token
from product.models import Gemstone
from product.views import Integrate_Gem_only_name_symbol


from bazi.lunar import Lunar


# todo-f mbti
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
                # bug-f 用户自己的名字在为他人测时消耗到了，再创建为自己测会失败
                # 解决办法：先去为他人测里判断是否出现重名，出现的话，手动改掉为他人测的名字
                notforself_found = Evalcontent.objects.filter(user_id=userid, name=name, forself=False)  # 为他人测已经出现过这个名字
                if notforself_found.count() != 0:
                    # 为他人测中存在冲突的名字
                    notforself_found.update(name=Concat(F('name'), Value('(非本人)')))

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
                # bug-f 为本人测已经用过的名字，再去到为他人测会受到联合主键限制
                # 解决办法：现检查为自己测有没有同名的，如果有，手动为name补充后缀
                forself_found = Evalcontent.objects.filter(user_id=userid, forself=True, name=name)
                if forself_found.count() != 0:
                    name += '(非本人)'

                content_found = Evalcontent.objects.filter(user_id=userid, name=name, forself=False)
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
            return Response({'ret': -1, 'errmsg': '其他错误'})   

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

# ----------------------------------------------------------

class start_chat(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    client = Ark(api_key=settings.VOLCENGINE_API_KEY)

    def fetch_non_stream_response(self, messages):
        stream = self.client.chat.completions.create(
            model=settings.VOLCENGINE_MODEL_ID,
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
                
                result_msg = llm_result['content']
                Chathistory.objects.create(user_id=userid, talker=0, msg=result_msg)
                
                wenyan_index = result_msg.find('$')
                return Response({'ret': 0, 
                                 'errmsg': None, 
                                 'llm_msg': {
                                     'wenyan': result_msg[:wenyan_index],
                                     'baihua': result_msg[wenyan_index+1:]
                                 }
                                 })
            # 有历史记录不可开始
            else:
                return Response({'ret': 3, 'errmsg': '已存在聊天历史记录，请继续聊天或清空历史记录再开始新的聊天', 'llm_msg':None})
        except Exception as e:
            print(repr(e))
            return Response({'ret': -1, 'errmsg': '其他错误', 'llm_msg':None})


class continue_chat(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    client = Ark(api_key=settings.VOLCENGINE_API_KEY)

    def fetch_non_stream_response(self, messages):
        stream = self.client.chat.completions.create(
            model=settings.VOLCENGINE_MODEL_ID,
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
            input_msg = info['msg']
            new_msgs = [{"role": "system", "content": settings.CHAT_PROMPT}, ]

            chathis_found = Chathistory.objects.filter(user_id=userid).order_by('create_time')
            # 无历史，需开启新聊天
            if chathis_found.count() == 0:
                return Response({'ret': 3, 'errmsg': '无历史聊天记录，请开始一个聊天', 'llm_msg':None})
            # 有历史，可继续聊天
            else:
                # 把这次用户说的存下来，注意不在chathis_found中
                Chathistory.objects.create(user_id=userid, talker=1, msg=input_msg)

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
                new_msgs.append({'role':'user', 'content':input_msg})
                
                # 与llm对话
                try:
                    # print('对话大模型中')
                    llm_result = self.fetch_non_stream_response(new_msgs)
                    print(llm_result)
                except Exception as e:
                    return Response({'ret': 7, 'errmsg': '大模型故障', 'llm_msg':None})
                
                result_msg = llm_result['content']
                Chathistory.objects.create(user_id=userid, talker=0, msg=result_msg)
                
                wenyan_index = result_msg.find('$')
                return Response({'ret': 0, 
                                 'errmsg': None, 
                                 'llm_msg': {
                                     'wenyan': result_msg[:wenyan_index],
                                     'baihua': result_msg[wenyan_index+1:]
                                 }
                                 })
        except Exception as e:
            print(repr(e))
            return Response({'ret': -1, 'errmsg': '其他错误', 'llm_msg':None})


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
#             return Response({'ret': -1, 'errmsg': '其他错误'})


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


# -------------------------------------------------------

class generate_eval_report(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    client = Ark(api_key=settings.VOLCENGINE_API_KEY)

    def fetch_non_stream_response(self, messages):
        stream = self.client.chat.completions.create(
            model=settings.VOLCENGINE_MODEL_ID,
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
            # todo-f 只考虑为自己测
            content_found = Evalcontent.objects.filter(user_id=userid, name=name, forself=True)
            if content_found.count() == 0:
                return Response({'ret': 3, 'errmsg':'对应的的测评内容未被记录', 'data':None})

            # 获取MBTI
            try:
                mbti = User.objects.get(id=userid).mbti
            except Exception as e:
                print(repr(e))
                return Response({'ret': 13, 'errmsg': '获取MBTI失败', 'data':None})


            # 生成送入llm的个人信息
            try:
                bazi_dic = json.loads(content_found[0].bazi.replace("'", '"'))
            except Exception as e:
                print(repr(e))
                print(content_found[0].bazi)
                return Response({'ret': 5, 'errmsg': '八字信息存在格式问题', 'data':None})
            
            # 获取wish
            wish_list = decode_wish(content_found[0].wish)

            eval_dict = {
                "生日": f"{content_found[0].birthdt.year}年{content_found[0].birthdt.month}月{content_found[0].birthdt.day}日{content_found[0].birthdt.hour}时{content_found[0].birthdt.minute}分",
                "八字": bazi_dic["八字"],
                "性别": bazi_dic["性别"],
                "纳音": bazi_dic["纳音"],
                "MBTI": mbti,
                "心愿1": wish_list[0],
                "心愿2": wish_list[1],
                "心愿3": wish_list[2],
            }
            # print(eval_dict)

            with open('D:\\eval_report.log', 'a+') as f:
                f.write('输入：\n')
                f.write(str(eval_dict))
                f.write('\n')

            # 将eval_dict信息作为第一条发给gpt
            new_msgs = [{"role": "system", "content": settings.EVALREPORT_PROMPT}, ]
            new_msgs.append({"role": "user", "content": str(eval_dict)})
            print(str(eval_dict))
            
            try:
                # print('对话大模型中')
                llm_result = self.fetch_non_stream_response(new_msgs)
                # print(llm_result)
            except Exception as e:
                print(repr(e))
                return Response({'ret': 7, 'errmsg': '大模型故障', 'data':None})


            # 从llm输出中提取报告内容'
            # -------------------------------------------------------------------------------
            # todo-f 正则
            llm_result_str_raw = llm_result['content']
            # print(llm_result_str_raw)

            with open('D:\\eval_report.log', 'a') as f:
                f.write('输出：\n')
                f.write(str(llm_result_str_raw))
                f.write('\n\n')

            # 尝试找“###”，截取其后面的内容
            index = llm_result_str_raw.find("###")
            if index != -1:
                llm_result_str_raw = llm_result_str_raw[index + 3:].strip()  # +3跳过“###”
                if llm_result_str_raw[:2] != '宝石':
                    return Response({'ret': 17, 'errmsg': '大模型返回内容无法解析', 'data':None})
            else:
                return Response({'ret': 17, 'errmsg': '大模型返回内容无法解析', 'data':None})

            parts = llm_result_str_raw.split('###')  # 测评报告的各个部分
            
            # 提取各个部分
            gem_pattern = r'堇青石|紫珍珠|海蓝石|绿松石|金红石|琥珀|祖母绿|翡翠'
            gem_match = re.findall(gem_pattern, parts[0].strip())
            gem = gem_match[0]

            report_key_parts = []
            for part_string in parts[1:4]:
                part_string = part_string.strip()
                found_index = part_string.find(" --- ")
                report_key_parts.append(part_string[found_index+5:])

            report_wish_parts = [None for _ in range(3)]
            for i, part_string in enumerate(parts[4:]):
                part_string = part_string.strip()
                found_index = part_string.find(" --- ")
                report_wish_parts[i] = part_string[found_index+5:]



            # 操作数据库
            report_found = Evalreport.objects.filter(user_id=userid, evalcontent__name=name)
            if report_found.count() == 0:  # 尝试创建一条数据
                
                # todo-f 等待llm对齐字段wish1,2,3
                newc_report = Evalreport.objects.create(user_id=userid, evalcontent=content_found[0],
                                                        title=gem, overall_1=report_key_parts[0], 
                                                        overall_2=report_key_parts[1], overall_3=report_key_parts[2],
                                                        wish_1=report_wish_parts[0], wish_2=report_wish_parts[1],
                                                        wish_3=report_wish_parts[2],
                                                        )
                serializer = EvalreportSerializer2(instance=newc_report, many=False)
                
            else:  # 已有该数据, 更新

                # todo-f 等待llm对齐字段wish1,2,3
                report_found.update( title=gem, overall_1=report_key_parts[0], 
                                    overall_2=report_key_parts[1], overall_3=report_key_parts[2],
                                    wish_1=report_wish_parts[0], wish_2=report_wish_parts[1],
                                    wish_3=report_wish_parts[2],
                                    update_time=datetime.datetime.now())
                
                serializer = EvalreportSerializer2(instance=report_found[0], many=False)
            return Response({'ret': 0, 'errmsg':None, 'data':serializer.data})
        except Exception as e:
            print(repr(e))
            return Response({'ret': -1, 'errmsg':'其他错误', 'data':None})   


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
            # bug-f 查询时不能不考虑userid
            report_found = Evalreport.objects.filter(user_id=userid, evalcontent__name=name)
            if report_found.count() == 0:
                return Response({'ret': 3, 'errmsg': '没有该名字对应的测评报告', 'data':None})   
            serializer = EvalreportSerializer2(instance=report_found[0], many=False)
            return Response({'ret': 0, 'errmsg': None, 'data': serializer.data})

        except Exception as e:
            print(repr(e))
            return Response({'ret': -1, 'errmsg': '其他错误', 'data':None})   
                

# ---------------------------------------------------------

def scale_dict_values(input_dict: dict, target_min=30, target_max=100):
    all_values = list(input_dict.values())
    max_value = max(all_values)
    min_value = min(all_values)
    if max_value == min_value or target_max == target_min:
        return
    for key in input_dict.keys():
        input_dict[key] = int(target_min +  ((input_dict[key] - min_value) * (target_max - target_min) / (max_value - min_value)))


# todo-f 生成珠推荐信息
# 区分人名 “非本人”
class generate_advice(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    client = Ark(api_key=settings.VOLCENGINE_API_KEY)

    def fetch_non_stream_response(self, messages):
        stream = self.client.chat.completions.create(
            model=settings.VOLCENGINE_MODEL_ID,
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
            
            # 生成送入llm的个人信息
            try:
                bazi_dic = json.loads(content_found[0].bazi.replace("'", '"'))
            except Exception as e:
                print(repr(e))
                print(content_found[0].bazi)
                return Response({'ret': 5, 'errmsg': '八字信息存在格式问题', 'data':None})
            

            # 与大模型交互
            eval_dict = {
                "生日": f"{content_found[0].birthdt.year}年{content_found[0].birthdt.month}月{content_found[0].birthdt.day}日{content_found[0].birthdt.hour}时{content_found[0].birthdt.minute}分",
                "八字": bazi_dic["八字"],
                "性别": bazi_dic["性别"],
                "纳音": bazi_dic["纳音"],
            }
            
            with open('D:\\advice.log', 'a+') as f:
                f.write('输入：\n')
                f.write(str(eval_dict))
                f.write('\n')

            
            new_msgs = [{"role": "system", "content": settings.ADVICE_PROMPT}, ]  # prompt
            new_msgs.append({"role": "user", "content": str(eval_dict)})  # 将eval_dict信息作为第一条发给gpt            
            try:
                # print('对话大模型中')
                llm_result = self.fetch_non_stream_response(new_msgs)
                # print(llm_result)
            except Exception as e:
                print(repr(e))
                return Response({'ret': 7, 'errmsg': '大模型故障', 'data':None})


            # 初步处理大模型输出，尝试找“###”，截取其后面的内容
            llm_result_str_raw = llm_result['content']
            # print(llm_result_str_raw)

            with open('D:\\advice.log', 'a+') as f:
                f.write('输出：\n')
                f.write(str(llm_result_str_raw))
                f.write('\n\n')

            index = llm_result_str_raw.find("###")
            if index != -1:
                llm_result_str_raw = llm_result_str_raw[index + 3:].strip()  # +3跳过“###”
                if llm_result_str_raw[:2] != '寓意':
                    return Response({'ret': 17, 'errmsg': '大模型返回内容无法解析', 'data':None})
            else:
                return Response({'ret': 17, 'errmsg': '大模型返回内容无法解析', 'data':None})



            # 循环提取各个部分
            # todo-f 寓意-分数
            symbol_mark_dict = {}
            parts = llm_result_str_raw.split('###')
            for i, part_string in enumerate(parts):
                pattern = r'寓意\d*:\s*\[*\s*(.*)\s*\[*\s*---\s*匹配度:\s*\[*\s*(\d+)\s*\[*\s*(.*)'
                match = re.findall(pattern, part_string)
                symbol = match[0][0].replace(' ', '')
                mark = int(match[0][1])
                symbol_mark_dict[symbol] = mark
            scale_dict_values(symbol_mark_dict)
            print(symbol_mark_dict)

            # 获取所有宝石（合并后），根据包含的寓意，算加权分数
            all_gem_name = list(Integrate_Gem_only_name_symbol(Gemstone.objects.filter()).values())
            print(all_gem_name)
            for gem in all_gem_name:
                gem_name = gem['name']
                gem_symbol = gem['symbol'].split()
                if len(gem_symbol) == 0 or len(gem_symbol) > 3:
                    return Response({'ret': 21, 'errmsg': '珠子寓意解析失败', 'data':None})
                elif len(gem_symbol) == 3:
                    weight = (0.5, 0.3, 0.2)
                elif len(gem_symbol) == 2:
                    weight = (0.6, 0.4)
                elif len(gem_symbol) == 1:
                    weight = (1,)
                weighted_mark = 0
                for i, w in enumerate(weight):
                    weighted_mark += w * symbol_mark_dict[gem_symbol[i]]
                
                found_advice = Advice.objects.filter(user_id=userid, person_name=name,
                                                        gem_name=gem_name)
                if found_advice.count() == 0:
                    new_advice = Advice.objects.create(user_id=userid, person_name=name,
                                                            gem_name=gem_name, mark=weighted_mark, 
                                                            )
                else:
                    found_advice.update(mark=weighted_mark)

            adv_found = Advice.objects.filter(user_id=userid, person_name=name).order_by('-mark')

            # todo 分位置展示
            ret_list = []
            adv_indexs = [-1, -1, -1, -1]
            for i, position in enumerate([pos[0] for pos in Gemstone.Pos_choices[:-1]]):
                for j, adv in enumerate(adv_found):
                    if j in adv_indexs:
                        continue
                    gem_found_position = Gemstone.objects.filter(name=adv.gem_name).values_list('position', flat=True).distinct()
                    if position in gem_found_position:
                        ret_list.append(adv)
                        adv_indexs[i] = j
                        break       
            serializer = AdviceSerializer(instance=ret_list, many=True)
                
            return Response({'ret': 0, 'errmsg':None, 'data':list(serializer.data)})
        except Exception as e:
            print(repr(e))
            return Response({'ret': -1, 'errmsg':'其他错误', 'data':None})   



# 获取所有建议
class get_advice(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    
    def post(self,request,*args,**kwargs):
        # 缩略图。名称。symbol。匹配度
        userid = request.user['userid']

        info = json.loads(request.body)
        try:
            name = info['name']

            # advice = list(Advice.objects.filter(user_id=userid, person_name=name).order_by('-mark').values('gem_name', 'mark'))
            adv_found = Advice.objects.filter(user_id=userid, person_name=name).order_by('-mark')

            if len(adv_found) == 0:
                return Response({'ret': 4051, 'errmsg': '不存在的人名', 'advice':None})


            # todo 分位置展示
            ret_list = []
            adv_indexs = [-1 for _ in range(4)]
            for i, position in enumerate([pos[0] for pos in Gemstone.Pos_choices[:-1]]):
                print(ret_list)
                print(adv_indexs)
                for j, adv in enumerate(adv_found):
                    if j in adv_indexs:
                        print(f'{j} in adv_indexs')
                        continue
                    gem_found_position = Gemstone.objects.filter(name=adv.gem_name).values_list('position', flat=True).distinct()
                    if position in gem_found_position:
                        print(f'result append {adv}')
                        ret_list.append(adv)
                        adv_indexs[i] = j
                        break       
            serializer = AdviceSerializer(instance=ret_list, many=True)

            return Response({'ret': 0, 'errmsg': None, 'advice': list(serializer.data)})
        except Exception as e:
            print(repr(e))
            return Response({'ret': -1, 'errmsg': '其他错误', 'advice':None})   



# 获取所有建议 用户方案选配
# todo Redis
class get_advice_for_scheme(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    
    def post(self,request,*args,**kwargs):
        # 尺寸，封面。缩略图。名称。symbol。price。匹配度。intro
        userid = request.user['userid']

        info = json.loads(request.body)
        try:
            name = info['name']

            advice = list(Advice.objects.filter(user_id=userid, person_name=name).order_by('-mark').values('gem_name', 'mark'))
            if len(advice) == 0:
                return Response({'ret': 4051, 'errmsg': '不存在的人名', 
                                'ding': None,
                                'yao': None,
                                'zi': None,
                                'pei': None,
                                 })

            mark_dict = {}  # 珠名-评分 字典
            for adv in advice:
                mark_dict[adv['gem_name']] = adv['mark']
    
            # 顶
            gem_ding = Gemstone.objects.filter(position='顶珠')
            gem_ding = gem_ding.annotate(
                mark=Case(
                    *[When(name=k, then=v) for k, v in mark_dict.items()],  # *进行展开赋值
                    default=0,
                    output_field=models.IntegerField()
                )
            )
            gem_ding = gem_ding.order_by('-mark').values('id', 'name', 'symbol', 'size', 'thumbnail', 'cover', 'intro', 'mark', 'price')
            for gem in gem_ding:
                gem['symbol'] = gem['symbol'].split()
                gem['thumbnail'] = settings.MEDIA_URL + gem['thumbnail']
                gem['cover'] = settings.MEDIA_URL + gem['cover']

            # 腰
            gem_yao = Gemstone.objects.filter(position='腰珠')
            gem_yao = gem_yao.annotate(
                mark=Case(
                    *[When(name=k, then=v) for k, v in mark_dict.items()],  # *进行展开赋值
                    default=0,
                    output_field=models.IntegerField()
                )
            )
            gem_yao = gem_yao.order_by('-mark').values('id', 'name', 'symbol', 'size', 'thumbnail', 'cover', 'intro', 'mark', 'price')
            for gem in gem_yao:
                gem['symbol'] = gem['symbol'].split()
                gem['thumbnail'] = settings.MEDIA_URL + gem['thumbnail']
                gem['cover'] = settings.MEDIA_URL + gem['cover']

            # 子
            gem_zi = Gemstone.objects.filter(position='子珠')
            gem_zi = gem_zi.annotate(
                mark=Case(
                    *[When(name=k, then=v) for k, v in mark_dict.items()],  # *进行展开赋值
                    default=0,
                    output_field=models.IntegerField()
                )
            )
            gem_zi = gem_zi.order_by('-mark').values('id', 'name', 'symbol', 'size', 'thumbnail', 'cover', 'intro', 'mark', 'price')
            for gem in gem_zi:
                gem['symbol'] = gem['symbol'].split()
                gem['thumbnail'] = settings.MEDIA_URL + gem['thumbnail']
                gem['cover'] = settings.MEDIA_URL + gem['cover']

            # 配
            gem_pei = Gemstone.objects.filter(position='配珠')
            gem_pei = gem_pei.annotate(
                mark=Case(
                    *[When(name=k, then=v) for k, v in mark_dict.items()],  # *进行展开赋值
                    default=0,
                    output_field=models.IntegerField()
                )
            )
            gem_pei = gem_pei.order_by('-mark').values('id', 'name', 'symbol', 'size', 'thumbnail', 'cover', 'intro', 'mark', 'price')
            for gem in gem_pei:
                gem['symbol'] = gem['symbol'].split()
                gem['thumbnail'] = settings.MEDIA_URL + gem['thumbnail']
                gem['cover'] = settings.MEDIA_URL + gem['cover']

            return Response({'ret': 0, 'errmsg': None, 
                             'ding': list(gem_ding),
                             'yao': list(gem_yao),
                             'zi': list(gem_zi),
                             'pei': list(gem_pei),
                             })
        except Exception as e:
            print(repr(e))
            return Response({'ret': -1, 'errmsg': '其他错误',
                             'ding': None,
                             'yao': None,
                             'zi': None,
                             'pei': None,                             
                             })   








# 获取所有建议
# class get_advice(APIView):
#     authentication_classes = [MyJWTAuthentication, ]
    
#     def post(self,request,*args,**kwargs):
#         # 缩略图。名称。symbol。匹配度
#         userid = request.user['userid']

#         info = json.loads(request.body)
#         try:
#             name = info['name']

#             # advice = list(Advice.objects.filter(user_id=userid, person_name=name).order_by('-mark').values('gem_name', 'mark'))
#             adv_found = Advice.objects.filter(user_id=userid, person_name=name).order_by('-mark')

#             if len(adv_found) == 0:
#                 return Response({'ret': 4051, 'errmsg': '不存在的人名', 'advice':None})

#             # gem_all = Gemstone.objects.all()
#             # gem_integrate_dict = Integrate_Gem_lite_for_advice(gem_all)

#             # for adv in advice:
#             #     # 添加缩略图和symbol
#             #     adv['thumbnail'] = gem_integrate_dict[adv['gem_name']]['thumbnail']
#             #     adv['symbol'] = gem_integrate_dict[adv['gem_name']]['symbol']
#             serializer = AdviceSerializer(instance=adv_found, many=True)

#             print(serializer.data)

#             return Response({'ret': 0, 'errmsg': None, 'advice': list(serializer.data)})
#         except Exception as e:
#             print(repr(e))
#             return Response({'ret': -1, 'errmsg': '其他错误', 'advice':None})   
