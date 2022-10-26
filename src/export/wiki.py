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

def get_page(url: str, debug_dump_file: Union[Path, None] = None) -> BeautifulSoup:
    if url.startswith('http'):
        print(f'Getting content of page: "{url}"')
        page_content = requests.get(url).text
        if debug_dump_file is not None:
            debug_dump_file.touch()
            debug_dump_file.write_text(page_content)
        time.sleep(0.1)
    else:
        page_file = Path(url)
        if page_file.exists() and page_file.is_file():
            page_content = page_file.read_text()
        else:
            page_content = ''
    return BeautifulSoup(page_content, 'html.parser')

def scrap_images(url: str, base_image_domain: str = DEFAULT_BASE_WIKI_IMAGE_DOMAIN, base_wiki_domain: Union[str, None] = None, get_page: Callable[[str, Union[Path, None]], BeautifulSoup] = get_page) -> Dict[str, Set[str]]:
    base_wiki_domain = (url[:url.rfind('/')] if url.rfind('/') > 8 else url) if base_wiki_domain is None else base_wiki_domain
    images = dict()
    debug_files = dict()
    debug_dir = Path(__file__).parent / 'debug'
    if not debug_dir.exists():
        debug_dir.mkdir()
    visited = set()
    page_queue = deque({url})
    while len(page_queue) > 0:
        page_url = page_queue.popleft()
        if page_url.startswith(base_wiki_domain) \
                and 'Template' not in page_url \
                and 'Forum:' not in page_url \
                and 'User:' not in page_url \
                and 'Help:' not in page_url \
                and 'Help_talk:' not in page_url \
                and 'User_blog:' not in page_url \
                and 'Message_Wall' not in page_url \
                and 'Special:Log' not in page_url \
                and 'Special:Search' not in page_url \
                and 'Special:Contributions' not in page_url \
                and 'action=' not in page_url \
                and 'oldid=' not in page_url \
                and 'diff=' not in page_url \
                and page_url not in visited:
            # debug
            debug_file_name = page_url
            debug_file_name = debug_file_name[:debug_file_name.find('?')] if debug_file_name.find('?') > 0 else debug_file_name
            debug_file_name = debug_file_name[debug_file_name.rfind('/')+1:] if debug_file_name.rfind('/') > 0 else debug_file_name
            debug_files.setdefault(debug_file_name, list()).append(page_url)
            debug_file_name = f'{debug_file_name}_{len(debug_files[debug_file_name])}.html'
            debug_file_path = debug_dir / debug_file_name
            visited.add(page_url)
            wiki_page = get_page(page_url, debug_file_path)
            page_queue.extend(get_links(wiki_page, page_url))
            for image_source, image_names in get_images(wiki_page, base_image_domain).items():
                images.setdefault(image_source, set()).update(image_names)
    debug_index = debug_dir / '_index.json'
    if debug_index.exists():
        debug_index.unlink()
        debug_index.touch()
    debug_index.write_text(json.dumps(debug_files, indent=4, sort_keys=True))
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
            page_links.add(f'{base_url}{link_url}')
        else:
            page_links.add(link_url)
    return page_links


def get_base_url(page: BeautifulSoup, url: str) -> str:
    base_url = None
    for base in page.find_all('base'):
        base_url = base.get('href')
        if base_url is not None:
            break
        # TODO: support base url as tag value see FortressCraft_Evolved_Wiki_2.html
    if base_url is None:
        base_url = url[:url.find('/', 8)] if url.find('/', 8) > 0 else url
    return base_url

def get_protocol(url: str) -> str:
    return url[:url.find('://')]


def main():
    # Parse command line arguments
    parser = ArgumentParser()
    parser.add_argument('url', nargs='?', default=DEFAULT_WIKI_URL, help='The URL of the FortressCraft Evolved! wiki')
    args = parser.parse_args()

    images = scrap_images(args.url)
    output = Path(__file__).parent / 'images.json'
    output.touch()
    output.write_text(json.dumps({image_source: sorted(list(image_names)) for image_source, image_names in images.items()}, indent=4, sort_keys=True))

if __name__ == '__main__':
    main()
