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
