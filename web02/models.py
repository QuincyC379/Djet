from django.db import models

"""
models for test
"""


# Create your models here.
class UserInfo(models.Model):
    name = models.CharField(max_length=32, verbose_name='用户名')
    pwd = models.CharField(max_length=64, verbose_name='密码')
