from bs4 import BeautifulSoup
import requests
import json

from scrape.utils import unicode_fraction_to_float


def scrape_dispatcher(url):
    sites = {
        'matprat': scrape_matprat,
        'meny': scrape_meny,
        'nrk': scrape_nrk,
    }
    site = url.split('.')[0].split('/')[-1]
    return sites[site]


def scrape(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    scrape = scrape_dispatcher(url)(soup)
    scrape['content'] += f'\n\n <a href="{url}">ORIGINAL HER</a>'
    return scrape


def scrape_matprat(soup):
    instructions = str(soup.find('div', {'class': 'rich-text'}))
    title = soup.find('h1', {'class': 'c-h1'}).text
    default_servings = json_data['recipeYield'][-1]  # incorrect if n >= 10
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
        'default_servings': default_servings,
        'ami': amount_measurement_ingredient
    }


def scrape_meny(soup):
    # Does not find ingredient amounts or measurements :(
    # Meny laster inn / renderer oppskriftdata etter siden har lastet. Noe data sendes som json
    page_json_content = soup.find('script', {'type': 'application/ld+json'})
    json_data = json.loads(page_json_content.text)

    title = soup.find('h1', {'class': 'c-h1'}).text
    default_servings = json_data['recipeYield'][-1]  # incorrect if n >= 10
    ingredients = [ingredient.strip() for ingredient in json_data["recipeIngredient"]]

    instructions = str(soup.find('div', {'class': 'c-recipe__intro'})) + "\n\n"
    instructions += "\n".join(map(lambda elem: elem['text'], json_data['recipeInstructions']))
    instructions += f'\n\n <a href="{url}">ORIGINAL HER</a>'
    return {
        'name': title,
        'content': instructions,
        'default_servings': default_servings,
        'ami': [(None, None, ingr) for ingr in ingredients],
    }


def scrape_nrk(soup):
    title = soup.find('h1', {'itemprop': 'name headline'})
    default_servings = soup.find('li', {'class': 'recipe-icon recipe-icon-portions'}).text

    ingredient_uls = soup.find_all('ul', {'class': 'recipe-list'})
    ingredients = [ul.find_all('li')]

