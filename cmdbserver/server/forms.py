#!/usr/bin/env python2.7
#coding:utf-8
from django import forms
from django.core.exceptions import ValidationError
from models import userinfo
class userregister(forms.Form):
    Name=forms.CharField(max_length=20,min_length=5,error_messages={'required':u'名称不能为空','min_length':u'名称至少为5个字符','max_length':u'名称最多为20个字符'},widget=forms.TextInput(attrs={'class': "form-control input-lg",'placeholder': u'please input your username'}))
    Email = forms.EmailField(required=True,error_messages={'required': u'邮箱不能为空','invalid': u'邮箱格式错误'},widget=forms.TextInput(attrs={'class': "form-control input-lg", 'placeholder': u'email address'}))
    Password = forms.CharField(required=True,max_length=256,widget=forms.widgets.TextInput(attrs={'class': "form-control input-lg",'type':'password', 'placeholder': u'Type a password'}))
class updatecommit1(forms.Form):
    svninfo=forms.CharField(max_length=100)
    reason=forms.CharField(max_length=256)
class updatecommit2(forms.Form):
    changelog=forms.CharField(max_length=256)
    auditor=forms.ChoiceField(choices=userinfo.objects.all().values_list('Name'),label="审核人员")
class updatecommit3(forms.Form):
    targetdate=forms.DateTimeField()
