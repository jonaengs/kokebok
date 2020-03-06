from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from recipe.models import Recipe, Ingredient, RecipeIngredient, Variation

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

    def test_recipe_add_ingredient(self):
        ingredient = Ingredient.objects.create(name='ingredient')
        # pycharm will complain about this, but it works fine
        self.recipe.ingredient_objects.add(ingredient, through_defaults={'recipe': self.recipe, 'ingredient': ingredient})
        self.assertIsNotNone(RecipeIngredient.objects.first())
        self.assertEquals(RecipeIngredient.objects.all().count(), 1)

    def test_recipe_create_ingredient(self):
        ingredient = Ingredient.objects.create(name='ingredient')
        self.recipe.ingredient_objects.create(through_defaults={'recipe': self.recipe, 'ingredient': ingredient})
        self.assertIsNotNone(RecipeIngredient.objects.first())
        self.assertEquals(RecipeIngredient.objects.all().count(), 1)

    def test_recipe_set_ingredient(self):
        # set should remove any previous
        self.test_recipe_add_ingredient()
        ingredients = Ingredient.objects.create(name='ingredient1'), Ingredient.objects.create(name='ingredient2')
        self.recipe.ingredient_objects.set(ingredients)
        self.assertEquals(RecipeIngredient.objects.all().count(), 2)
        self.assertNotEqual(RecipeIngredient.objects.all()[0].ingredient, RecipeIngredient.objects.all()[1].ingredient)
        self.assertEqual(RecipeIngredient.objects.all()[0].recipe, RecipeIngredient.objects.all()[1].recipe)


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

    def test_update_method(self):
        self.recipe.update_recipe_ingredient(
            self.ingredient.id, 'amount_per_serving', 10
        )
        self.ri = RecipeIngredient.objects.get(pk=self.ri.pk)  # must be retrieved again to get updated attributes
        self.assertEqual(self.ri.amount_per_serving, 10)


class VariationTest(TestCase):

    def setUp(self):
        self.recipe = Recipe.objects.create(name='recipe')
        ingredient1 = Ingredient.objects.create(name='ingredient1')
        ingredient2 = Ingredient.objects.create(name='ingredient2')
        self.recipe.ingredient_objects.set((ingredient1, ingredient2))
        self.variant = Variation.objects.create(original=self.recipe)

    def test_inheritance(self):
        self.assertEqual(self.recipe, self.variant.original)

    def test_ingredient_inheritance(self):
        for i1, i2 in zip(self.recipe.ingredient_objects.all().order_by('id'),  # recipe and variant share ingredients
                          self.variant.ingredient_objects.all().order_by('id')):
            self.assertEqual(i1, i2)
        for i1, i2 in zip(self.recipe.ingredient_objects.all().order_by('id'),  # variant and original share ingredients
                          self.variant.original.ingredient_objects.all().order_by('id')):
            self.assertEqual(i1, i2)

    def test_change_variant_ingredient(self):
        for recipe_ingredient in self.variant.recipe_ingredients.all():
            recipe_ingredient.amount_per_serving = 10
            recipe_ingredient.save()
        for recipe_ingredient in self.variant.recipe_ingredients.all():
            self.assertEqual(recipe_ingredient.amount_per_serving, 10)
        for recipe_ingredient in self.recipe.recipe_ingredients.all():
            self.assertEqual(recipe_ingredient.amount_per_serving, None,
                             msg="change in variant ingredients should not change those of the original recipe")

    def test_variation_inheritance(self):
        variant2 = Variation.objects.create(original=self.variant)
        self.assertEqual(self.variant, variant2.original)
