from django.db import models

"""
models for test
"""


# Create your models here.
class UserInfo(models.Model):
    """员工"""
    name = models.CharField(max_length=32, verbose_name='用户名')
    pwd = models.CharField(max_length=64, verbose_name='密码')
    gender_choices = (
        (1, '男'),
        (2, '女')
    )
    gender = models.IntegerField(verbose_name='性别', choices=gender_choices, default=1)
    dept = models.ManyToManyField('Department', verbose_name='隶属部门')
    usertype = models.ForeignKey('UserType', verbose_name='用户类型', on_delete=models.CASCADE, null=True, blank=True,
                                 to_field='code')

    def __str__(self):
        return self.name


class Department(models.Model):
    """
    部门，初创公司
    """
    name = models.CharField(max_length=16, verbose_name='部门名称')

    def __str__(self):
        return self.name


class UserType(models.Model):
    """
    员工分类，don't bother,just for test!
    """
    title = models.CharField(max_length=16, verbose_name='员工类型')
    code = models.IntegerField(verbose_name='员工编号', unique=True, null=True, blank=True)

    def __str__(self):
        return self.title
