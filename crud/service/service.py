from django.urls import path


class CrudConfig:
    def __init__(self, model, crud_site):
        self.model = model
        self.crud_site = crud_site


class CrudSite:
    def __init__(self):
        self._registry = {}

    def regiser(self, model, crud_config=None):
        if not crud_config:
            crud_config = CrudConfig
        self._registry[model] = crud_config(model, self)

    @property
    def urls(self):
        return self.get_urls(), None, 'crud'

    def get_urls(self):
        urlpatterns = []
        for model,crud_config_obj in self._registry.items():
            urlpatterns += [
                path('')
            ]

        return urlpatterns




site = CrudSite()
