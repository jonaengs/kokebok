from django.contrib import admin

from recipe.models import Ingredient, Recipe, RecipeIngredient, RecipeCategory, IngredientCategory, \
    RecipeCategoryConnection, IngredientCategoryConnection

for cls in (Ingredient, Recipe, RecipeIngredient, RecipeCategory, IngredientCategory, RecipeCategoryConnection, \
            IngredientCategoryConnection):
    admin.site.register(cls)
