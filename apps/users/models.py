#!/usr/bin/python
#coding:utf-8
from datetime import datetime

from django.db import models

from django.contrib.auth.models import AbstractUser
# Create your models here.


class UserProfile(AbstractUser):
    nick_name = models.CharField(max_length=50, verbose_name='昵称', default='')
    birthday = models.DateField(null=True, blank=True, verbose_name='生日')
    gender = models.CharField(max_length=6, choices=(('male', '男'), ('female', '女')), default='female', verbose_name='性别')
    address = models.CharField(max_length=100, default='', verbose_name='地址')
    mobile = models.CharField(max_length=11, null=True, blank=True, verbose_name='手机号')
    image = models.ImageField(max_length=100, upload_to='image/%Y/%m', default='image?default.png', verbose_name='头像')
    ols_motivational = models.FloatField(default=0.0, verbose_name='动机')
    ols_communicational = models.FloatField(default=0.0, verbose_name='交流')
    ols_visual = models.FloatField(default=0.0, verbose_name='视觉')
    ols_verbal = models.FloatField(default=0.0, verbose_name='言语')
    ols_sensing = models.FloatField(default=0.0, verbose_name='感悟')
    ols_intuitive = models.FloatField(default=0.0, verbose_name='直觉')
    ols_sequential = models.FloatField(default=0.0, verbose_name='序列')
    ols_global = models.FloatField(default=0.0, verbose_name='综合')
    ols_cluster = models.IntegerField(default=0, verbose_name='OLS分类')

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name

    def get_unread_nums(self):
        # 获取用户未读数据数量
        from operation.models import UserMessage
        return UserMessage.objects.filter(user=self.id, has_read=False).count()

    def __str__(self):
        return self.username


class EmailVerifyRecord(models.Model):
    code = models.CharField(max_length=20, verbose_name='验证码')
    email = models.EmailField(max_length=50, verbose_name='邮箱')
    send_type = models.CharField(max_length=18, choices=(('register', '邮箱'), ('forget', '修改密码'), ('update_email', '修改邮箱')),
                                 verbose_name='验证码类型')
    send_time = models.DateField(default=datetime.now, verbose_name='发送时间')

    class Meta:
        verbose_name = '邮箱验证码'
        verbose_name_plural = '邮箱验证码'


class Banner(models.Model):
    title = models.CharField(max_length=100, verbose_name='标题')
    image = models.ImageField(upload_to='banner/%Y/%m', max_length=100, verbose_name='轮播图')
    url = models.URLField(max_length=200, verbose_name='访问地址')
    index = models.IntegerField(default=100, verbose_name='顺序')
    add_time = models.DateField(default=datetime.now, verbose_name='添加时间')

    class Meta:
        verbose_name = '轮播图'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title