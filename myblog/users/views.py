import re

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import DatabaseError
from django.http import HttpResponseBadRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from random import randint

from libs.yuntongxun.sms import CCP
from users.models import User
from utils.response_code import RETCODE

#1.导入系统的logging
import logging
#2.创建获取日志器
logger = logging.getLogger("django")

# Create your views here.
class RegisterView(View):
    # 展示注册界面，处理GET请求
    def get(self, request):
        # 响应注册界面  render(请求对象,'注册界面')
        return render(request, 'register.html')

    # 实现注册功能，处理POST请求
    def post(self, request):
        # 1.接收请求参数
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        sms_code_client = request.POST.get('sms_code')

        # 2.验证数据
        # 2.1 判断参数是否齐全
        if not all([mobile,password,password2,sms_code_client]):
            return HttpResponseBadRequest('缺少必填参数')

        # 2.2 通过re.match判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$' , mobile):
            return HttpResponseBadRequest('请输入正确的手机号')

        # 2.3 通过re.match判断密码是否是8-20个数字
        if not re.match(r'^[0-9A-Za-z]{8,20}$' , password):
            return HttpResponseBadRequest('请输入8-20位密码')

        # 2.4 判断两次密码是否一致
        if password != password2:
            return HttpResponseBadRequest('两次密码输入不一致')

        # 2.5 验证短信验证码，对比Redis中与页面传递的验证码是否一致，其中redis中的数据是bytes类型，需要进行decode()再比较
        redis_conn = get_redis_connection('default')
        sms_code_server = redis_conn.get('sms:%s' %mobile)
        if sms_code_server is None:
            return HttpResponseBadRequest('短信验证码已过期')
        if sms_code_server.decode() != sms_code_client:
            return HttpResponseBadRequest('短信验证码输入错误')

        # 3.保存注册数据，可以使用系统方法create_user() 来对密码进行加密，若出现DatabaseError则注册失败
        try:
            user = User.objects.create_user(username=mobile,mobile=mobile,password=password)
        except DatabaseError as e:
            logger.error(e)
            return HttpResponseBadRequest('注册失败，请重试')

        # 4.注册成功后即表示用户认证通过，设置状态保持
        # 当前站点存储sessionid的信息，且Redis服务器中存储sessionid的信息
        login(request ,user)

        # 5.注册成功则重定向至首页
        # redirect 进行重定间
        # reverse  可以通过namespace:name 来获取到视图所对应的路由
        response = redirect(reverse('home:index'))

        # 6.设置cookie信息
        # 设置登录状态，会话结束后自动过期
        response.set_cookie("is_login" , True)
        # 设置首页用户名，设置有效期为7天
        response.set_cookie("username" , user.username , max_age=7*24*3600)

        # 7.响应注册结果
        return response

# class RegisterView(View):
#     # 展示注册界面，处理GET请求
#     def get(self, request):
#         # 响应注册界面  render(请求对象,'注册界面')
#         return render(request, 'register.html')
#
#     # 实现注册功能，处理POST请求
#         # 实现注册功能，处理POST请求
#         def post(self, rquest):
#             # 1.接收请求参数
#             mobile = request.POST.get('mobile')
#             password = request.POST.get('password')
#             password2 = request.POST.get('password2')
#             sms_code_client = request.POST.get('sms_code')
#
#             # 2.验证数据
#             # 2.1 判断参数是否齐全
#             if not all([mobile, password, password2, sms_code_client]):
#                 return HttpResponseBadRequest('缺少必填参数')
#
#             # 2.2 通过re.match判断手机号是否合法
#             if not re.match(r'^1[3-9]\d{9}$', mobile):
#                 return HttpResponseBadRequest('请输入正确的手机号')
#
#             # 2.3 通过re.match判断密码是否是8-20个数字
#             if not re.match(r'^[0-9A-Za-z]{4,8}$', password):
#                 return HttpResponseBadRequest('请输入8-20位密码')
#
#             # 2.4 判断两次密码是否一致
#             if password != password2:
#                 return HttpResponseBadRequest('两次密码输入不一致')
#
#             # 2.5 验证短信验证码，对比Redis中与页面传递的验证码是否一致，其中redis中的数据是bytes类型，需要进行decode()再比较
#             redis_conn = get_redis_connection('default')
#             sms_code_server = redis_conn.get('sms:%s' % mobile)
#             if sms_code_server is None:
#                 return HttpResponseBadRequest('短信验证码已过期')
#             if sms_code_server.decode() != sms_code_client:
#                 return HttpResponseBadRequest('短信验证码输入错误')
#
#             # 3.保存注册数据，可以使用系统方法create_user() 来对密码进行加密，若出现DatabaseError则注册失败
#             try:
#                 user = User.objects.create_user(username=mobile, mobile=mobile, password=password)
#             except DatabaseError as e:
#                 logger.error(e)
#                 return HttpResponseBadRequest('注册失败，请重试')
#
#             # 4.注册成功后即表示用户认证通过，设置状态保持
#             # 当前站点存储sessionid的信息，且Redis服务器中存储sessionid的信息
#             login(request, user)
#
#             # 5.注册成功则重定向至首页
#             # redirect 进行重定间
#             # reverse  可以通过namespace:name 来获取到视图所对应的路由
#             response = redirect(reverse('home:index'))
#
#             # 6.设置cookie信息
#             # 设置登录状态，会话结束后自动过期
#             response.set_cookie("is_login", True)
#             # 设置首页用户名，设置有效期为7天
#             response.set_cookie("username", user.username, max_age=7 * 24 * 3600)
#
#             # 7.响应注册结果
#             return response


# 定义生成图形验证码视图
class ImageCodeView(View):
    def get(self, request):
        #1.接收前端传递过来的uuid
        uuid = request.GET.get('uuid')
        #2.判断uuid是否获取到
        if uuid is None:
            return HttpResponseBadRequest('请求参数未携带uuid')
        #3.通过调用captcha来生成图片验证码(图片二进制和图片内容)
        text, image = captcha.generate_captcha()
        #4.将图片内容保存到redis中，其中uuid作为一个key，图片内容作为一个value，同时需要设置一个实效性
        #获取Redis连接
        redis_conn = get_redis_connection('default')
        #存储 第一个参数key键：img:uuid 第二个参数：时效性，单位是s  第三个参数value值：text验证码文本内容
        redis_conn.setex('img:%s' %uuid, 300, text)
        #5.响应图片二进制
        return HttpResponse(image, content_type='image/jpeg')

# 定义生成短信验证码视图
class SmsCodeView(View):
    def get(self, request):
        # 1.按收参数，查询字符串的形式传递过来 mobile image_code uuid
        mobile = request.GET.get('mobile')
        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('uuid')

        # 2.参数的验证
        # 2.1 验证参数是否齐全
        if not all([mobile,image_code_client,uuid]):
            return JsonResponse({'code':RETCODE.NECESSARYPARAMERR , 'errormsg':'缺少必传参数'})

        # 2.2 验证图片验证码
        #连接redis，获取redis中的图片验证码；
        redis_conn = get_redis_connection('default')
        image_code_server = redis_conn.get('img:%s' %uuid)
        #判断图片验证码是否存在；
        if image_code_server is None:
            return JsonResponse({'code': RETCODE.IMAGECODEERR, 'errormsg': '图片验证码验证失败'})
        #如果图片验证码未过期，我们获取到之后就可以删除图片验证码；
        try:
            redis_conn.delete('img:%s' %uuid)
        except Exception as e:
            logger.error(e)
        #比对图片验证码，注意大小写问题，其中redis中的数据是bytes类型； decode()
        if image_code_client.lower() != image_code_server.decode().lower() :
            return JsonResponse({'code': RETCODE.IMAGECODEERR, 'errormsg': '输入图片验证码有误'})

        # 3.生成4位短信验证码，并将其记录至日志中
        sms_code = '%04d' %randint(0,9999)
        logger.info(sms_code)

        # 4.保存短信验证码到redis中，并设置有效期
        redis_conn.setex('sms:%s' % mobile, 300, sms_code)

        # 5.发送短信 第一个参数：手机号码  第二个参数：内容数据格式为数组,[短信验证码,有效期] 第三个参数：模板Id
        CCP().send_template_sms(mobile , [sms_code , 5] , 1)

        # 6.返回响应
        return JsonResponse({'code': RETCODE.OK, 'errormsg': '发送短信验证码成功'})

# 定义用户登录的视图
class LoginView(View):
    # GET方式，处理显示登录界面
    def get(self , request):
        return render(request , 'login.html')

    # POST方式，处理登录的逻辑
    def post(self , request):
        # 1.接收表单参数
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        remember = request.POST.get('remember')

        # 2.校验参数
        # 2.1 判断参数是否齐全
        if not all([mobile , password]):
            return HttpResponseBadRequest('缺少必传参数')

        # 2.2 判断手机号是否正确
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseBadRequest('请输入正确的手机号')
        # 2.3 判断密码是否是8-20个数字
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return HttpResponseBadRequest('请输入8-20位密码')

        # 3.认证登录用户（认证字段已经在User模型中的USERNAME_FIELD = 'mobile'修改）
        # 3.1 判断用户是否存在
        user = authenticate(mobile=mobile,password=password)
        # 3.2 不存在则提示用户名或密码错误
        if user is None:
            return HttpResponseBadRequest('账号或密码输入有误')

        # 4.实现状态保持
        login(request, user)

        # 5.根据next参数来设置响应结果
        next = request.GET.get('next')
        if next:
            response = redirect(next)
        else:
            response = redirect(reverse('home:index'))

        # 6.设置状态保持的周期
        if remember !='on':
            # 6.1 没有记住用户：浏览器会话结束就过期，设置cookie，is_login和username
            request.session.set_expiry(0)
            response.set_cookie('is_login' , True)
            response.set_cookie('username' , user.username , max_age=7*24*3600)
        else:
            # 6.2 记住用户：None表示两周后过期，设置cookie，is_login和username
            request.session.set_expiry(None)
            response.set_cookie('is_login', True ,max_age=14*24*3600)
            response.set_cookie('username', user.username, max_age=14 * 24 * 3600)

        # 7.返回响应
        return response

class LogoutView(View):
    def get(self , request):
        # 1.清理session
        logout(request)
        # 2.退出登录，重定向到登录页
        response = redirect(reverse('home:index'))
        # 3.退出登录时清除cookie中的登录状态
        # 由于首页中登录状态是从cookie中读取的；所以退出登录时，需要将cookie中登录状态清除。
        response.delete_cookie('is_login')
        response.delete_cookie('username')
        # 4.返回响应
        return response

# 定义用户中心的视图
class CenterView(LoginRequiredMixin, View):
     # 展示用户中心
     def get(self, request):
        user = request.user
        # 携带数据至前端页面
        context = {
            "username":user.username,
            "avatar":user.avatar.url if user.avatar else None,
            "mobile":user.mobile,
            "desc":user.desc,
        }
        return render(request ,'center.html' , context=context)
     # 修改用户中心
     def post(self, request):
         user = request.user
         # 1.接收参数
         avatar = request.FILES.get('avatar')
         # 获取用户名，若没有获取到用户名，则使用原本的用户信息
         username = request.POST.get('username' , user.username)
         # 获取简介，若没有获取到简介，则使用原本的用户信息
         desc = request.POST.get('desc' , user.desc)

         # 2.将参数保存起来
         try:
             user.username = username
             user.desc = desc
             if avatar:
                 user.avatar = avatar
             # 保存数据至数据库中
             user.save()
         except Exception as e:
            logger.error(e)
            return HttpResponseBadRequest('个人中心更新失败')

         # 3.刷新当前页面(重定向至center)
         response = redirect(reverse('users:center'))
         # 4.更新cookie中的username信息
         response.set_cookie('username' , user.username , max_age=7*24*3600)
         # 5.返回响应
         return response
