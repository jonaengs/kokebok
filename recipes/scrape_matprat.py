from bs4 import BeautifulSoup
import requests

from recipes.measurement_converter import unicode_fraction_to_float

"""
fname = 'test_page.html'
with io.open(fname, "w", encoding="utf-8") as f:
    f.write(str(page.text))
    with open(fname, mode='r') as file:

"""


def scrape_matprat(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    default_servings = soup.find('input', {'id': 'portionsInput'}).get('value')
    title = soup.find('h1', {'class': 'article-title lp_is_start'}).text

    instructions = str(soup.find('div', {'class': 'rich-text'}))
    instructions += f'\n\n <a href="{url}">ORIGINAL HER</a>'

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





