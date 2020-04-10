from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from recipes.models import Recipe, Ingredient, RecipeIngredient, Variation, Category, IngredientCategory, RecipeCategory, \
    BaseCategoryConnection, IngredientCategoryConnection, RecipeCategoryConnection

User = get_user_model()


class RecipeTest(TestCase):
    recipe_name = 'recipe_name'

    def setUp(self) -> None:
        self.recipe = Recipe.objects.create(name=self.recipe_name)
        self.user = get_user_model().objects.create_user(email='test@test.com', password='123')

    def test_duplicate_name_ok(self):
        Recipe.objects.create(name=self.recipe_name)

    def test_add_info(self):
        self.recipe.serves = 2
        self.recipe.public = True
        self.recipe.author = self.user
        self.recipe.save()

    def test_str(self):
        self.assertEqual(str(self.recipe), self.recipe.name)

    def test_recipe_add_ingredient(self):
        ingredient = Ingredient.objects.create(name='base_ingredient')
        # pycharm will complain about this, but it works fine
        self.recipe.ingredient_objects.add(ingredient)
        self.assertIsNotNone(RecipeIngredient.objects.first())
        self.assertEquals(RecipeIngredient.objects.all().count(), 1)

    def test_recipe_create_ingredient(self):
        ingredient = Ingredient.objects.create(name='base_ingredient')
        self.assertEqual(RecipeIngredient.objects.all().count(), 0)
        self.recipe.ingredient_objects.create()
        self.assertIsNotNone(RecipeIngredient.objects.first())
        self.assertEquals(RecipeIngredient.objects.all().count(), 1)
        recipe_ingredient = RecipeIngredient.objects.first()
        recipe_ingredient.ingredient = ingredient
        recipe_ingredient.save()
        self.assertEqual(RecipeIngredient.objects.first().ingredient, recipe_ingredient.ingredient)

    def test_recipe_set_ingredient(self):
        # set should remove any previous
        self.test_recipe_add_ingredient()
        ingredients = Ingredient.objects.create(name='ingredient1'), Ingredient.objects.create(name='ingredient2')
        self.recipe.ingredient_objects.set(ingredients)
        self.assertEquals(RecipeIngredient.objects.all().count(), 2)
        self.assertNotEqual(RecipeIngredient.objects.all()[0].ingredient, RecipeIngredient.objects.all()[1].ingredient)
        self.assertEqual(RecipeIngredient.objects.all()[0].recipe, RecipeIngredient.objects.all()[1].recipe)


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


class VariationTest(TestCase):

    def setUp(self):
        self.recipe = Recipe.objects.create(name='recipes')
        ingredient1 = Ingredient.objects.create(name='ingredient1')
        ingredient2 = Ingredient.objects.create(name='ingredient2')
        self.recipe.ingredient_objects.set((ingredient1, ingredient2))
        self.variant = Variation.objects.create(original=self.recipe)

    def test_inheritance(self):
        self.assertEqual(self.recipe, self.variant.original)

    def test_ingredient_inheritance(self):
        for i1, i2 in zip(self.recipe.ingredient_objects.all().order_by('id'),  # recipes and variant share ingredients
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
                             msg="change in variant ingredients should not change those of the original recipes")

    def test_variation_inheritance(self):
        variant2 = Variation.objects.create(original=self.variant)
        self.assertEqual(self.variant, variant2.original)


class CategoriesTest(TestCase):

    # === BEGIN HELPER METHODS ===
    def setup_tree(self, cls):
        self.middle_category = cls.objects.create(name='middle_category')
        self.leaf_category = cls.objects.create(name='leaf_category')
        self.root_category = cls.objects.create(name='root_category')
        self.categories = (self.leaf_category, self.middle_category, self.root_category)

        self.middle_category.parent = self.root_category
        self.leaf_category.parent = self.middle_category
        for cat in (self.middle_category, self.leaf_category, self.root_category):
            cat.save()

    def assertQuerysetContentsEqual(self, queryset1, queryset2):
        for o1, o2 in zip(queryset1, queryset2):
            self.assertEqual(o1, o2)
    # === END HELPER METHODS ===

    def test_base_connection(self):
        self.assertTrue(BaseCategoryConnection._meta.abstract)

    def test_category_model_abstract(self):
        self.assertTrue(Category._meta.abstract)

    def test_category_subclass(self):
        self.assertTrue(issubclass(RecipeCategory, Category))
        self.assertTrue(issubclass(IngredientCategory, Category))

    def test_base_connection_subclass(self):
        self.assertTrue(issubclass(IngredientCategoryConnection, BaseCategoryConnection))
        self.assertTrue(issubclass(RecipeCategoryConnection, BaseCategoryConnection))

    def test_mptt_tree_implemented_correctly(self):
        for cls in (RecipeCategory, IngredientCategory):
            self.setup_tree(cls)
            self.assertQuerysetContentsEqual(self.root_category.get_family(), self.middle_category.get_family())
            self.assertQuerysetContentsEqual(self.middle_category.get_family(), self.leaf_category.get_family())
            self.assertEqual(self.root_category.get_family().count(), 3)
            self.assertTrue(all(
                category in self.root_category.get_family() for category in self.categories
            ))

    def test_insert_same_object_twice_in_family_fails(self):
        self.setup_tree(IngredientCategory)
        ingredient = Ingredient.objects.create(name='test')
        IngredientCategoryConnection.objects.create(ingredient=ingredient, category=self.leaf_category)
        try:
            IngredientCategoryConnection.objects.create(ingredient=ingredient, category=self.root_category)
        except ValidationError:
            pass
        else:
            self.fail()

        self.setup_tree(RecipeCategory)
        recipe = Recipe.objects.create(name='test')
        RecipeCategoryConnection.objects.create(recipe=recipe, category=self.middle_category)
        try:
            RecipeCategoryConnection.objects.create(recipe=recipe, category=self.root_category)
        except ValidationError:
            pass
        else:
            self.fail()

    def test_only_object_of_right_type_can_be_present_in_type_category(self):
        ingredient = Ingredient.objects.create(name='test1')
        recipe = Recipe.objects.create(name='test1')

        self.setup_tree(IngredientCategory)
        IngredientCategoryConnection.objects.create(ingredient=ingredient, category=self.leaf_category)
        try:
            RecipeCategoryConnection.objects.create(recipe=recipe, category=self.middle_category)
        except ValueError:
            pass
        else:
            self.fail()

        self.setup_tree(RecipeCategory)
        RecipeCategoryConnection.objects.create(recipe=recipe, category=self.middle_category)
        try:
            IngredientCategoryConnection.objects.create(ingredient=ingredient, category=self.leaf_category)
        except ValueError:
            pass
        else:
            self.fail()
