from collections import Counter

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import CreateView, ListView, DetailView, UpdateView

from scrape.utils import create_recipe_from_scrape
from recipes.models import Recipe, Ingredient, RecipeIngredient
from scrape.scrape import scrape, get_sites


class IngredientCreateView(CreateView):
    model = Ingredient


class RecipeCreateView(CreateView):
    model = Recipe


class RecipeListView(ListView):
    model = Recipe

    def get_queryset(self):
        return Recipe.objects.prefetch_related('recipe_ingredients__base_ingredient')


class RecipeDetailView(DetailView):
    model = Recipe


def scrape_view(request):
    url = request.GET.get('url_input')
    if url:
        site_content = scrape(url)
        recipe = create_recipe_from_scrape(site_content)
        return HttpResponseRedirect('/admin/recipes/recipe/' + str(recipe.id) + '/change')
    return render(request, template_name='scrape.html', context={'supported_sites': get_sites().keys()})


def search(request):
    # TODO: account for subrecipes
    query = request.GET
    ctx = {'ingredients': Ingredient.objects.all()}
    if query:
        exclusive = not query.get('exclusive') == "inclusive"  # defaults to exclusive
        sort_by = query.get('sort_by')  # should support: "recent", "alphabetical", "most matches". Support ASC, DESC?
        ingredients = query.get('ingredients', '').split(",")
        if ingredients:
            relevant_recipes = Recipe.objects.prefetch_related('recipe_ingredients__base_ingredient'). \
                filter(recipe_ingredients__base_ingredient__name__in=ingredients)
            if exclusive:
                recipes = relevant_recipes.distinct()
                include_ubiquitous = query.get('include-ubiquitous') == "on"
                if include_ubiquitous:
                    ingredients += Ingredient.objects.filter(ubiquitous=True).values_list('name', flat=True)
                for recipe in list(recipes):
                    if not all(ingredient in ingredients for ingredient in
                               recipe.recipe_ingredients.all().values_list('base_ingredient').values_list('name',
                                                                                                          flat=True)):
                        recipes = recipes.exclude(id=recipe.id)
            if sort_by:
                # default sorting is alphabetical, as specified in model.
                if not exclusive and sort_by == 'best_match':  # sorting by best match is meaningless for exclusive
                    recipes_counter = Counter(relevant_recipes)
                    recipes = sorted(recipes_counter, key=recipes_counter.get, reverse=True)
                elif sort_by == 'recent':
                    recipes = sorted(recipes, key=lambda recipe: recipe.datetime_created, reverse=True)

            ctx.update({'recipes': recipes})
    return render(request, 'home.html', ctx)


def recipe_update_view(request, uuid, slug):
    recipe = Recipe.objects.get(id=uuid)
    return HttpResponseRedirect(reverse('recipe_detail', kwargs={'uuid': uuid, 'slug': slug}))

