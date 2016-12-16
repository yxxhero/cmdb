#coding:utf-8
from django.shortcuts import render,redirect
from django.template.context_processors import request
from django.http.response import HttpResponse
from django.shortcuts import render_to_response
import json
from forms import userregister
# Create your views here.
#检测是否已经登录
def checklogin(func):
    def warper(request,*args,**kwargs):
        if request.session.get('is_login',None):
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
    print request.method
    if request.method == 'POST':
        register_form=userregister(request.POST)
        if register_form.is_valid():
            register_dic=register_form.clean()
            print register_dic
            ret['status']=True
        else:
            error_msg=register_form.errors.as_json()
            ret['error']=json.loads(error_msg)
    else:
        form=userregister()
        return render_to_response('signup.html',{'user':form})
    return HttpResponse(json.dumps(ret))
