#coding:utf-8
from django.shortcuts import render,redirect
from django.template.context_processors import request
from django.http.response import HttpResponse
from django.shortcuts import render_to_response
from forms import userregister
from models import userinfo
import json
# Create your views here.
#检测是否已经登录
def checklogin(func):
    def warper(request,*args,**kwargs):
        if request.session.get('login_info',None):
            return func(request,*args,**kwargs)
        else:
            return render_to_response("signin.html")
    return warper
######################################################################
@checklogin        
def index(request):
    return render_to_response("index.html")    
def login(request):
    return render_to_response("signin.html")
def register(request):
    ret={'status':False,'error':'','summary':''}
    form=userregister()
    print request.method
    if request.method == 'POST':
        register_form=userregister(request.POST)
        if register_form.is_valid():
            register_dic=register_form.clean()
            print register_dic
            num=userinfo.objects.filter(Name=register_dic['Name'],Password=register_dic['Password']).count()
            if num >= 1:
                message='用户已存在'
                return render_to_response('signup.html',{'user':form,'errormessage':message})
            else:
                try:
                    userinfo.objects.create(**register_dic)
                except Exception,e:
                    return render_to_response('signup.html',{'user':form,'errormessage':e.message})
                else:
                    message='注册成功'
                    return render_to_response('signup.html',{'user':form,'errormessage':message})
        else:
            error_msg=register_form.errors.as_json()
            ret['error']=json.loads(error_msg)
            warn_item=ret['error'].keys()[0]
            message=ret['error'][warn_item][0]['message']
            return render_to_response('signup.html',{'user':form,'errormessage':message})
    else:
        return render_to_response('signup.html',{'user':form})
def signin(request):
    Name=request.POST.get('Name',None)
    Password=request.POST.get('Password',None)
    if all([Name,Password]):
        num=userinfo.objects.filter(Name=Name,Password=Password).count()
        if num>=1:
            request.session['login_info']={'username':Name}
            return redirect('/index/')
        else:
            return render_to_response('signin.html',{'message':"用户名或密码错误"})
    else:
        return render_to_response('signin.html')
