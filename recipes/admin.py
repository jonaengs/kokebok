from django.contrib import admin

from recipes.models import Ingredient, Recipe, RecipeCategoryConnection, IngredientCategoryConnection, \
    RecipeIngredient, IngredientCategory, RecipeCategory, Variation


class RecipeCategoryInline(admin.TabularInline):
    model = RecipeCategoryConnection
    max_num = 1


class IngredientCategoryInline(admin.TabularInline):
    model = IngredientCategoryConnection
    max_num = 1


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class IngredientAdmin(admin.ModelAdmin):
    inlines = [
        IngredientCategoryInline,
    ]


class RecipeAdmin(admin.ModelAdmin):
    inlines = [
        RecipeCategoryInline,
        RecipeIngredientInline,
    ]


class VariationAdmin(RecipeAdmin):
    pass


admin.site.register(Variation, VariationAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register((IngredientCategory, RecipeCategory))
