from django.contrib import admin
from django.urls import resolve

from recipes.models import Ingredient, Recipe, RecipeIngredient


def get_parent_id_from_request(request):
    resolved = resolve(request.path_info)
    return resolved.kwargs.get('object_id')


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    inlines = [
        RecipeIngredientInline,
    ]

    # hidden on creation, read only when editing
    special_fields = ('datetime_created', 'datetime_updated')

    def get_form(self, request, obj=None, change=False, **kwargs):
        if not obj:
            self.exclude = self.special_fields + ('slug',)
        else:
            self.readonly_fields = self.special_fields
        return super(RecipeAdmin, self).get_form(request, obj, change, **kwargs)


admin.site.register(Ingredient)
admin.site.register(Recipe, RecipeAdmin)
