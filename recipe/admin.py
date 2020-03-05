from django.contrib import admin
import importlib
import inspect

from django.core.exceptions import ImproperlyConfigured

for _, cls in inspect.getmembers(importlib.import_module('recipe.models'), inspect.isclass):
    try:
        admin.site.register(cls)
    except (ImproperlyConfigured, TypeError):
        pass
