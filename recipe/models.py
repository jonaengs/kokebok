from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel


class Recipe(models.Model):
    date_created = models.DateTimeField(default=timezone.now)
    name = models.CharField(max_length=128)
    default_servings = models.IntegerField(blank=True)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=40)
    ubiquitous = models.BooleanField(default=False)
    recipes = models.ManyToManyField(
        to='recipe.Recipe',
        through='recipe.RecipeIngredient',
        related_name='ingredients'
    )

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

    recipe = models.ForeignKey(to='recipe.Recipe', on_delete=models.CASCADE)
    ingredient = models.ForeignKey(to='recipe.Ingredient', on_delete=models.CASCADE)
    amount_per_serving = models.IntegerField(blank=True)
    measurement = models.CharField(
        max_length=5,
        choices=Measurements.choices,
        default=Measurements.COUNT,
        blank=True
    )


class Category(MPTTModel):
    name = models.CharField(max_length=40)
    parent = TreeForeignKey('self', blank=True, null=True, related_name='children', on_delete=models.SET_NULL)

    def thing_not_in_branch(self, field, thing_id):
        filter_dict = {'id=': thing_id}
        for category in self.get_family():
            if category.__getattribute__(field).filter(filter_dict).exists():
                return False
        return True

    class Meta:
        abstract = True


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
    )


class IngredientCategoryConnection(models.Model):
    ingredient = models.ForeignKey(to=Ingredient, on_delete=models.CASCADE)
    category = models.ForeignKey(to=IngredientCategory, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        assert self.category.thing_not_in_branch("ingredients", self.ingredient.id), \
            "ingredient already in category family"
        super(self, IngredientCategoryConnection).save(*args, **kwargs)


class RecipeCategoryConnection(models.Model):
    recipe = models.ForeignKey(to=Ingredient, on_delete=models.CASCADE)
    category = models.ForeignKey(to=IngredientCategory, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        assert self.category.thing_not_in_branch("ingredients", self.recipe.id), \
            "ingredient already in category family"
        super(self, RecipeCategoryConnection).save(*args, **kwargs)




