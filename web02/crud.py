"""
相当于admin文件
"""
from django.utils.safestring import mark_safe

from crud.service import service
from crud.service.service import CrudConfig
from web02.models import UserInfo


class UserInfoConfig(CrudConfig):
    """
    继承CrudConfig，派生新的功能
    """

    def edit(self, obj=None):
        return mark_safe('<a href="/edit/%s/">编辑</a>' % obj.id)

    list_display = ['id', 'name', 'pwd', edit]


service.site.regiser(UserInfo, UserInfoConfig)
