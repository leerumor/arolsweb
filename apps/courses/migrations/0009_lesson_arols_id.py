# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-03-03 15:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0008_bannercourse'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='arols_id',
            field=models.CharField(default='', max_length=20, verbose_name='学习资源标识符'),
        ),
    ]
