# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-23 15:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='hostinfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hostname', models.CharField(max_length=255)),
                ('ip', models.GenericIPAddressField()),
                ('minionid', models.CharField(max_length=255, null=True)),
                ('system', models.CharField(max_length=255)),
                ('project', models.CharField(max_length=255)),
                ('location', models.CharField(max_length=255, null=True)),
                ('services', models.CharField(max_length=255, null=True)),
                ('Createtime', models.DateTimeField(auto_now_add=True)),
                ('Updatetime', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
