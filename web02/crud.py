"""
相当于admin文件
"""
from crud.service import service
from web02.models import UserInfo

service.site.regiser(UserInfo)
