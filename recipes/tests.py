from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from recipes.models import Recipe, Ingredient, RecipeIngredient


class RecipeTest(TestCase):
    recipe_name = 'recipe_name'

    def setUp(self) -> None:
        self.recipe = Recipe.objects.create(name=self.recipe_name)

    def test_duplicate_name_ok(self):
        Recipe.objects.create(name=self.recipe_name)

    def test_add_info(self):
        self.recipe.serves = 2
        self.recipe.save()

    def test_str(self):
        self.assertEqual(str(self.recipe), self.recipe.name)


class IngredientTest(TestCase):
    ingredient_name = 'base_ingredient'

    def setUp(self):
        self.ingredient = Ingredient.objects.create(name=self.ingredient_name)

    def test_unique_error(self):
        def duplicate_name():
            Ingredient.objects.create(name=self.ingredient_name)
        self.assertRaises(IntegrityError, duplicate_name)

    def test_set_ubiquitous(self):
        self.ingredient.ubiquitous = True
        self.ingredient.save()


class RecipeIngredientTest(TestCase):

    def setUp(self) -> None:
        self.recipe = Recipe.objects.create(name='recipes')
        self.ingredient = Ingredient.objects.create(name='base_ingredient')
        self.ri = RecipeIngredient.objects.create(base_ingredient=self.ingredient, recipe=self.recipe)

    def test_create_directly(self):
        self.assertIsNotNone(RecipeIngredient.objects.first())
        self.assertEqual(self.ri, RecipeIngredient.objects.first())

    def test_set_fields_good_values(self):
        self.ri.measurement = RecipeIngredient.Measurements.choices[1][0]
        self.ri.amount_per_serving = 1
        self.ri.save()

    def test_illegal_amount_per_serving(self):
        self.ri.amount_per_serving = -1
        self.assertRaises(ValidationError, self.ri.save)
        self.ri.amount_per_serving = "a"
        self.assertRaises(ValidationError, self.ri.save)

    def test_illegal_measurement(self):
        # choices are only validated in clean methods, not on save() or other db-related methods.
        self.ri.measurement = 'test'
        self.assertRaises(ValidationError, self.ri.full_clean)
