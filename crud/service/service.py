from django.db.models import Q
from django.forms import ModelForm
from django.http import HttpResponse, QueryDict
from django.shortcuts import render, redirect
from django.urls import path, reverse
from django.utils.safestring import mark_safe

from crud.utils.Qpaginator import Pagination

"""
抽离代码过程中出现的request不知道怎么获取问题，
解决思路是用了装饰器wrapper单独封装了request，
在ClassList中便可以正常使用
"""


class ClassList:
    """
    抽离代码，使业务和逻辑分离
    """

    def __init__(self, config, queryset):
        self.config = config
        self._model = config.model

        pager_obj = Pagination(self.config.request.GET.get('page', 1), queryset.count(), self.config.request.path_info,
                               self.config.request.GET,
                               per_page_count=2)

        self.queryset = queryset[pager_obj.start:pager_obj.end]
        self.list_display = config.get_list_display()
        self.edit_link = config.get_edit_link()
        self.show_add_btn = config.get_show_add_btn()

        self.pager_html = pager_obj.bs_page_html()
        """
        获取Boolean值为了控制前端展示
        """
        self.show_search_field_form = config.show_search_field_form()
        # 前端页面赋值
        self.search_form_val = config.request.GET.get(config.search_key, '')
        # 前端处理显示actions
        self.show_actions = config.get_show_actions()
        self.actions = config.get_actions()

    @property
    def header_list(self):
        """
        表头部分
        :return:
        """
        header_list = []
        for header in self.config.get_list_display():
            if isinstance(header, str):
                val = self._model._meta.get_field(header).verbose_name
            else:
                # 函数处理
                val = header(self.config, is_header=True)
            header_list.append(val)

        return header_list

    @property
    def body_list(self):
        """
        数据部分
        :return:
        """
        new_data_list = []
        for data in self.queryset:
            temp = []
            for field in self.list_display:
                if isinstance(field, str):
                    val = getattr(data, field)
                else:
                    val = field(self.config, data)
                if field in self.edit_link:
                    """
                    如果当前的字段在需要编辑的列表中
                    """
                    val = self.config.edit_tag_link(data.pk, val)
                temp.append(val)
            new_data_list.append(temp)

        return new_data_list

    def add_actions(self):
        """
        改造action，用于前端显示
        :return:
        """
        action_list = []
        if self.actions:

            for func in self.actions:
                result = {'name': func.__name__, 'text': func.text}
                action_list.append(result)
        return action_list


class CrudConfig:

    def __init__(self, model, crud_site):
        """
        :param model: 当前被注册的类
        :param crud_site: site对象
        """
        self.model = model
        self.crud_site = crud_site
        self.request = None
        self._query_param_key = '_list_filter'
        self.search_key = '_q'

    def wrapper(self, func):
        """
        封装request
        :return:
        """

        def inner(request, *args, **kwargs):
            self.request = request
            return func(request, *args, **kwargs)

        return inner

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
            # result.append(CrudConfig.edit)
            result.append(CrudConfig.delete)
        return result

    # 编辑当前字段
    edit_link = []

    def get_edit_link(self):
        """
        编辑当前字段
        :return:
        """
        result = []
        if self.edit_link:
            result.extend(self.edit_link)
        return result

    # 添加按钮显示与隐藏
    show_add_btn = False

    def get_show_add_btn(self):
        return self.show_add_btn

    def get_add_btn(self):
        """
        给添加按钮赋值url
        :return:
        """
        # /crm/web02/userinfo/add
        return mark_safe('<a href=%s class="btn btn-success">添加</a>' % self.get_add_url())

    # 自定义排序
    order_by = []

    def get_order_by(self):
        result = []
        result.extend(self.order_by)
        return result

    # 自定义ModelForm
    model_form = None

    def get_model_form(self):
        if self.model_form:
            return self.model_form
        else:
            meta = type('Meta', (object,), {'model': self.model, 'fields': '__all__'})
            MyModelForm = type('MyModelForm', (ModelForm,), {'Meta': meta})
            return MyModelForm

    # 搜索字段
    search_fields = []

    search_field_form = False

    def show_search_field_form(self):
        """
        用于封装到classlist中，前端控制展示与隐藏
        :return:
        """
        return self.search_field_form

    def get_search_fields(self):
        result = []
        if self.search_fields:
            result.extend(self.search_fields)

        return result

    def get_search_condition(self):
        """
        构造Q对象
        :return:
        """
        query_val = self.request.GET.get(self.search_key, '')

        condition = Q()
        condition.connector = 'or'

        if self.get_search_fields() and self.show_search_field_form():

            for search_field in self.get_search_fields():
                condition.children.append((search_field, query_val))
        print(condition)
        return condition

    # 批量处理(actions)
    show_actions = False

    def get_show_actions(self):
        return self.show_actions

    actions = []

    def get_actions(self):
        result = []
        if self.actions:
            result.extend(self.actions)
        return result

    @property
    def urls(self):
        return self.get_urls()

    def get_urls(self):
        info = self.model._meta.app_label, self.model._meta.model_name
        urlpatterns = [
            path('', self.wrapper(self.changelist_view), name='%s_%s_changelist' % info),
            path('add/', self.wrapper(self.add_view), name='%s_%s_add' % info),
            path('<int:obj_id>/change/', self.wrapper(self.change_view), name='%s_%s_change' % info),
            path('<int:obj_id>/delete/', self.wrapper(self.delete_view), name='%s_%s_delete' % info),
        ]
        urlpatterns.extend(self.extra_url())
        return urlpatterns

    def extra_url(self):
        """
        处理增删改查以外的url,即自定义url
        :return:
        """
        return []

    def changelist_view(self, request, *args, **kwargs):
        """
        处理表头及展示数据
        :param request:
        :return:
        """
        if request.method == 'POST' and self.get_show_actions():  # post请求并且批量表单显示
            func_string = request.POST.get('action_list', '')
            if func_string:
                func = getattr(self, func_string)

                ret = func(request)
                # 传入request为了在该函数中处理数据
                if ret:
                    return ret

        data_list = self.model.objects.filter(self.get_search_condition()).order_by(*self.get_order_by())
        # self指代当前对象
        cl = ClassList(self, data_list)

        return render(request, 'change_list.html',
                      {'data_list': cl.body_list,
                       'header_list': cl.header_list,
                       'add_btn': self.get_add_btn,
                       'pager_html': cl.pager_html,
                       'cl': cl
                       }
                      )

    def add_view(self, request, *args, **kwargs):
        """
        添加视图处理
        :param request:
        :return:
        """

        if request.method == 'GET':
            """
            form不能写死，用户可以自定制字段
            故使用self.get_model_form
            """
            # 获取自定制ModelForm
            form = self.get_model_form()
            return render(request, 'add_view.html', {'form': form})
        elif request.method == 'POST':
            """
            form不能写死，用户可以自定制字段
            故使用self.get_model_form
            """
            # 获取自定制ModelForm
            form = self.get_model_form()(request.POST)
            if form.is_valid():
                form.save()
                return redirect(self.get_show_url())
            return render(request, 'add_view.html', {'form': form})

        return HttpResponse('添加')

    def change_view(self, request, obj_id, *args, **kwargs):
        """
        编辑视图
        :param request:
        :param obj_id:
        :param args:
        :param kwargs:
        :return:
        """

        obj = self.model.objects.filter(pk=obj_id).first()
        if request.method == 'GET':
            """
            form不能写死，用户可以自定制字段
            故使用self.get_model_form
            """
            form = self.get_model_form()(instance=obj)
            return render(request, 'change_view.html', {'form': form})
        elif request.method == 'POST':
            """
            form不能写死，用户可以自定制字段
            故使用self.get_model_form
            """
            form = self.get_model_form()(instance=obj, data=request.POST)
            if form.is_valid():
                form.save()

                # 可以携带条件跳回原页面
                query_param_str = request.GET.get(self._query_param_key)
                now_url = '%s?%s' % (self.get_show_url(), query_param_str)

                return redirect(now_url)
            return render(request, 'change_view.html', {'form': form})

    def delete_view(self, request, obj_id, *args, **kwargs):
        """
        删除视图，处理
        :param request:
        :param obj_id:
        :return:
        """
        self.model.objects.filter(pk=obj_id).delete()
        return redirect(self.get_show_url())

    # 自定义checkbox,edit，delete
    def checkbox(self, obj=None, is_header=False):
        """
        页面checkbox选项
        :param obj:
        :param is_header:
        :return:
        """
        if is_header:
            return '选择'
        return mark_safe('<input type="checkbox" value=%s name="pk">' % obj.id)

    def edit(self, obj=None, is_header=False):
        """
        页面编辑选项
        :param obj:
        :param is_header:
        :return:
        """
        if is_header:
            return '操作0'
        curr_url = self.request.GET.urlencode()
        params = QueryDict(mutable=True)
        params[self._query_param_key] = curr_url
        return mark_safe('<a href=%s?%s>编辑</a>' % (self.get_change_url(obj.id), params.urlencode()))

    def delete(self, obj=None, is_header=False):
        """
        页面删除选项
        :param obj:
        :param is_header:
        :return:
        """
        if is_header:
            return '操作1'
        return mark_safe('<a href={0}>删除</a>'.format(self.get_delete_url(obj.id)))

    def get_add_url(self):
        """
        反向生成添加url
        :return:
        """
        info = self.model._meta.app_label, self.model._meta.model_name
        url = reverse('%s_%s_add' % info)
        return url

    def get_show_url(self):
        """
        反向生成列表url
        :return:
        """
        info = self.model._meta.app_label, self.model._meta.model_name
        url = reverse('%s_%s_changelist' % info)
        return url

    def get_change_url(self, oid):
        """
        反向生成编辑url
        :return:
        """
        info = self.model._meta.app_label, self.model._meta.model_name
        # 反向生成url需要参数时用args
        url = reverse('%s_%s_change' % info, args=(oid,))

        return url

    def get_delete_url(self, oid):
        """
        反向生成删除url
        :return:
        """
        info = self.model._meta.app_label, self.model._meta.model_name
        # 反向生成url需要参数时用args
        url = reverse('%s_%s_delete' % info, args=(oid,))
        return url

    def edit_tag_link(self, pk, text):
        """
        生成编辑标签
        :return:
        """
        curr_url = self.request.GET.urlencode()
        params = QueryDict(mutable=True)
        params[self._query_param_key] = curr_url

        return mark_safe('<a href={0}?{1}>{2}</a>'.format(self.get_change_url(pk), params.urlencode(), text))


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
