from django.contrib import admin
from django.urls import resolve
from nested_admin.nested import NestedTabularInline, NestedModelAdmin

from recipes.models import Ingredient, Recipe, RecipeCategoryConnection, IngredientCategoryConnection, \
    RecipeIngredient, IngredientCategory, RecipeCategory, Variation, SubRecipe


def get_parent_id_from_request(request):
    resolved = resolve(request.path_info)
    return resolved.kwargs.get('object_id')


class RecipeCategoryInline(NestedTabularInline):
    model = RecipeCategoryConnection
    max_num = 1


class IngredientCategoryInline(admin.TabularInline):
    model = IngredientCategoryConnection
    max_num = 1


class RecipeIngredientInline(NestedTabularInline):
    model = RecipeIngredient
    extra = 1

    def get_exclude(self, request, obj=None):
        if self.parent_model == SubRecipe:
            return ('recipe',)
        elif self.parent_model == Recipe:
            return ('sub_recipe',)


class SubRecipeInline(NestedTabularInline):
    inlines = [
        RecipeIngredientInline,
    ]
    model = SubRecipe
    extra = 0

    def get_queryset(self, request):
        recipe = Recipe.objects.get(pk=get_parent_id_from_request(request))
        # return recipe.sub_recipes.all().prefetch_related('recipe_ingredients', )
        return super(SubRecipeInline, self).get_queryset(request)


class IngredientAdmin(admin.ModelAdmin):
    inlines = [
        IngredientCategoryInline,
    ]


class RecipeAdmin(NestedModelAdmin):
    inlines = [
        RecipeCategoryInline,
        RecipeIngredientInline,
        SubRecipeInline,
    ]

    # hidden on creation, read only when editing
    special_fields = ('author', 'datetime_created', 'datetime_updated')

    def get_form(self, request, obj=None, change=False, **kwargs):
        if not obj:
            self.exclude = self.special_fields + ('slug',)
        else:
            self.readonly_fields = self.special_fields
        return super(RecipeAdmin, self).get_form(request, obj, change, **kwargs)


class VariationAdmin(admin.ModelAdmin):
    fields = ('original',)


admin.site.register(Variation, VariationAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register((IngredientCategory, RecipeCategory))
