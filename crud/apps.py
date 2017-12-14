from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules


class CrudConfig(AppConfig):
    name = 'crud'

    def ready(self):
        autodiscover_modules('crud', )
