from __future__ import unicode_literals

from django.db import models

# Create your models here.
class userinfo(models.Model):
    Name=models.CharField(max_length=30)
    Email=models.EmailField()

