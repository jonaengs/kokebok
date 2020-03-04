from django.shortcuts import render
from django.views.generic import ListView

from recipe.models import Recipe


class RecipeList(ListView):
    model = Recipe
