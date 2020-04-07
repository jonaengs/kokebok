from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import CreateView, ListView, DetailView
from rest_framework import generics

from recipes.forms import RecipeForm
from recipes.measurement_converter import conversions
from recipes.models import Recipe, Ingredient, RecipeIngredient
from recipes.scrape_matprat import scrape_matprat
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

"""
intended to speed up things, but actually seems to make them go slower?
    def get_queryset(self):
        return self.model.objects.prefetch_related('ingredient_objects', 'recipe_ingredients')
"""


class RecipeDetailView(DetailView):
    model = Recipe


def scrape_view(request):
    if (url := request.GET.get('url')):
        scrape = scrape_matprat(url)
        recipe = Recipe.objects.create(
            name=scrape['name'],
            content = scrape['content'],
            default_servings=int(scrape['default_servings']),
            public=True
        )
        for a, m, i in scrape["ami"]:
            if not Ingredient.objects.filter(name=i).exists():
                ingr = Ingredient.objects.create(name=i)
            else:
                ingr = Ingredient.objects.get(name=i)
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingr,
                amount_per_serving=int(a),
                measurement=conversions[m]
            )
        return HttpResponse(f'recipe: {recipe} added successfully')
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
