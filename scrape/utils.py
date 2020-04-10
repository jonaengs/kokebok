from unicodedata import numeric

from recipes.models import Recipe, Ingredient, RecipeIngredient


M = RecipeIngredient.Measurements
conversions = {
    'stk': M.COUNT,
    'stykk': M.COUNT,
    'ts': M.TEASPOONS,
    'dl': M.DECILITERS,
    'ss': M.TABLESPOONS,
    'båt': M.COUNT,
    'g': M.GRAMS,
    'kg': M.KILOGRAMS,
    'håndfull': M.COUNT,
    'skiver': M.SLICES,

    **dict((str(m), m) for m in M)  # add already defined conversions. (tbsp => tbsp, '' => count, etc.)
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
        serves=int(scrape['serves']) if scrape['serves'] else None,
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


def is_number(s):
    return (".".join(s.split(","))).isdigit()  # replace commas with dots before checking for digit
