from urllib.parse import urlparse

from bs4 import BeautifulSoup
import requests
import json

from scrape.utils import unicode_fraction_to_float, conversions, is_number


def get_sites():
    return {
        'matprat': scrape_matprat,
        'meny': scrape_meny,
        'nrk': scrape_nrk,
    }

def get_scrape_func(url):
    sites = get_sites()
    netloc = urlparse(url).netloc.split(".")  # https://wwww.google.com/?q=aisdhaA_Sd => ['www', 'google', 'com']
    site = netloc[1] if netloc[0].lower() == 'www' else netloc[0]  # some urls start 'www.', some dont
    if site not in sites.keys():
        raise ValueError("Domain of passed url not found in scrape table")
    return sites[site]


def scrape(url):
    """
    :param url: site to be scraped. Must be present in the sites map in scrape_linker()
    :return: Dictionary containing data for creation of a recipe and corresponding ingredients and recipe_ingredients.
        All keys and values are strings.
        'name': name string
        'content': content string. Often html in string format
        'serves': default servings. May be None
        'ami': list of tuples (amount, measurement, ingredient) for the creation of recipe ingredients
        'sub_recipes': dictionary of sub-recipes in the recipe. Form: {sub-recipe title : sub-recipe ami}
    """
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    scrape_dict = get_scrape_func(url)(soup)
    scrape_dict['content'] += f'\n\n <a href="{url}">ORIGINAL HER</a>'
    return scrape_dict


def scrape_matprat(soup):
    title = soup.find('h1', {'class': 'article-title lp_is_start'}).text
    serves = soup.find('input', {'id': 'portionsInput'}).get('value')
    instructions = str(soup.find('div', {'class': 'rich-text'}))

    ingredient_lists = soup.find_all('li', {"itemprop": "ingredients"})
    amount_measurement_ingredient = []
    for ingredient_item in ingredient_lists:
        listing = ingredient_item.text.strip().split("\n")
        if len(listing) >= 4:
            listing[-1] = listing[0].strip() + " " + listing[-1].strip()
            listing = listing[1:]
        amount = unicode_fraction_to_float(listing[0].strip())
        amount_measurement_ingredient.append((amount, listing[1].strip(), (listing[-1].strip())))
    return {
        'name': title,
        'content': instructions,
        'serves': serves,
        'ami': amount_measurement_ingredient
    }


def scrape_meny(soup):
    # Does not find ingredient amounts or measurements :(
    # Meny laster inn / renderer oppskriftdata etter siden har lastet. Noe data sendes som json
    page_json_content = soup.find('script', {'type': 'application/ld+json'})
    json_data = json.loads(page_json_content.text)

    title = soup.find('h1', {'class': 'c-h1'}).text
    serves = json_data['recipeYield'][-1]  # incorrect if n >= 10
    ingredients = [ingredient.strip() for ingredient in json_data["recipeIngredient"]]

    instructions = str(soup.find('div', {'class': 'c-recipe__intro'})) + "\n\n"
    instructions += "\n".join(map(lambda elem: elem['text'], json_data['recipeInstructions']))
    return {
        'name': title,
        'content': instructions,
        'serves': serves,
        'ami': [(None, None, ingr) for ingr in ingredients],
    }


def scrape_nrk(soup):
    def ingredients_list_to_ami(ingredients):
        ami = []
        for ingredient in ingredients:
            # example ingredient strings: "200 g spagetti", "4 cherrytomater", "nykvernet pepper", "2 ss smør til steking"
            parts = ingredient.split(" ")
            amount, measure, ingredient = None, None, None
            if is_number(parts[0]):  # Amount specified
                amount = parts.pop(0)
                if len(parts) >= 2:  # measurement given requires length of 3+
                    if parts[0] in conversions.keys():  # measurement is known
                        measure = parts.pop(0)
                if measure is None:  # Didn't find measure, assume count
                    measure = 'stk'
            ingredient = " ".join(parts)
            ami.append((amount, measure, ingredient))
        return ami

    def build_instructions():
        instructions_div = soup.find('div', {'class': 'article-content'})
        instructions = soup.find('div', {'itemprop': 'description'}).text  # introduction
        instructions += "<hr>"
        instructions += "".join([str(elem) for elem in instructions_div.find_all(['p', 'h2'])])
        tips = instructions_div.find('ul')
        if tips:  # tips are not always present
            instructions += "<h4>TIPS:</h4>" + str(tips)
        return instructions

    title = soup.find('h1', {'itemprop': 'name headline'}).text
    serves = soup.find('li', {'class': 'recipe-icon recipe-icon-portions'}).text.split(" ")[0]

    instructions = build_instructions()

    # remove meta-data uls that clutter the ingredient uls. Removes them from the soup altogether, so DO LAST.
    all(ul.extract() for ul in soup.find_all('ul', {'class': 'recipe-list recipe-list-meta'}))

    ingredient_uls = list(soup.find_all('ul', {'class': 'recipe-list'}))
    ami, sub_recipes = [], {}
    for ul in ingredient_uls:
        ul_title = ul.previous_sibling.previous_sibling
        ul_ingredients = [li.text.strip() for li in ul.find_all('li')]
        if ul_title.name == 'h4':  # sub-recipe
            sub_recipes[ul_title.text] = ingredients_list_to_ami(ul_ingredients)
        else:
            ami += ingredients_list_to_ami(ul_ingredients)

    return {
        'name': title,
        'content': instructions,
        'serves': serves,
        'ami': ami,
        'sub_recipes': sub_recipes
    }
