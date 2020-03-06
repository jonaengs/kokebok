from django import forms

from recipes.models import Recipe, RecipeIngredient


class RecipeIngredientForm(forms.ModelForm):

    class Meta:
        model = RecipeIngredient


class RecipeForm(forms.ModelForm):

    class Meta:
        model = Recipe
