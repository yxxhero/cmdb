#coding:utf-8
from django.shortcuts import render,redirect
from django.template.context_processors import request
from django.http.response import HttpResponse
from django.shortcuts import render_to_response
from forms import userregister
from models import userinfo,hostinfo
from django.utils.safestring import mark_safe
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
    hostlist=[]
    tmp_list=hostinfo.objects.all()
    for i in tmp_list:
        if i.status:
            i.status=mark_safe('<i class="fa fa-circle ok_status" aria-hidden="true"></i>')
        else:
            i.status=mark_safe('<i class="fa fa-circle warn_status" aria-hidden="true"></i>')
        hostlist.append(i)
    hostnum=hostinfo.objects.all().count()
    username=request.session['login_info']['username']
    return render_to_response("index.html",{'username':username,'hostlist':hostlist,'hostnum':hostnum})
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
def logout(request):
    del request.session['login_info']
    return render_to_response('signin.html')
def posthostinfo(request):
    clinet_host_info=eval(request.POST.get('host_info',None))
    print clinet_host_info
    num=hostinfo.objects.filter(hostname=clinet_host_info['hostname']).count()
    print num
    if num < 1:
        host_dic={}
        host_dic['hostname']=clinet_host_info['hostname']
        host_dic['ip']=clinet_host_info['ip_dict']['eth1']
        host_dic['system']=clinet_host_info['system_name']
        host_dic['project']='dark'
        host_dic['services']=' '.join(clinet_host_info['processlist'])
        hostinfo.objects.create(**host_dic)
        return HttpResponse('ok')
    else:
        return HttpResponse('Host already exists')
def deletehost(request):
    hostid=request.POST.get("id",None)
    if hostid:
        try:
            hostinfo.objects.filter(id=hostid).delete()
        except Exception,e:
            print e
            return HttpResponse("false")
        else:
            return HttpResponse("ok")
