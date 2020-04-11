from django.contrib import admin
from nested_admin.nested import NestedTabularInline, NestedModelAdmin

from recipes.models import Ingredient, Recipe, RecipeCategoryConnection, IngredientCategoryConnection, \
    RecipeIngredient, IngredientCategory, RecipeCategory, Variation, SubRecipe


class RecipeCategoryInline(NestedTabularInline):
    model = RecipeCategoryConnection
    max_num = 1


class IngredientCategoryInline(admin.TabularInline):
    model = IngredientCategoryConnection
    max_num = 1


class RecipeIngredientInline(NestedTabularInline):
    model = RecipeIngredient
    extra = 1
    exclude = ('sub_recipe',)


class SubRecipeInline(NestedTabularInline):
    inlines = [
        RecipeIngredientInline,
    ]
    model = SubRecipe
    extra = 0


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
