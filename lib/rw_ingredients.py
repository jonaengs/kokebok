from django.utils.text import slugify

import recipes.models


def write_ingredients():
    Ingredient = recipes.models.Ingredient
    with open('ingredients.txt', mode='w', encoding='utf-8') as f:
        f.writelines([ingredient.name + "\n" for ingredient in Ingredient.objects.all()])


def read_ingredients():
    Ingredient = recipes.models.Ingredient
    with open('ingredients.txt', mode='r') as f:
        for ingredient_name in f.readlines():
            Ingredient.objects.create(name=ingredient_name)


def slugify_norwegian(name):
    for char, replacement in (('ø', 'o'), ('æ', 'a'), ('å', 'a')):
        name = name.replace(char, replacement)
    return slugify(name)
