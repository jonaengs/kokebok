from django.shortcuts import render
from django.views.generic import CreateView, ListView
from rest_framework import generics

from recipes.forms import SearchForm
from recipes.models import Recipe, Ingredient
from recipes.serializers import RecipeSerializer


class RecipeListAPI(generics.ListAPIView):
    queryset = Recipe.objects
    serializer_class = RecipeSerializer


class IngredientCreateView(CreateView):
    model = Ingredient


class RecipeCreateView(CreateView):
    model = Recipe


class RecipeListView(ListView):
    model = Recipe

    # def get_context_data(self, *args, object_list=None, **kwargs):
        # return super(RecipeListView, self).get_context_data(*args, object_list=object_list, form=SearchForm(), **kwargs)


def search(request):
    query = request.GET
    if query:
        exclusive = bool(query.get('exclusive', False))  # exclusive = False => inclusive
        sort_by = query.get('sort_by', 'alphabetical')  # should support: "recent", "popular", "alpha desc".
        ingredients = query.get('ingredients', '').split(",")  # comma-separated
        if ingredients:
            return "good!"
        return ":("
    return render(request, 'home.html')

