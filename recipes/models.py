import uuid

from ckeditor.fields import RichTextField
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import SET_NULL, CASCADE
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from lib.rw_ingredients import slugify_norwegian


class Recipe(models.Model):
    name = models.CharField(max_length=128)
    content = RichTextField(blank=True)
    origin_url = models.URLField(max_length=300, blank=True, null=True)
    serves = models.PositiveIntegerField(blank=True, null=True)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(blank=True)

    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('recipe_detail', kwargs={'uuid': self.id, 'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_norwegian(self.name)
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ('name',)


class Ingredient(MPTTModel):
    name = models.CharField(max_length=64, unique=True)
    ubiquitous = models.BooleanField(default=False)
    # Add substitutes later? substitutes = models.ManyToManyField(to="self", related_name="substitutes", blank=True)
    parent = TreeForeignKey(
        'self',
        blank=True,
        null=True,
        related_name='children',
        on_delete=SET_NULL
    )

    def object_already_in_family(self, field, object_id):
        family = self.get_ancestors() | self.get_children()
        filter_dict = {'id': object_id}
        for ingredient in family:
            if ingredient.__getattribute__(field).filter(**filter_dict).exists():
                return True
        return False

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class RecipeIngredient(models.Model):
    """
    Usage of ingredients in recipes. Allows for different names, measurements etc. of the same ingredient
    in recipes.
    """

    class Measurements(models.TextChoices):
        GRAMS = 'g', _('grams')
        KILOGRAMS = 'kg', _('kilograms')
        DECILITERS = 'dl', _('deciliters')
        CENTILITERS = 'cl', _('centiliters')
        MILLILITERS = 'ml', _('milliliters')
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
        on_delete=CASCADE,
        related_name='recipe_ingredients',
        blank=True,
        null=True,
    )
    base_ingredient = models.ForeignKey(
        to='recipes.Ingredient',
        on_delete=CASCADE,
        related_name='recipe_usages',
        blank=True,
        null=True,
    )
    amount_per_serving = models.FloatField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0.0)]
    )
    measurement = models.CharField(
        max_length=16,
        choices=Measurements.choices,
        default=Measurements.COUNT,
        blank=True,
    )

    class Meta:
        ordering = ('recipe__name', )

    def __str__(self):
        return f"{self.name} [{self.recipe.name}]"

    def clean(self):
        if not self.recipe:
            raise ValidationError("Recipe must be given")
        if not self.name and not self.base_ingredient:
            raise ValidationError("Recipe ingredient must be given either a name or a base_ingredient")
        return super().clean()

    def save(self, **kwargs):
        self.full_clean()
        if not self.pk:  # = if being created, not updated
            if not self.name and self.base_ingredient:
                self.name = self.base_ingredient.name
        super().save(**kwargs)
