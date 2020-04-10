import uuid

from ckeditor.fields import RichTextField
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel


class Recipe(models.Model):
    name = models.CharField(max_length=128)
    content = RichTextField(blank=True)
    serves = models.PositiveIntegerField(blank=True, null=True)

    # id
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(blank=True)

    # timestamps
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_updated = models.DateTimeField(auto_now=True)

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

    def get_absolute_url(self):
        return reverse('recipe_detail', kwargs={'uuid': self.id, 'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super(Recipe, self).save(*args, **kwargs)




# variation on a recipes. Allow users to "subclass" other recipes
class Variation(Recipe):  # variations are also recipes. This allows for variations on variations etc.
    original = models.ForeignKey(
        to='recipes.Recipe',
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name='variations',
    )


class Ingredient(models.Model):
    name = models.CharField(max_length=64, unique=True)  # unique??
    ubiquitous = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    class Measurements(models.TextChoices):
        GRAMS = 'g', _('grams')
        KILOGRAMS = 'kg', _('kilograms')
        DECILITERS = 'dl', _('deciliters')
        LITERS = 'L', _('liters')
        TABLESPOONS = 'tbsp', _('tablespoons')
        TEASPOONS = 'tsp', _('teaspoons')
        COUNT = '', _('count')
        SLICES = 'slices', _('slices')
        __empty__ = _('Unknown')

    name = models.CharField(
        blank=True,
        max_length=128,
    )
    recipe = models.ForeignKey(
        to='recipes.Recipe',
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    base_ingredient = models.ForeignKey(
        to='recipes.Ingredient',
        on_delete=models.CASCADE,
        related_name='recipe_usages',
        blank=True,
        null=True,
    )
    amount_per_serving = models.FloatField(
        blank=True,
        null=True,
    )
    measurement = models.CharField(
        max_length=16,
        choices=Measurements.choices,
        default=Measurements.COUNT,
        blank=True,
    )

    def __str__(self):
        return self.recipe.name + ": " + self.name

    def clean(self):
        if not self.name and not self.base_ingredient:
            raise ValidationError("Recipe ingredient must be given either a name or a base_ingredient")
        if self.amount_per_serving and self.amount_per_serving < 0:
            raise ValidationError("Amount per serving must be positive")
        return super(RecipeIngredient, self).clean()

    def save(self, **kwargs):
        if not self.pk and not self.name and self.base_ingredient:
            self.name = self.base_ingredient.name
        super(RecipeIngredient, self).save(**kwargs)


# TODO: Consider moving everything category-related into its own app
# TODO: The whole implementation is pretty ugly. Consider refactoring. Maybe just add a "type" field to category.
#  with choices "base_ingredient" or "recipes" as choices. And actually, maybe reconsider if things need to split at all.
#  Some ingredients may require recipes themselves.
class Category(MPTTModel):
    name = models.CharField(max_length=40, unique=True)
    parent = TreeForeignKey('self', blank=True, null=True, related_name='children', on_delete=models.SET_NULL)

    def object_already_in_family(self, field, object_id):
        family = self.get_ancestors() | self.get_children()
        filter_dict = {'id': object_id}
        for category in family:
            if category.__getattribute__(field).filter(**filter_dict).exists():
                return True
        return False

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class IngredientCategory(Category):
    ingredients = models.ManyToManyField(
        to='recipes.Ingredient',
        related_name='categories',
        through='recipes.IngredientCategoryConnection',
    )

    class Meta:
        verbose_name_plural = "Ingredient categories"


class RecipeCategory(Category):
    recipes = models.ManyToManyField(
        to='recipes.Recipe',
        related_name='categories',
        through='recipes.RecipeCategoryConnection'
    )

    class Meta:
        verbose_name_plural = "Recipe categories"


class BaseCategoryConnection(models.Model):
    @property
    def category(self):
        raise NotImplementedError()

    @property
    def attr(self):
        raise NotImplementedError("implementing classes must specify which attr to prevent overlap with")

    @property
    def attr_name(self):  # name of Recipe/IngredientCategory m2m field
        raise NotImplementedError()

    def clean(self, *args, **kwargs):
        if self.category.object_already_in_family(self.attr_name, self.attr.id):
            raise ValidationError("base_ingredient already in category family (c)")

    def save(self, *args, **kwargs):
        if self.category.object_already_in_family(self.attr_name, self.attr.id):
            raise ValidationError("base_ingredient already in category family (s)")
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class IngredientCategoryConnection(BaseCategoryConnection):
    ingredient = models.ForeignKey(to='recipes.Ingredient', on_delete=models.CASCADE,
                                   related_name='category_connections')
    category = models.ForeignKey(to='recipes.IngredientCategory', on_delete=models.CASCADE, related_name='connections')

    @property
    def attr(self):
        return self.ingredient

    @property
    def attr_name(self):
        return "ingredients"


class RecipeCategoryConnection(BaseCategoryConnection):
    recipe = models.ForeignKey(to='recipes.Recipe', on_delete=models.CASCADE, related_name='category_connections')
    category = models.ForeignKey(to='recipes.RecipeCategory', on_delete=models.CASCADE, related_name='connections')

    @property
    def attr(self):
        return self.recipe

    @property
    def attr_name(self):
        return "recipes"
