from django.contrib import admin

from recipes.models import Ingredient, Recipe, RecipeCategoryConnection, IngredientCategoryConnection, \
    RecipeIngredient, IngredientCategory, RecipeCategory


class RecipeCategoryInline(admin.TabularInline):
    model = RecipeCategoryConnection
    max_num = 1

    def get_readonly_fields(self, request, obj=None):
        fields = super(RecipeCategoryInline, self).get_readonly_fields(request, obj)
        if obj is not None:
            pass
            # print(fields)
            # print(Ingredient.objects.filter(category_connections__category__in=obj.categories.all()))
        return fields


class IngredientCategoryInline(admin.TabularInline):
    model = IngredientCategoryConnection
    max_num = 1

    def get_readonly_fields(self, request, obj=None):
        fields = super(IngredientCategoryInline, self).get_readonly_fields(request, obj)
        if obj is not None:
            print(obj)
            # print(fields)
            # print(Ingredient.objects.filter(category_connections__category__in=obj.categories.all()))
        return fields


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


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register((IngredientCategory, RecipeCategory))
