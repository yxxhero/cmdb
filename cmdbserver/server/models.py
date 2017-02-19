#!/usr/bin/env python2.7
#coding:utf-8
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class userinfo(models.Model):
    Name=models.CharField(max_length=255)
    Email=models.EmailField()
    Password=models.CharField(max_length=255)
    Is_admin=models.BooleanField(default=0)
    Createtime=models.DateTimeField(auto_now_add=True)
    Updatetime=models.DateTimeField(auto_now = True)
class hostinfo(models.Model):
    hostname=models.CharField(max_length=255)
    ip=models.GenericIPAddressField()
    minionid=models.CharField(max_length=255,null=True)
    system=models.CharField(max_length=255)
    project=models.CharField(max_length=255)
    location=models.CharField(max_length=255,null=True)
    services=models.CharField(max_length=255,null=True)
    status=models.BooleanField(default=1)
    Createtime=models.DateTimeField(auto_now_add=True)
    Updatetime=models.DateTimeField(auto_now = True)
class saltcommandhistory(models.Model):
    username=models.CharField(max_length=30)
    createtime=models.DateTimeField(auto_now_add = True)
    minions=models.CharField(max_length=255)
    miniontype=models.CharField(max_length=255)
    module=models.CharField(max_length=255)
    arg=models.CharField(max_length=255,null=True)
    class Meta:
        verbose_name = '命令历史'
        verbose_name_plural = '命令历史'
class codeupdate(models.Model):
    commituser=models.CharField(max_length=255)
    svninfo=models.CharField(max_length=255)
    describtion=models.CharField(max_length=255)
    auditor=models.CharField(max_length=255)
    status=models.BooleanField(default=0)
    Createtime=models.DateTimeField(auto_now_add=True)
    Updatetime=models.DateTimeField(auto_now = True)    
