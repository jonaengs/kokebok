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
    instructions += f'\n\n <a href="{url}">ORIGINAL HER</a>'
    return {
        'name': title,
        'content': instructions,
        'serves': serves,
        'ami': [(None, None, ingr) for ingr in ingredients],
    }


def scrape_nrk(soup):
    title = soup.find('h1', {'itemprop': 'name headline'}).text
    serves = soup.find('li', {'class': 'recipe-icon recipe-icon-portions'}).text.split(" ")[0]

    instructions_div = soup.find('div', {'class': 'article-content'})

    instructions = soup.find('div', {'itemprop': 'description'}).text  # introduction
    instructions += "\n<h3>SLIK GJØR DU:</h3>\n"
    instructions += '<ol>' + "".join(['<li>' + p.text + '</li>' for p in instructions_div.find_all('p')]) + '</ol>'
    if (tips := instructions_div.find('ul')):  # tips are not always present
        instructions += "<h4>TIPS:</h4>" + str(tips)

    ingredient_uls = list(soup.find_all('ul', {'class': 'recipe-list'}))
    ul_1 = ingredient_uls[0]
    if 'recipe-list-meta' in ul_1.get('class'):  # some recipes contain an extra ul wrapping the metadata
        ingredient_uls = ingredient_uls[1:]

    ingredients = [li.text.strip() for ul in ingredient_uls for li in ul.find_all('li')]
    ami = []
    for ingredient in ingredients:
        # examples: "200 g spagetti", "4 cherrytomater", "nykvernet pepper", "2 ss smør til steking"
        parts = ingredient.split(" ")
        if is_number(parts[0]):  # some amount is given
            if len(parts) >= 3:  # measurement given requires length of 3+
                if parts[1] in conversions.keys():  # measurement is known
                    ami.append((parts[0], parts[1], " ".join(parts[2:])))
                else:  # assume no measurement is given, count is then implicit
                    ami.append((parts[0], "stk", " ".join(parts[1:])))
            elif len(parts) == 2:  # no measurement given, assume count
                ami.append((parts[0], "stk", " ".join(parts[1:])))
        else:  # no amount given => no measurement given.
            ami.append((None, None, " ".join(parts)))

    return {
        'name': title,
        'content': instructions,
        'serves': serves,
        'ami': ami,
    }
