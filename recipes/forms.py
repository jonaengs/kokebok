from django import forms

from recipes.models import Recipe, RecipeIngredient


class RecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = '__all__'


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = '__all__'


class SearchForm(forms.Form):
    search = forms.CharField()
    exclusive = forms.BooleanField()
    sort_by = forms.ChoiceField()