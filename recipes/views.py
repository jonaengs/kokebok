from django.views.generic import ListView, CreateView

from recipes.models import Recipe, Ingredient


class RecipeListView(ListView):
    model = Recipe


class IngredientCreateView(CreateView):
    model = Ingredient


class RecipeCreateView(CreateView):
    model = Recipe
