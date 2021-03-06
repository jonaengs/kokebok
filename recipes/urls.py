from django.urls import path

from recipes.views import RecipeListView, search, RecipeDetailView, scrape_view

urlpatterns = [
    path('', search, name='search'),
    path('scrape/', scrape_view, name='scrape'),
    path('recipes/', RecipeListView.as_view(), name='recipe_list'),
    path('<uuid:uuid>/<slug:slug>/', RecipeDetailView.as_view(), name='recipe_detail'),
]