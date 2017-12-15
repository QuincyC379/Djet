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

    def checkbox(self, obj=None, is_header=False):
        if is_header:
            return '选择'
        return mark_safe('<input type="checkbox" val=%s>' % obj.id)

    def edit(self, obj=None, is_header=False):
        if is_header:
            return '操作'
        return mark_safe('<a href="/edit/%s/">编辑</a>' % obj.id)

    list_display = [checkbox, 'id', 'name', 'pwd', edit]


service.site.regiser(UserInfo, UserInfoConfig)
