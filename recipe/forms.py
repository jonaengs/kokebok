from django import forms

from recipe.models import Recipe, RecipeIngredient


class RecipeIngredientForm(forms.ModelForm):

    class Meta:
        model = RecipeIngredient


class RecipeForm(forms.ModelForm):

    class Meta:
        model = Recipe
