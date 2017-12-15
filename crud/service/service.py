from django.http import HttpResponse
from django.shortcuts import render
from django.urls import path


class CrudConfig:
    list_display = []

    def __init__(self, model, crud_site):
        self.model = model
        self.crud_site = crud_site

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
        处理展示数据
        """
        data_list = self.model.objects.all()
        new_data_list = []
        for data in data_list:
            temp = []
            for field in self.list_display:
                if isinstance(field, str):
                    val = getattr(data, field)
                else:
                    val = field(self, data)
                temp.append(val)
            new_data_list.append(temp)
        return render(request, 'change_list.html', {'data_list': new_data_list})

    def add_view(self, request):
        return HttpResponse('添加')

    def change_view(self, request, obj_id):
        return HttpResponse('修改')

    def delete_view(self, request, obj_id):
        return HttpResponse('删除')


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
