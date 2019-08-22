#!/usr/bin/env python
# coding=utf-8
from django.shortcuts import render
from django import forms
from django.forms import fields,widgets
from django.core.exceptions import ValidationError
from R6K import models
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings

class RegisterForm(forms.Form):
    username = forms.EmailField(
        widget=widgets.EmailInput(
            attrs={'class':'form-control col-sm-3','placeholder':'please use your email','style':"margin-left: 15px;width: 93%"}
        ),
        min_length=6,
        max_length=32,
        error_messages={
            'required': '* The user name cannot be empty',
            'invalid':'* The user name should be in email format',
            'min_length':'* The user name must be at least 6 characters long',
            'max_length':'* The user name cannot exceed 32 characters',
        },
    )
    password = fields.CharField(
        widget=widgets.PasswordInput(attrs={'class':'form-control col-sm-3','placeholder':'密码为4-12个字符','style':"margin-left: 15px;width: 93%"}),
        min_length=4,
        max_length=12,
        error_messages={'required':'* The password cannot be empty',
                        'min_length':'* Password length cannot be less than 4 characters',
                        'max_length':'* Password length cannot be longer than 12 characters'}
    )
    confirm_pwd = fields.CharField(
        widget=widgets.PasswordInput(attrs={'class': 'form-control col-sm-3', 'placeholder': '密码为4-12个字符','style':"margin-left: 15px;width: 93%"}),
        min_length=4,
        max_length=12,
        error_messages={'required':'* The password cannot be empty',
                        'min_length':'* Password length cannot be less than 4 characters',
                        'max_length':'* Password length cannot be longer than 12 characters'}
    )
    eid=fields.CharField(
        widget=widgets.TextInput(attrs={'class': 'form-control col-sm-3', 'placeholder': '请输入eid','style':"margin-left: 15px;width: 93%"}),
        min_length=7,max_length=7,
        error_messages={'required':'* eid cannot be empty',
                        'min_length':'* eid length cannot be less than 7 characters',
                        'max_length':'* eid length cannot be more than 7 characters'}
    )
    team=fields.CharField(
        widget=widgets.TextInput(attrs={'class': 'form-control col-sm-3', 'placeholder': '请输入team name','style':"margin-left: 15px;width: 93%"}),
        min_length=2,max_length=11,
        error_messages={'required':'* team name cannot be empty',
                        'min_length':'* team name length cannot be less than 2 characters',
                        'max_length':'* team name length cannot be more than 11 characters'})
    linechoice=fields.ChoiceField(
        choices=((0,'NT'),
                 (1,'HW'),
                 (2,'FPGA'),
                 (3,'FDU A'),
                 (4,'FDU B'),
                 (5,'FDU C'),
                 (6,'FDU D'),
                 (7,'FDU E'),
                 (8,'FDU F'),
                 (9,'FDU G'),
                 (10,'FDU H'),
                 (11,'PIDS'),
                 (12,'EOT'),),
        error_messages={'invalid':'* Please have a choice'})
    def clean_username(self):
        #对于username扩展验证,查看是否存在
        username = self.cleaned_data['username'].lower()
        users = models.user_info.objects.filter(username=username).count()
        if users:#如果用户名已存在
            raise ValidationError('* The username was existed')
        return username

    def __init__(self,request,*args,**kwargs):#构造方法,传request参数
        super(RegisterForm,self).__init__(*args,**kwargs)#完成原有form功能以外
        self.request = request#再封装一个request

    def clean(self):  # 验证两次输入密码是否一致
        p1 = self.cleaned_data.get('password')
        p2 = self.cleaned_data.get('confirm_pwd')
        if p1 != p2:
            raise ValidationError('* Entered passwords differ')

    def clean_eid(self):
        #对于username扩展验证,查看是否存在
        eid = self.cleaned_data['eid'].lower()
        users = models.user_info.objects.filter(eid=eid).count()
        if users:#如果用户名已存在
            raise ValidationError('* The eid was existed')
        return eid

class LoginForm(forms.Form):
    username = fields.CharField(widget=widgets.TextInput(attrs={'class': 'form-control', 'placeholder': 'Please input username'}))
    password = fields.CharField(widget=widgets.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Please input password'}))
    rmb = fields.IntegerField(required=False)
    # check_code = fields.CharField(error_messages={'required': '验证码不能为空.'})
    def clean_username(self):
        # 对于username扩展验证,查看是否存在
        username = self.cleaned_data['username'].lower()
        users = models.user_info.objects.filter(username=username).count()
        if not users:  # 如果用户名已存在
            raise ValidationError('* The username was not exist.')
        return username

    def __init__(self,request,*args,**kwargs):#构造方法,传request参数
        super(LoginForm,self).__init__(*args,**kwargs)#完成原有form功能以外
        self.request = request#再封装一个request

class ChangePwd(forms.Form):
    oldpwd = fields.CharField(widget=widgets.PasswordInput(attrs={'class': 'form-control'}),min_length=4,max_length=12)
    password = fields.CharField(widget=widgets.PasswordInput(attrs={'class':'form-control'}),min_length=4,max_length=12)
    confirm_pwd = fields.CharField(widget=widgets.PasswordInput(attrs={'class': 'form-control'}),min_length=4,max_length=12)
    def clean(self):  # 验证两次输入密码是否一致
        p1 = self.cleaned_data.get('password')
        p2 = self.cleaned_data.get('confirm_pwd')
        # print(p1,p2)
        if p1 != p2:
            raise ValidationError('* Entered passwords differ')

    def __init__(self,request,*args,**kwargs):#构造方法,传request参数
        super(ChangePwd,self).__init__(*args,**kwargs)#完成原有form功能以外
        self.request = request#再封装一个request

def login(request):
    if request.method=='GET':
        redirect_to = request.GET.get('next')
        obj=LoginForm(request)
        return render(request,'login.html',{'obj':obj,'next':redirect_to})
    elif request.method=='POST':
        redirect_to = request.POST['next']
        obj=LoginForm(request,request.POST)
        if obj.is_valid():
            username = obj.cleaned_data['username'].lower()
            import hashlib
            password = hashlib.md5(b'ericsson')
            password.update(obj.cleaned_data['password'].encode('utf-8'))
            user_info = models.user_info.objects.filter(username=username, password=password.hexdigest()). \
                values('nid', 'username', 'eid','team','line','superuser').first()
            if not user_info:
                obj.add_error('password', '* Wrong password')
                return render(request,'login.html',{'obj':obj})
            else:
                request.session['user_info'] = user_info
                if obj.cleaned_data['rmb']:
                    request.session.set_expiry(60 * 60 * 24 * 30)
                if (redirect_to=='None') or (not redirect_to) or ('register' in redirect_to):
                    return redirect('/r6k/nodes')
                else:
                    return redirect(redirect_to)
        else:
            return render(request,'login.html',{'obj':obj})

def register(request):
    if request.method=='GET':
        redirect_to = request.GET.get('next')
        obj=RegisterForm(request)
        return render(request,'register.html',{'obj':obj,'next':redirect_to})
    elif request.method=='POST':
        redirect_to = request.POST['next']
        obj=RegisterForm(request,request.POST)
        if obj.is_valid():
            import hashlib
            pwd=hashlib.md5(b'ericsson')
            pwd.update(obj.cleaned_data['password'].encode("utf-8"))
            user=models.user_info.objects.create(
                username=obj.cleaned_data['username'].lower(),
                password=pwd.hexdigest(),
                eid=obj.cleaned_data['eid'].lower(),
                team=obj.cleaned_data['team'].upper(),
                line=obj.cleaned_data['linechoice']
            )
            try:
                send_mail('Account register', 'Hi %s,\nYour account %s was registered. If you forget your password, you can reset your password.\n\n\n\n\nhttp://10.185.57.124:8888/r6k' %(user.eid,user.username),settings.EMAIL_HOST_USER,[user.username], fail_silently=False)
            except Exception as e:
                print(e)
            if (redirect_to=='None') or (not redirect_to):
                return redirect('/r6k/login')
            else:
                return redirect('/r6k/login?next='+redirect_to)
        else:
            return render(request,'register.html',{'obj':obj})

def logout(request):
    '''
    注销
    :param request:
    :return:
    '''
    request.session.clear()
    return redirect('/r6k')
from django.shortcuts import redirect


def check_login(func):
    def inner(request, *args, **kwargs):
        if request.session.get('user_info'):
            return func(request, *args, **kwargs)
        else:
            return redirect('/r6k/login')
    return inner

@check_login
def userdetail(request):
    obj=request.session.get('user_info')
    print(request.get_raw_uri())
    if request.method=='GET':
        line_choices=models.user_info.objects.model.line_choice
        line_choice=obj['line']
        # print('userdetail',obj,line_choices,line_choice)
        return render(request,'user-info.html',locals())
    if request.method=='POST':
        team=request.POST['team']
        line=int(request.POST['line'])
        username=request.session.get('user_info')['username']
        models.user_info.objects.filter(username=username).update(team=team,line=line)
        # print(team,line)
        return redirect('/r6k')

@check_login
def changepwd(request):
    if request.method == 'GET':
        obj = ChangePwd(request)
        return render(request, 'changepwd.html',{'obj':obj})
    if request.method == 'POST':
        message=''
        obj = ChangePwd(request, request.POST)
        #验证两次输入密码一致
        if obj.is_valid():
            import hashlib
            pwd = hashlib.md5(b'ericsson')
            pwd.update(obj.cleaned_data['oldpwd'].encode("utf-8"))
            #验证原密码是否正确
            verify=models.user_info.objects.filter(nid=request.POST['nid'],password=pwd.hexdigest()).count()
            #原密码验证不通过
            if not verify:
                message='* The old password was wrong!'
                return render(request, 'changepwd.html', locals())
            else:
                #原密码验证通过，存储新密码
                pwd = hashlib.md5(b'ericsson')
                pwd.update(obj.cleaned_data['password'].encode("utf-8"))
                models.user_info.objects.filter(nid=request.POST['nid']).update(password=pwd.hexdigest())
            return redirect('/r6k')
        return render(request,'changepwd.html',locals())

@csrf_exempt
def resetpwd(request):
    import random,string,hashlib
    ret={'status':True,'message':None}
    if request.method == 'POST':
        if not models.user_info.objects.filter(username=request.POST['account'].lower()).count():
            ret['status']=False
            ret['message']='The user %s is not registered yet.' %request.POST['account']
        else:
            pwd = hashlib.md5(b'ericsson')
            #随机生成6位密码
            newpwd=''.join(random.choice(string.ascii_uppercase+string.ascii_lowercase+string.digits) for _ in range(6))
            pwd.update(newpwd.encode("utf-8"))
            try:
                send_mail('Reset password', 'Your password had been reset, your new password is %s.\n\n\n\n\nhttp://10.185.57.124:8888/r6k' %newpwd,settings.EMAIL_HOST_USER,[request.POST['account']], fail_silently=False)
            except Exception as e:
                print(e)
            models.user_info.objects.filter(username=request.POST['account'].lower()).update(password=pwd.hexdigest())
    return JsonResponse(ret)