from django.apps import apps
from django.contrib import admin
from typing import Type

# Register all models from the shop app
app_config = apps.get_app_config('shop')
for model in app_config.get_models():
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
        
