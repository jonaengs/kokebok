from unicodedata import numeric

from recipes.models import Recipe, Ingredient, RecipeIngredient

M = RecipeIngredient.Measurements
conversions = {
    'stk': M.COUNT,
    'stykk': M.COUNT,
    'ts': M.TEASPOONS,
    'dl': M.DECILITERS,
    'cl': M.CENTILITERS,
    'ml': M.MILLILITERS,
    'ss': M.TABLESPOONS,
    'båt': M.COUNT,
    'g': M.GRAMS,
    'kg': M.KILOGRAMS,
    'håndfull': M.COUNT,
    'skiver': M.SLICES,

    **dict((str(m), m) for m in M)  # add already defined conversions. (tbsp => tbsp, '' => count, etc.)
}


# From https://stackoverflow.com/a/50264056/8132000
def unicode_fraction_to_float(num):
    if len(num) == 1:
        return numeric(num)
    elif num[-1].isdigit():  # normal number, ending in [0-9]
        return float(num)
    else:  # Assume the last character is a vulgar fraction
        return float(num[:-1]) + numeric(num[-1])


def create_recipe_ingredient_from_ami(ami, recipe):
    for a, m, i in ami:
        base_ingredient = find_base_ingredient(i)
        RecipeIngredient.objects.create(
            name=i,
            recipe=recipe,
            base_ingredient=base_ingredient,
            amount_per_serving=a,
            measurement=conversions[m] if m else ""
        )


def create_recipe_from_scrape(scrape_dict):
    ami = scrape_dict.pop('ami')
    recipe = Recipe.objects.create(**scrape_dict)
    create_recipe_ingredient_from_ami(ami, recipe=recipe)
    return recipe


def find_base_ingredient(ingredient_name):
    candidates = Ingredient.objects.filter(name__in=ingredient_name.split(" "))
    if not candidates.exists() and len(ingredient_name.split(" ")) == 1:
        # one word => no adjectives. Create ingredient with same name
        return Ingredient.objects.create(name=ingredient_name, ubiquitous=False)
    return candidates[0] if candidates else None


def is_number(s):
    return s.replace(",", ".").isdigit()  # replace commas with dots before checking for digit
