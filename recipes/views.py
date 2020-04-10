from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import CreateView, ListView, DetailView
from rest_framework import generics

from scrape.utils import conversions, create_recipe_from_scrape
from recipes.models import Recipe, Ingredient, RecipeIngredient
from scrape.scrape import scrape
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


def scrape_view(request):
    url = request.GET.get('url')
    if url:
        site_content = scrape(url)
        recipe = create_recipe_from_scrape(site_content)
        return HttpResponseRedirect('/admin/recipes/recipe/' + str(recipe.id) + '/change')
    return HttpResponse('In the address bar: add ?url=<insert_your_url_here> add the end of the current url,'
                        'without the angled brackets')


def search(request):
    query = request.GET
    ctx = {'ingredients': Ingredient.objects.all()}
    if query:
        exclusive = query.get('exclusive') == "True"  # exclusive = False => inclusive
        # sort_by = query.get('sort_by', 'alphabetical')  # should support: "recent", "popular", "alpha desc".
        ingredients = query.get('ingredients', '').split(",")
        if ingredients:
            recipes = Recipe.objects.prefetch_related('recipe_ingredients__base_ingredient').\
                filter(recipe_ingredients__base_ingredient__name__in=ingredients).distinct()
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
