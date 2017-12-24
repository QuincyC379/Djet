from django.http import HttpResponse
from django.shortcuts import render
from django.urls import path
from django.utils.safestring import mark_safe


class CrudConfig:

    def __init__(self, model, crud_site):
        self.model = model
        self.crud_site = crud_site

    # 页面展示
    list_display = []

    def get_list_display(self):
        """
        默认显示选择、编辑和删除
        :return:
        """
        result = []
        if self.list_display:
            result.append(CrudConfig.checkbox)
            result.extend(self.list_display)
            result.append(CrudConfig.edit)
            result.append(CrudConfig.delete)
        return result

    @property
    def urls(self):
        return self.get_urls()

    def get_urls(self):
        info = self.model._meta.app_label, self.model._meta.model_name
        urlpatterns = [
            path('', self.changelist_view, name='%s_%s_changelist' % info),
            path('add/', self.add_view, name='%s_%s_add' % info),
            path('<int:obj_id>/change/', self.change_view, name='%s_%s_change' % info),
            path('<int:obj_id>/delete/', self.delete_view, name='%s_%s_delete' % info),
        ]
        return urlpatterns

    def changelist_view(self, request):
        """
        处理数据表头及展示数据
        :param request:
        :return:
        """
        header_list = []
        for header in self.get_list_display():
            if isinstance(header, str):
                val = self.model._meta.get_field(header).verbose_name
            else:
                # 函数处理
                val = header(self, is_header=True)
            header_list.append(val)

        """
        处理展示数据
        """
        data_list = self.model.objects.all()
        new_data_list = []
        for data in data_list:
            temp = []
            for field in self.get_list_display():
                if isinstance(field, str):
                    val = getattr(data, field)
                else:
                    val = field(self, data)
                temp.append(val)
            new_data_list.append(temp)

        return render(request, 'change_list.html', {'data_list': new_data_list, 'header_list': header_list})

    def add_view(self, request):
        return HttpResponse('添加')

    def change_view(self, request, obj_id):
        return HttpResponse('修改')

    def delete_view(self, request, obj_id):
        return HttpResponse('删除')

    # 自定义checkbox,edit，delete
    def checkbox(self, obj=None, is_header=False):
        if is_header:
            return '选择'
        return mark_safe('<input type="checkbox" value=%s>' % obj.id)

    def edit(self, obj=None, is_header=False):
        if is_header:
            return '操作0'
        return mark_safe('<a href="/edit/%s/">编辑</a>' % obj.id)

    def delete(self, obj=None, is_header=False):
        if is_header:
            return '操作1'
        return mark_safe('<a href="/delete/%s/">删除</a>' % obj.id)


class CrudSite:

    def __init__(self):
        self._registry = {}

    def regiser(self, model, crud_config=None):
        """
        将所有模型类中的类注册到self._registry中，方便后期遍历循环
        :param model: 模型类
        :param crud_config: 要注册的配置类
        :return:
        """
        if not crud_config:
            crud_config = CrudConfig
        self._registry[model] = crud_config(model, self)

    @property
    def urls(self):
        return self.get_urls(), None, 'crud'

    def get_urls(self):
        urlpatterns = []
        for model, crud_config_obj in self._registry.items():
            urlpatterns += [
                path('%s/%s/' % (model._meta.app_label, model._meta.model_name), (crud_config_obj.urls, None, None))
            ]

        return urlpatterns


site = CrudSite()
