from collections import deque
from genericpath import isfile
import json
import requests
from argparse import ArgumentParser
from bs4 import BeautifulSoup
from pathlib import Path
from typing import Dict, List, Set, Tuple, Callable, Union
import time

DEFAULT_WIKI_URL = 'https://fortresscrafte.fandom.com/wiki/FortressCraft_Evolved_Wiki'

DEFAULT_BASE_WIKI_IMAGE_DOMAIN = 'https://static.wikia.nocookie.net/fortresscrafte/images'

def get_page(url: str) -> BeautifulSoup:
    if url.startswith('http'):
        print(f'Getting content of page: "{url}"')
        page_content = requests.get(url).text
        time.sleep(0.1)
    else:
        page_file = Path(url)
        if page_file.exists() and page_file.is_file():
            with page_file.open('r') as page:
                page_content = page.read()
        else:
            page_content = ''
    return BeautifulSoup(page_content, 'html.parser')

def scrap_images(url: str, base_image_domain: str = DEFAULT_BASE_WIKI_IMAGE_DOMAIN, base_wiki_domain: Union[str, None] = None, get_page: Callable[[str], BeautifulSoup] = get_page) -> Dict[str, Set[str]]:
    base_wiki_domain = (url[:url.rfind('/')] if url.rfind('/') > 8 else url) if base_wiki_domain is None else base_wiki_domain
    images = dict()
    visited = set()
    page_queue = deque({url})
    while len(page_queue) > 0:
        page_url = page_queue.popleft()
        if page_url.startswith(base_wiki_domain) and 'Forum' not in page_url and page_url not in visited:
            visited.add(page_url)
            wiki_page = get_page(page_url)
            page_queue.extend(get_links(wiki_page, page_url))
            for image_source, image_names in get_images(wiki_page, base_image_domain).items():
                images.setdefault(image_source, set()).update(image_names)
    return images

def get_images(page: BeautifulSoup, base_image_domain: str = DEFAULT_BASE_WIKI_IMAGE_DOMAIN) -> Dict[str, Set[str]]:
    images = dict()
    for image in page.find_all('img'):
        image_source = image.get('src')
        if image_source and image_source.startswith(base_image_domain):
            image_name = image.get('data-image-key')
            image_file = None
            for source_part in image_source.split('/'):
                if source_part.endswith('.png') or source_part.endswith('.ico') or source_part.endswith('.jpg') or source_part.endswith('.jpeg'):
                    image_file = source_part
            if image_file:
                images.setdefault(image_source, set()).add(image_file)
                if image_name:
                    images[image_source].add(image_name)
    return images

def get_links(page: BeautifulSoup, url: str) -> Set[str]:
    base_url = get_base_url(page, url)
    protocol = get_protocol(base_url)
    page_links = set()
    for link in page.find_all('a'):
        link_url = link.get('href')
        if link_url is None or link_url.startswith('#'):
            continue
        if link_url.startswith('//'):
            page_links.add(f'{protocol}:{link_url}')
        elif link_url.startswith('/'):
            page_links.add(f'{base_url}link_url')
        else:
            page_links.add(link_url)
    return page_links


def get_base_url(page: BeautifulSoup, url: str) -> str:
    base_url = url[:url.find('/', 8)] if url.find('/', 8) > 0 else url
    for base in page.find_all('base'):
        base_url = base.get('href')
        break
    return base_url

def get_protocol(url: str) -> str:
    return url[:url.find('://')]


def main():
    # Parse command line arguments
    parser = ArgumentParser()
    parser.add_argument('url', nargs='?', default=DEFAULT_WIKI_URL, help='The URL of the FortressCraft Evolved! wiki')
    args = parser.parse_args()

    images = scrap_images(args.url)
    print(json.dumps({image_source: sorted(list(image_names)) for image_source, image_names in images.items()}, indent=4, sort_keys=True))

if __name__ == '__main__':
    main()
