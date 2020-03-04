from django.views.generic import ListView, CreateView

from recipe.models import Recipe, Ingredient


class RecipeList(ListView):
    model = Recipe


class CreateIngredientView(CreateView):
    model = Ingredient


class CreateRecipeView(CreateView):
    model = Recipe
