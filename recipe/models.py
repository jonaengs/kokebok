from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel


class Recipe(models.Model):
    date_created = models.DateTimeField(default=timezone.now)
    name = models.CharField(max_length=128)
    default_servings = models.PositiveIntegerField(blank=True, null=True)
    ingredient_objects = models.ManyToManyField(
        to='recipe.Ingredient',
        through='recipe.RecipeIngredient',
        related_name='recipes',
    )

    # community interactions
    author = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='original_recipes',
    )
    public = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def update_recipe_ingredient(self, ingredient_id, attr, value):
        recipe_ingredient = self.recipe_ingredients.get(ingredient_id__exact=ingredient_id)
        recipe_ingredient.__setattr__(attr, value)
        recipe_ingredient.save()


# variation on a recipe. Allow users to "subclass" other recipes
class Variation(Recipe):  # variations are also recipes. This allows for variations on variations etc.
    original = models.ForeignKey(
        to='recipe.Recipe',
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name='variations',
    )

    # TODO: it may be inefficient to copy every ingredient connection for every variation.
    #  Consider saving differences between original and variation instead. (<- may require tree-structured models)
    def save(self, *args, **kwargs):
        if not self.pk:  # on creation, copy over ingredient connections from original recipe
            super().save(*args, **kwargs)
            for ingredient in self.original.recipe_ingredients.all():
                ingredient.recipe = self
                ingredient.pk = None  # must also set id = None if RecipeIngredient every subclasses another model
                ingredient.save()
        else:
            super().save(*args, **kwargs)


# TODO: Figure out where to put Favorites. A separate app for user interactions, or maybe in the users app?
class Favorite(models.Model):
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites',
    )
    recipe = models.ForeignKey(
        to='recipe.Recipe',
        on_delete=models.CASCADE,
        related_name='favorites'
    )


class Ingredient(models.Model):
    name = models.CharField(max_length=64, unique=True)  # unique??
    ubiquitous = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    class Measurements(models.TextChoices):
        GRAMS = 'g', _('grams')
        LITERS = 'L', _('liters')
        TABLESPOONS = 'Tb.', _('tablespoons')
        TEASPOONS = 'tsp', _('teaspoons')
        COUNT = '', _('')
        __empty__ = _('Unknown')

    recipe = models.ForeignKey(
        to='recipe.Recipe',
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        to='recipe.Ingredient',
        on_delete=models.CASCADE,
        related_name='recipe_usages'
    )
    amount_per_serving = models.PositiveIntegerField(
        blank=True,
        null=True,
    )
    measurement = models.CharField(
        max_length=5,
        choices=Measurements.choices,
        default=Measurements.COUNT,
        blank=True
    )

    def __str__(self):
        return self.recipe.name + ": " + self.ingredient.name


# TODO: Consider moving everything category-related into its own app
class Category(MPTTModel):
    name = models.CharField(max_length=40)
    parent = TreeForeignKey('self', blank=True, null=True, related_name='children', on_delete=models.SET_NULL)

    def thing_in_branch(self, field, thing_id):
        filter_dict = {'id': thing_id}
        for category in self.get_family():
            if category.__getattribute__(field).filter(**filter_dict).exists():
                return True
        return False

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class IngredientCategory(Category):
    ingredients = models.ManyToManyField(
        to='recipe.Ingredient',
        through='recipe.IngredientCategoryConnection',
        related_name='categories',
    )


class RecipeCategory(Category):
    recipes = models.ManyToManyField(
        to='recipe.Recipe',
        related_name='categories',
        through='recipe.RecipeCategoryConnection'
    )


class IngredientCategoryConnection(models.Model):
    ingredient = models.ForeignKey(to='recipe.Ingredient', on_delete=models.CASCADE)
    category = models.ForeignKey(to='recipe.IngredientCategory', on_delete=models.CASCADE)

    def clean(self, *args, **kwargs):
        if not self.category.thing_in_branch("ingredient_objects", self.ingredient.id):
            raise ValidationError("ingredient already in category family")

    def save(self, *args, **kwargs):
        if self.category.thing_in_branch("ingredient_objects", self.ingredient.id):
            raise ValidationError("ingredient already in category family")
        super().save(*args, **kwargs)


class RecipeCategoryConnection(models.Model):
    recipe = models.ForeignKey(to='recipe.Recipe', on_delete=models.CASCADE)
    category = models.ForeignKey(to='recipe.RecipeCategory', on_delete=models.CASCADE)

    def clean(self, *args, **kwargs):
        if not self.category.thing_in_branch("recipes", self.recipe.id):
            raise ValidationError("recipe already in category family")

    def save(self, *args, **kwargs):
        if self.category.thing_in_branch("recipes", self.recipe.id):
            raise ValidationError("recipe already in category family")
        super().save(*args, **kwargs)
