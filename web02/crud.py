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
    edit_link = ['name']

    # order_by = ['-name']

    search_fields = ['pk__icontains', 'name__icontains']
    search_field_form = True

    show_actions = True

    def multi_del(self, request):
        """
        批量删除数据逻辑在这处理
        :param request:
        :return:
        """
        pk_list = request.POST.getlist('pk')
        obj_list = self.model.objects.filter(pk__in=pk_list)
        print('=====>', obj_list)

    def multi_init(self, request):
        pass

    actions = [multi_del, multi_init]
    multi_del.text = '批量删除'
    multi_init.text = '批量初始化'


service.site.regiser(UserInfo, UserInfoConfig)
