# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-09 14:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0006_course_teacher'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='is_banner',
            field=models.BooleanField(default=False, verbose_name='是否是轮播图'),
        ),
    ]
