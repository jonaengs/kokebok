from recipes.models import Ingredient


def write_ingredients():
    with open('ingredients.txt', mode='w', encoding='utf-8') as f:
        f.writelines([ingredient.name + "\n" for ingredient in Ingredient.objects.all()])


def read_ingredients():
    with open('ingredients.txt', mode='r') as f:
        for ingredient_name in f.readlines():
            Ingredient.objects.create(name=ingredient_name)
