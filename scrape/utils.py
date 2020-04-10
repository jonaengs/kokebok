from unicodedata import numeric

from recipes.models import Recipe, Ingredient, RecipeIngredient

conversions = {
    'stk': '',
    'ts': 'tsp',
    'dl': 'dl',
    'ss': 'tbsp',
    'båt': '',
    'g': 'g',
    'kg': 'kg',
}


# Taken from https://stackoverflow.com/a/50264056/8132000
def unicode_fraction_to_float(num):
    if len(num) == 1:
        return numeric(num)
    elif num[-1].isdigit():
        # normal number, ending in [0-9]
        return float(num)
    else:
        # Assume the last character is a vulgar fraction
        return float(num[:-1]) + numeric(num[-1])


def create_recipe_from_scrape(scrape):
    recipe = Recipe.objects.create(
        name=scrape['name'],
        content=scrape['content'],
        default_servings=int(scrape['default_servings']) if scrape['default_servings'] else None,
        public=True
    )
    for a, m, i in scrape["ami"]:
        base_ingredient = find_base_ingredient(i)
        RecipeIngredient.objects.create(
            name=i,
            recipe=recipe,
            base_ingredient=base_ingredient,
            amount_per_serving=int(a) if a else None,
            measurement=conversions[m] if m else ""
        )
    return recipe


def find_base_ingredient(ingredient_name):
    base = Ingredient.objects.filter(name__in=ingredient_name.split(" "))
    if base.exists():
        if len(base) > 1:
            print(f"\n\n\n more than one potential ingredient. Choosing the first one. \n{base}\n\n\n")
        return base[0]
    if len(ingredient_name.split(" ")) == 1:  # one word ingredient => no strange adjectives => probably base ingredient
        return Ingredient.objects.create(name=ingredient_name, ubiquitous=False)
    return None


