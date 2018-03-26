from django.shortcuts import render, redirect
from django.views.generic import View
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login
from .models import User
import re
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired


# Create your views here.
class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html', {'title': '注册'})

    def post(self, request):
        dic = request.POST
        uname = dic.get('user_name')
        pwd = dic.get('pwd')
        cpwd = dic.get('cpwd')
        email = dic.get('email')
        allow = dic.get('allow')
        context = {
            'erro_msg': '',
            'uname': uname,
            'pwd': pwd,
            'cpwd': cpwd,
            'email': email,
            'title': '注册'
        }
        if not all([uname, pwd, cpwd, email]):
            context['erro_msg'] = '请填写正确信息'
            return render(request, 'register.html', context)
        if not allow:
            context['erro_msg'] = '请同意协议'
            return render(request, 'register.html', context)
        if pwd != cpwd:
            context['erro_msg'] = '两次输入的密码不一致'
            return render(request, 'register.html', context)
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            context['erro_msg'] = '请输入正确邮箱地址'
            return render(request, 'register.html', context)
        if User.objects.filter(username=uname).count() > 0:
            context['erro_msg'] = '用户名以存在'
            return render(request, 'register.html', context)
        if User.objects.filter(email=email).count() > 0:
            context['erro_msg'] = '该邮箱以被注册'
            return render(request, 'register.html', context)
        user = User.objects.create_user(uname, email, pwd)
        user.is_active = False
        user.save()
        serializer = Serializer(settings.SECRET_KEY, 60 * 60)
        value = serializer.dumps({'id': user.id}).decode()
        msg = '<a herf="http://127.0.0.1:8080/user/active/%s">点击激活</a>' % value
        send_mail('天天生鲜-账户激活', '', settings, settings.EMAIL_FROM, [email], html_message=msg)
        return render(request, 'register.html', context)


def active(request, value):
    try:
        serializer = Serializer(settings.SECRET_KEY)
        dict = serializer.loads(value)
    except SignatureExpired as e:
        return HttpResponse('连接已过期')
    uid = dict.get('id')
    user = User.objects.get(pk=uid)
    user.is_active = True
    user.save()
    return redirect('/user/login')


def exists(request):
    uname = request.GET.get('uname')
    # 判断用户是否存在
    if uname is not None:
        result = User.objects.filter(username=uname).count()
    return JsonResponse({'result': result})


class LoginView(View):
    def get(self, request):
        uname = request.COOKIES.get('uname','')
        context = {
            'title':'登陆',
            'uname':uname
        }
        return render(request, 'login.html', context)

    def post(self, request):
        dic = request.POST
        uname = dic.get('username')
        pwd = dic.get('pwd')
        remembername = dic.get('rembername')
        context = {
            'erro_msg': '',
            'uname': uname,
            'pwd': pwd,
            'title': '登陆',
        }
        if not all([uname, pwd]):
            context['erro_msg'] = '请填写完整信息'
            return render(request, 'login.html', context)
        user = authenticate(username=uname, password=pwd)
        if user is None:
            context['erro_msg'] = '用户名或密码错误'
            return render(request, 'login.html', context)
        # 如果未激活不允许登陆
        if not user.is_active:
            context['erro_msg'] = '请先到邮箱激活'
            return render(request, 'login.html', context)
        # 状态保持
        login(request, user)
        # 记住用户名
        response = redirect('/user/info')
        if remembername is None:
            response.delete_cookie('uname')
        else:
            response.set_cookie("uname",uname,expires=60*60*24*7)

        return response
