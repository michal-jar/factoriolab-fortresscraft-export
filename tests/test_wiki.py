from .context import wiki

import unittest
from bs4 import BeautifulSoup
from pathlib import Path


class WikiTestCase(unittest.TestCase):

    TEST_DATA = Path(__file__).parent / 'data'

    TEST_PAGE = TEST_DATA / 'Cargo_Lift_Controller.html'

    def test_get_protocol(self):
        test_cases = [
            ('http', 'http://page.url'),
            ('https', 'https://secure.page.url'),
            ('file', 'file:///local/file.ext')
            ]
        for i, (protocol, url) in enumerate(test_cases):
            with self.subTest(f'{i}: "{protocol}" is protocol of "{url}"'):
                self.assertEqual(wiki.get_protocol(url), protocol)

    def test_get_base_url(self):
        test_cases = [
            ('Cargo_Lift_Controller.html', 'http://page.url', 'http://page.url'),
            ('Cargo_Lift_Controller.html', 'https://secure.page.url', 'https://secure.page.url'),
            ('Cargo_Lift_Controller.html', 'http://page.url', 'http://page.url/'),
            ('Cargo_Lift_Controller.html', 'https://secure.page.url', 'https://secure.page.url/'),
            ('Cargo_Lift_Controller.html', 'http://page.url', 'http://page.url/wiki/fortress_craft_evolved/Cargo_Lift_Controller.html'),
            ('Cargo_Lift_Controller.html', 'https://secure.page.url', 'https://secure.page.url/wiki/fortress_craft_evolved/Cargo_Lift_Controller.html'),
            ]
        for i, (page_name, base_url, url) in enumerate(test_cases):
            with self.subTest(f'{i}: Should get "{base_url}"'):
                page_path = self.TEST_DATA / page_name
                page = BeautifulSoup(page_path.read_text(), 'html.parser')
                self.assertEqual(wiki.get_base_url(page, url), base_url)

    def test_get_links(self):
        page = BeautifulSoup(self.TEST_PAGE.read_text(), 'html.parser')
        url = 'https://fortresscrafte.fandom.com/wiki/Cargo_Lift_Controller'
        links = {'https://www.facebook.com/getfandom', 'https://www.fandom.com/topics/movies', 'https://www.fandom.com/', 'https://fortresscrafte.fandom.com/wiki/Research_Projects', 'https://static.wikia.nocookie.net/fortresscrafte/images/f/fe/Cargo_Lift_Controller.png/revision/latest?cb=20180804002939', 'https://www.youtube.com/fandomentertainment', 'https://www.fandom.com/terms-of-use', 'https://about.fandom.com/mediakit#contact', 'https://static.wikia.nocookie.net/fortresscrafte/images/f/fc/Iron_Gear.png/revision/latest?cb=20160721235534', 'https://fortresscrafte.fandom.com/wiki/Blog:Recent_posts', 'https://www.fandom.com/video', 'https://www.fanatical.com/', 'https://www.instagram.com/getfandom/', 'https://www.fandom.com/licensing', 'https://www.fandom.com/careers', 'https://www.fandom.com/press', 'https://community.fandom.com/Sitemap', 'https://fortresscrafte.fandom.com/wiki/Streamer%27s/Youtuber%27s', 'https://www.futhead.com/', 'https://twitter.com/getfandom', 'https://bit.ly/FanLabWikiBar', 'https://fortresscrafte.fandom.com/wiki/Machines', 'https://community.fandom.com/wiki/Community_Central', 'https://www.fandomatic.com', 'https://www.fandom.com/about', 'http://steamcommunity.com/app/254200', 'https://www.fandom.com/explore', 'https://www.linkedin.com/company/157252', 'https://createnewwiki.fandom.com/Special:CreateNewWiki', 'https://play.google.com/store/apps/details?id=com.fandom.app&referrer=utm_source%3Dwikia%26utm_medium%3Dglobalfooter', 'https://www.fandom.com/do-not-sell-my-info', 'https://about.fandom.com/mediakit', 'https://fandom.zendesk.com/', 'https://www.fandom.com/topics/tv', 'https://static.wikia.nocookie.net/fortresscrafte/images/4/43/Copper_Wire.png/revision/latest?cb=20160721234453', 'https://fortresscrafte.fandom.com', 'https://www.fandom.com/what-is-fandom', 'https://www.fandom.com/about#contact', 'https://fortresscrafte.fandom.com/wiki/Tools', 'https://auth.fandom.com/register?redirect=https%3A%2F%2Ffortresscrafte.fandom.com%2Fwiki%2FCargo_Lift_Controller', 'https://fortresscrafte.fandom.com/wiki/Survival_Mode', 'https://fortresscrafte.fandom.com/wiki/Special:AllPages', 'https://www.cortexrpg.com/', 'https://fortresscrafte.fandom.com/wiki/Ores', 'https://static.wikia.nocookie.net/fortresscrafte/images/2/27/Cargo-lift-1.jpg/revision/latest?cb=20160711213019', 'https://apps.apple.com/us/app/fandom-videos-news-reviews/id1230063803', 'https://bit.ly/FandomIG', 'https://letsgoluna.fandom.com/wiki/Let%27s_Go_Luna!_Wiki', 'https://www.fandom.com/topics/games', 'http://bit.ly/en-spotlight-universalconquest', 'https://fortresscrafte.fandom.com/wiki/Special:Community', 'https://fortresscrafte.fandom.com/wiki/Survival', 'https://fortresscrafte.fandom.com/wiki/Special:AllMaps', 'https://www.fandom.com/topics/anime', 'https://club57.fandom.com/wiki/Club_57_Wiki', 'https://community.fandom.com/wiki/Help:Contents', 'https://fortresscrafte.fandom.comlink_url', 'https://www.fandom.com/privacy-policy', 'https://bit.ly/TikTokFandom', 'https://fortresscrafte.fandom.com/wiki/FortressCraft_Evolved_Wiki', 'https://fortresscrafte.fandom.com/wiki/Forum:Index', 'https://fortresscrafte.fandom.com/wiki/ARTHER', 'https://static.wikia.nocookie.net/fortresscrafte/images/2/2f/Charged_Lithium_Coils.png/revision/latest?cb=20180429052414', 'https://auth.fandom.com/signin?redirect=https%3A%2F%2Ffortresscrafte.fandom.com%2Fwiki%2FCargo_Lift_Controller', 'https://www.muthead.com/'}
        self.assertSetEqual(wiki.get_links(page, url), links)

    def test_get_images(self):
        page = BeautifulSoup(self.TEST_PAGE.read_text(), 'html.parser')
        images = {'https://static.wikia.nocookie.net/fortresscrafte/images/e/e6/Site-logo.png/revision/latest?cb=20210713163518': {'Site-logo.png'}, 'https://static.wikia.nocookie.net/fortresscrafte/images/f/fe/Cargo_Lift_Controller.png/revision/latest?cb=20180804002939': {'Cargo_Lift_Controller.png'}, 'https://static.wikia.nocookie.net/fortresscrafte/images/f/fc/Iron_Gear.png/revision/latest/scale-to-width-down/32?cb=20160721235534': {'Iron_Gear.png'}, 'https://static.wikia.nocookie.net/fortresscrafte/images/4/43/Copper_Wire.png/revision/latest/scale-to-width-down/32?cb=20160721234453': {'Copper_Wire.png'}, 'https://static.wikia.nocookie.net/fortresscrafte/images/2/2f/Charged_Lithium_Coils.png/revision/latest/scale-to-width-down/32?cb=20180429052414': {'Charged_Lithium_Coils.png'}, 'https://static.wikia.nocookie.net/fortresscrafte/images/2/27/Cargo-lift-1.jpg/revision/latest?cb=20160711213019': {'Cargo-lift-1.jpg'}}
        self.assertDictEqual(wiki.get_images(page), images)

    def get_page(self, url: str) -> BeautifulSoup:
        print(f'Visiting page: "{url}"')
        if url in self.visited:
            self.fail()
        self.visited.add(url)
        return BeautifulSoup(self.TEST_PAGE.read_text(), 'html.parser')

    def test_scrap(self):
        self.visited = set()
        page = BeautifulSoup(self.TEST_PAGE.read_text(), 'html.parser')
        self.assertDictEqual(wiki.scrap_images(wiki.DEFAULT_WIKI_URL, get_page=self.get_page), wiki.get_images(page))
        self.assertEqual(len(self.visited), 13)


if __name__ == '__main__':
    unittest.main()
