from django import forms

from recipes.models import Recipe, RecipeIngredient


class RecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = '__all__'


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ('name', 'content', 'default_servings', 'public')


class SearchForm(forms.Form):
    search = forms.CharField()
    exclusive = forms.BooleanField()
    sort_by = forms.ChoiceField()