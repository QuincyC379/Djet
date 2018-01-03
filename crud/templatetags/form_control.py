from django.forms.models import ModelChoiceField
from django.template import Library
from django.urls import reverse

from crud.service.service import site

register = Library()


@register.inclusion_tag('myform.html')
def my_form(config, form):
    # 遍历当前对象获取需要的值

    new_form = []
    for form_part in form:
        temp = {'is_popup': False, 'item': form_part}
        """
        <django.forms.fields.CharField object at 0x000000425CDA1080>
        <django.forms.fields.CharField object at 0x000000425CDA10F0>
        <django.forms.fields.TypedChoiceField object at 0x000000425CDA1160>
        <django.forms.models.ModelMultipleChoiceField object at 0x000000425CDA11D0>
        <django.forms.models.ModelChoiceField object at 0x000000425CDA1240>
        """
        if isinstance(form_part.field, ModelChoiceField):
            """
            判断是否为多对多或者一对多"""
            related_model_name = form_part.field.queryset.model
            if related_model_name in site._registry:

                related_name = config.model._meta.get_field(form_part.name).remote_field.related_name

                info = related_model_name._meta.app_label, related_model_name._meta.model_name
                base_url = reverse('%s_%s_add' % info)
                popup_url = '%s?_popup=%s&model_name=%s&related_name=%s' % (
                    base_url, form_part.auto_id, info[1], related_name)
                temp['is_popup'] = True
                temp['popup_url'] = popup_url
        new_form.append(temp)
    return {'form': new_form}
