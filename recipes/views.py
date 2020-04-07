from django.shortcuts import render
from django.views.generic import CreateView, ListView, DetailView
from rest_framework import generics

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


class RecipeDetailView(DetailView):
    model = Recipe


def search(request):
    query = request.GET
    ctx = {'ingredients': Ingredient.objects.all()}
    if query:
        exclusive = query.get('exclusive') == "True"  # exclusive = False => inclusive
        sort_by = query.get('sort_by', 'alphabetical')  # should support: "recent", "popular", "alpha desc".
        ingredients = query.get('ingredients', '').split(",")
        if ingredients:
            print(Recipe.objects.prefetch_related('ingredient_objects').filter(ingredient_objects__name__in=ingredients))
            print(ingredients)
            recipes = Recipe.objects.prefetch_related('ingredient_objects').filter(ingredient_objects__name__in=ingredients).distinct()
            if exclusive:
                include_ubiquitous = query.get('include-ubiquitous') == "on"
                if include_ubiquitous:  # Will include every single recipe using a ubiq. ingr. if done for inclusive
                    ingredients += Ingredient.objects.filter(ubiquitous=True).values_list('name', flat=True)
                for recipe in list(recipes):
                    if any(ingredient not in ingredients for ingredient in
                           recipe.ingredient_objects.all().values_list('name', flat=True)):
                        recipes = recipes.exclude(id=recipe.id)
            ctx.update({'recipes': recipes})
    return render(request, 'home.html', ctx)
