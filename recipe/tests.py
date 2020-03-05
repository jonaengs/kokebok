from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from recipe.models import Recipe, Ingredient, RecipeIngredient

User = get_user_model()


class RecipeTest(TestCase):
    recipe_name = 'recipe_name'

    def setUp(self) -> None:
        self.recipe = Recipe.objects.create(name=self.recipe_name)
        self.user = get_user_model().objects.create_user(email='test@test.com', password='123')

    def test_duplicate_name_ok(self):
        Recipe.objects.create(name=self.recipe_name)

    def test_add_info(self):
        self.recipe.default_servings = 2
        self.recipe.public = True
        self.recipe.author = self.user
        self.recipe.save()

    def test_str(self):
        self.assertEqual(str(self.recipe), self.recipe.name)


class IngredientTest(TestCase):
    ingredient_name = 'ingredient'

    def setUp(self):
        self.ingredient = Ingredient.objects.create(name=self.ingredient_name)

    def test_unique_error(self):
        def duplicate_name():
            Ingredient.objects.create(name=self.ingredient_name)
        self.assertRaises(IntegrityError, duplicate_name)

    def test_set_ubiquitous(self):
        self.ingredient.ubiquitous = True
        self.ingredient.save()

    def test_ingredient_add_recipe(self):
        recipe = Recipe.objects.create(name='recipe')
        # pycharm will complain about this, but it works fine
        self.ingredient.recipes.add(recipe, through_defaults={'recipe': recipe, 'ingredient': self.ingredient})
        self.assertIsNotNone(RecipeIngredient.objects.first())
        self.assertEquals(RecipeIngredient.objects.all().count(), 1)

    def test_ingredient_create_recipe(self):
        recipe = Recipe.objects.create(name='recipe')
        self.ingredient.recipes.create(through_defaults={'recipe': recipe, 'ingredient': self.ingredient})
        self.assertIsNotNone(RecipeIngredient.objects.first())
        self.assertEquals(RecipeIngredient.objects.all().count(), 1)

    def test_ingredient_set_recipe(self):
        # set should remove any previous
        self.test_ingredient_add_recipe()
        recipes = Recipe.objects.create(name='recipe'), Recipe.objects.create(name='recipe')
        self.ingredient.recipes.set(recipes)
        self.assertEquals(RecipeIngredient.objects.all().count(), 2)
        self.assertTrue(RecipeIngredient.objects.all()[0].recipe != RecipeIngredient.objects.all()[1].recipe)


class RecipeIngredientTest(TestCase):

    def setUp(self) -> None:
        self.recipe = Recipe.objects.create(name='recipe')
        self.ingredient = Ingredient.objects.create(name='ingredient')
        self.ri = RecipeIngredient.objects.create(ingredient=self.ingredient, recipe=self.recipe)

    def test_create_directly(self):
        self.assertIsNotNone(RecipeIngredient.objects.first())
        self.assertEqual(self.ri, RecipeIngredient.objects.first())

    def test_set_fields_good_values(self):
        self.ri.measurement = RecipeIngredient.Measurements.choices[0]
        self.ri.amount_per_serving = 1
        self.ri.save()

    def test_illegal_amount_per_serving(self):
        self.ri.amount_per_serving = -1
        self.assertRaises(IntegrityError, self.ri.save)
        self.ri.amount_per_serving = "a"
        self.assertRaises(ValueError, self.ri.save)

    def test_illegal_measurement(self):
        # choices are only validated in clean methods, not on save() or other db-related methods.
        self.ri.measurement = 'test'
        self.assertRaises(ValidationError, self.ri.full_clean)
