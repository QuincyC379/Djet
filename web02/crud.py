"""
相当于admin文件
"""

from crud.service import service
from crud.service.service import CrudConfig, QueryOpt
from web02.models import UserInfo, Department, UserType


class UserInfoConfig(CrudConfig):
    """
    继承CrudConfig，派生新的功能
    """

    def gender(self, obj=None, is_header=False):
        if is_header:
            return '性别'
        return obj.get_gender_display()

    list_display = ['id', 'name', gender, 'pwd']
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

    # 综合搜索
    comprehensive_search = [
        QueryOpt('gender', is_choice=True),
        QueryOpt('dept', multi=True),
        # 指定了to_field，处理:
        QueryOpt('usertype', text_func=lambda x: str(x), pk_func=lambda x: x.code),
    ]


service.site.regiser(UserInfo, UserInfoConfig)


class DepartmentConfig(CrudConfig):
    list_display = ['name']


service.site.regiser(Department, DepartmentConfig)


class UserTypeConfig(CrudConfig):
    list_display = ['title']
    edit_link = ['title']


service.site.regiser(UserType, UserTypeConfig)
