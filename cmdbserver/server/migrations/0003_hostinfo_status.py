# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-25 01:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0002_hostinfo'),
    ]

    operations = [
        migrations.AddField(
            model_name='hostinfo',
            name='status',
            field=models.BooleanField(default=1),
        ),
    ]