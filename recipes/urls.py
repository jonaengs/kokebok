from django.urls import path

from recipes.views import RecipeListAPI

urlpatterns = [
    path('api/', RecipeListAPI.as_view(), name='recipe_list_api'),
]