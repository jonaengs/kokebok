from django.views.generic import ListView, CreateView
from rest_framework import generics

from recipes.models import Recipe, Ingredient
from recipes.serializers import RecipeSerializer


class RecipeListAPI(generics.ListCreateAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class IngredientCreateView(CreateView):
    model = Ingredient


class RecipeCreateView(CreateView):
    model = Recipe
