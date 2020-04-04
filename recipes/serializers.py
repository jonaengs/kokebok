from rest_framework import serializers
from .models import Recipe, Ingredient, RecipeIngredient


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('name', 'date_created', 'author', 'id', 'default_servings', )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('name', 'id', 'ubiquitous', )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeIngredient
        fields = ('id', 'measurement', 'amount_per_serving', )
