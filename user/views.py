import json
import requests
import datetime
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView


from .models import *
from .auth import MyJWTAuthentication, create_token


class login(APIView):

    login_url_mod = 'https://api.weixin.qq.com/sns/jscode2session?appid={}&secret={}&js_code={}&grant_type=authorization_code'

    def post(self,request,*args,**kwargs):
        info = json.loads(request.body)
        login_code = info['code']
        login_code_url = self.login_url_mod.format(settings.APPID, settings.APPSECRET, login_code)  # 构造url
        login_response = requests.get(login_code_url)  # 向腾讯服务器发送登录请求
        login_json = login_response.json()

        try:
            sessionkey = login_json['session_key']
            oid = login_json['openid']  # 获得的openid
        except Exception as e:
            print(repr(e))
            return Response({'ret': -1, 'errmsg': '微信登录接口调用失败', 'session_key': None, 'openid': None, 'openid': None})

        user_found = User.objects.filter(openid=oid)  # users表中是否已有该用户
        if user_found.count() == 0:  # 没有该用户，尝试创建一条数据，并返回id
            newuser = User.objects.create(openid=oid)
            token = create_token(newuser)
            return Response({'ret': 0, 'errmsg': None, 'session_key': sessionkey, 'openid': oid, 'token': str(token)})
        else:  # 已有该用户
            # 登录模式
            token = create_token(user_found[0])
            # print(token)
            return Response({'ret': 0, 'errmsg': None, 'session_key': sessionkey, 'openid': oid, 'token': str(token)})


class get_user_info(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def get(self,request,*args,**kwargs):
        userid = request.user['userid']
        # print(userid)
        try:
            user = User.objects.get(id=userid)
        except Exception as e:
            print(repr(e))
            return Response({'ret': -1, 'data': None})
        serializer = UserSerializer(instance=user, many=False)
        return Response({'ret': 0, 'data': serializer.data})


class update_user_info(APIView):
    authentication_classes = [MyJWTAuthentication, ]
    def post(self,request,*args,**kwargs):
        userid = request.user['userid']
        info = json.loads(request.body)
        try:
            name = info['name']
            gender = info['gender']
            birthdt = info['birthdt']
            birthloc = info['birthloc']
            liveloc = info['liveloc']
            job = info['job']
            belief = info['belief']
            mbti = info['mbti']

            user = User.objects.filter(id=userid).update(name=name, gender=gender, birthdt=birthdt,
                                                         birthloc=birthloc, liveloc=liveloc,
                                                         job=job, belief=belief, mbti=mbti)
            
            return Response({'ret': 0, 'errmsg': None})   
        except Exception as e:
            print(repr(e))
            return Response({'ret': -1, 'errmsg': '请检查提交的数据是否标准'})   




class save_phone(APIView):
    authentication_classes = [MyJWTAuthentication, ]

    phone_url_mod = 'https://api.weixin.qq.com/wxa/business/getuserphonenumber?access_token={}'
    getaccesstoken_url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}'.format(settings.APPID, settings.APPSECRET)
    
    def post(self,request,*args,**kwargs):
        # 先获得access token
        try:
            at_obj = Accesstoken.objects.get(id=1)
        except:
            # 还没有access token
            response = requests.get(self.getaccesstoken_url)  # 向腾讯服务器发送请求
            jsrespon = response.json()
            newtoken = jsrespon['access_token']
            exp_in = jsrespon['expires_in']
            at_obj = Accesstoken.objects.create(access_token=newtoken, expire_time=datetime.datetime.now()+datetime.timedelta(seconds=exp_in))
        if at_obj.expire_time.replace(tzinfo=None) <= datetime.datetime.utcnow():
            # access token 过期了
            response = requests.get(self.getaccesstoken_url)  # 向腾讯服务器发送请求
            jsrespon = response.json()
            newtoken = jsrespon['access_token']
            exp_in = jsrespon['expires_in']
            print('token过期', newtoken)
            at_obj.access_token = newtoken
            at_obj.expire_time = datetime.datetime.now()+datetime.timedelta(seconds=exp_in)
            at_obj.save()
        

        # 获取手机号
        info = json.loads(request.body)
        code = info['code']  # 前端获取的code
        
        wx_access_token = at_obj.access_token
        post_data = {
            'code': code,
        }
        getphone_response = requests.post(self.phone_url_mod.format(wx_access_token), data=post_data)
        getphone_json = getphone_response.json()

        errcode = getphone_json['errcode']
        if errcode != 0:
            # 接口调用失败
            errmsg = getphone_json['errmsg']
            return Response({'ret': -1, 'errmsg': errmsg, 'phone_number': None})

        phone_number = getphone_json["phone_info"]["purePhoneNumber"]
        # 更新该用户手机号
        userid = request.user['userid']
        try:
            user = User.objects.get(id=userid)
        except Exception as e:
            print(repr(e))
            return Response({'ret': -1, 'errmsg': '查找该用户失败', 'phone_number': None})
        
        user.phone = phone_number
        user.save()
        return Response({'ret': 0, 'errmsg': None, 'phone_number': phone_number})   


