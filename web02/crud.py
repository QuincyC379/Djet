"""
相当于admin文件
"""

from crud.service import service
from crud.service.service import CrudConfig
from web02.models import UserInfo


class UserInfoConfig(CrudConfig):
    """
    继承CrudConfig，派生新的功能
    """

    list_display = ['id', 'name', 'pwd']


service.site.regiser(UserInfo, UserInfoConfig)
