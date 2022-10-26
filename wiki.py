import requests
from bs4 import BeautifulSoup

wiki_url = "https://fortresscrafte.fandom.com/wiki/Cargo_Lift_Controller"
wiki_html = requests.get(wiki_url).text
wiki_page = BeautifulSoup(wiki_html, 'html.parser')

for image in wiki_page.find_all('img'):
    image_source = image.get('src')
    image_name = image.get('data-image-key')
    if image_source and image_source.startswith('https://static.wikia.nocookie.net/fortresscrafte/images'):
        print(f'{image_name} - {image_source}')
