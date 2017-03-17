#coding:utf-8
from django.shortcuts import render,redirect
from django.template.context_processors import request
from django.http.response import HttpResponse
from django.shortcuts import render_to_response
from forms import userregister,codecommit
from models import userinfo,hostinfo,saltcommandhistory,codeupdate
from django.utils.safestring import mark_safe
from django.db import connection
from django.db.models import Count
import json
import salt.client 
from datetime import datetime
from datetime import timedelta 
import salt.config
import zerorpc
import os
class DateTimeEncoder(json.JSONEncoder):
    def default(self,o):
        if isinstance(o,datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self,o)
# Create your views here.
#检测是否已经登录
def checklogin(func):
    def warper(request,*args,**kwargs):
        if request.session.get('login_info',None):
            return func(request,*args,**kwargs)
        else:
            return render_to_response("signin.html")
    return warper
#获得时间序列
def getdatelist(begin_date,end_date):
    date_list = []
    begin_date = datetime.strptime(begin_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    while begin_date <= end_date:
        date_str = begin_date.strftime("%Y-%m-%d")
        date_list.append(date_str)
        begin_date += timedelta(days=1)
    return date_list
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
    updatenum=codeupdate.objects.all().count()
    username=request.session['login_info']['username']
    return render_to_response("index.html",{'username':username,'hostlist':hostlist,'hostnum':hostnum,"updatenum":updatenum})
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
@checklogin
def saltcontrol(request):
    loginstatus=request.session.get('login_info',None)
    username=loginstatus['username']
    tgt_type=request.POST.get('miniontype','glob')
    minion=request.POST.get('minion',None)
    saltmodule=request.POST.get('module',None)
    module_arg=request.POST.get('arg',None)
    try:
        saltcommandhistory.objects.create(username=username,minions=minion,miniontype=tgt_type,module=saltmodule,arg=module_arg)
    except Exception,e:
        print e.message
    else:
        print "ok"
    local = salt.client.LocalClient()
    if module_arg:
        result=local.cmd(minion,saltmodule,arg=(module_arg,),expr_form=tgt_type)
    else:
        result=local.cmd(minion,saltmodule,expr_form=tgt_type)
#    return render_to_response("index.html",{"dicts":result,'username':loginstatus['username']},context_instance=RequestContext(request))
    return HttpResponse(json.dumps(result))

@checklogin
def showcmdhistory(request):
    username=request.session['login_info']['username']
    updatenum=codeupdate.objects.all().count()
    cmdhistoryresult=saltcommandhistory.objects.all()
    return render_to_response('commandhistory.html',{'cmddicts':cmdhistoryresult,"username":username,"updatenum":updatenum})
@checklogin
def saltconfig(request):
    username=request.session['login_info']['username']
    if os.path.exists('/tmp/saltconf.tmp'):
        master_conf=json.load(open('/tmp/saltconf.tmp','r'))
    else:
        master_ops = salt.config.client_config('/etc/salt/master')
        master_conf={"interface":master_ops['interface'],"publish_port":master_ops["publish_port"],"max_open_files":master_ops["max_open_files"],"worker_threads":master_ops["worker_threads"],"ret_port":master_ops["ret_port"],"pidfile":master_ops["pidfile"],"root_dir":master_ops["root_dir"]}
        with open('/tmp/saltconf.tmp','w') as fd:
            json.dump(master_conf,fd)
    return render_to_response('saltconfig.html',{"username":username,"dicts":master_conf})
@checklogin
def saltadmin(request):
    username=request.session['login_info']['username']
    return render_to_response('saltadmin.html',{"username":username})
@checklogin
def hoststatus(request):
    ip=request.GET.get('ip',None).split('/')[0]
    c = zerorpc.Client()
    addr='tcp://'+ip+':4242'
    c.connect("tcp://127.0.0.1:4242")
    cpu=c.get_sysinfo()
    username=request.session['login_info']['username']
    return render_to_response('hoststatus.html',{"username":username,'hostip':ip,'cpu':cpu})
@checklogin
def filterhistory(request):
    st=request.POST.get("st",None)
    et=request.POST.get("et",None)
    if all([st,et]):
        hisresult=saltcommandhistory.objects.filter(createtime__range=(st,et))
        resultlist=[]
        for item in hisresult:
            resultlist.append({"id":item.id,"username":item.username,"createtime":item.createtime,"minions":item.minions,"miniontype":item.miniontype,"module":item.module,"arg":item.arg})
        resultdata=json.dumps(resultlist,cls=DateTimeEncoder)
        return HttpResponse(resultdata)
@checklogin
def codepublish(request):
    username=request.session['login_info']['username']
    updatenum=codeupdate.objects.all().count()
    start_date=(datetime.now()+timedelta(days=-7)).strftime('%Y-%m-%d')
    end_date=datetime.now().strftime('%Y-%m-%d')
    datelist=getdatelist(start_date,end_date)
    user_list=codeupdate.objects.values('commituser').distinct()
    select = {'day': connection.ops.date_trunc_sql('day', 'Createtime')}
    data_list=[]
    for user in user_list:
        result=codeupdate.objects.extra(select=select).filter(commituser=user['commituser']).values('day').annotate(number=Count('svninfo'))
        num_list=[]
        for i in range(len(datelist)):
            num_list.append(0)
#        for d in datelist:
        for num in result:
            if num['day'].strftime('%Y-%m-%d') in datelist:
                dindex=datelist.index(num['day'].strftime('%Y-%m-%d'))
                num_list[dindex]=(num['number'])
        data_list.append({"name":str(user['commituser']),"data":num_list})
    print data_list 
    print datelist
    print user_list[0]['commituser']
    return render_to_response('codepublish.html',{"username":username,"form":codecommit,"updatenum":updatenum,"datetimelist":datelist,"datalist":data_list})
@checklogin
def commitcount(request):
    username=request.session['login_info']['username']
    updateresult=codeupdate.objects.all()
    updatenum=codeupdate.objects.all().count()
    result_list=[]
    for item in updateresult:
        peoplename=userinfo.objects.filter(id=item.auditor).values_list("Name")[0][0] 
        if item.status==1:
            status=mark_safe('<button class="layui-btn layui-btn-mini layui-btn-radius layui-btn-normal">已审核</button>')
            result_list.append({"commituser":item.commituser,"svninfo":item.svninfo,"describtion":item.describtion,"auditor":peoplename,"status":status,"Createtime":item.Createtime})
        else:
            status=mark_safe('<button class="layui-btn layui-btn-mini layui-btn-radius layui-btn-danger">未审核</button>')
            result_list.append({"commituser":item.commituser,"svninfo":item.svninfo,"describtion":item.describtion,"auditor":peoplename,"status":status,"Createtime":item.Createtime}) 
    return render_to_response('updatecount.html',{"username":username,"updatenum":updatenum,"result_list":result_list})
@checklogin
def commitupdate(request):
    ret={}
    form=codecommit()
    username=request.session['login_info']['username']
    print request.method
    if request.method == 'POST':
        code_form=codecommit(request.POST)
        if code_form.is_valid():
            code_dic=code_form.clean()
            print code_dic
            try:
                codeupdate.objects.create(commituser=username,svninfo=code_dic['svninfo'],describtion=code_dic['explain'],auditor=code_dic['people'])
            except Exception,e:
                ret['status']=0
                ret['message']=e.message
                print e.message
                return HttpResponse(json.dumps(ret)) 
            else:
                ret['status']=1
                ret['message']='code has commit.'
                return HttpResponse(json.dumps(ret)) 
        else:
            ret['status']=0
            ret['message']="illegal data."
            return HttpResponse(json.dumps(ret))
