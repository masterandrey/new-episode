import re
from urllib.parse import urlsplit, parse_qs
import urllib.parse
from ..episodes_scraper import EpisodesScraper
import aiohttp
import re
import collections
from lxml import html


class KinozalScraper(EpisodesScraper):
    def __init__(self, host: str) -> None:
        """
        :param host: full host address, including proto and port.
        Example:
        """
        self.host = host if re.match(r'\w+://', host) else 'http://' + host

    def page_url(self, search_string: str, page: int):
        """
        Url of search result page
        :param search_string: string to search
        :param page: page number starting from 1
        :return: url
        """
        url_parsed = urllib.parse.urlparse(
            urllib.parse.urljoin(
                self.host,
                'browse.php'
            )
        )
        url_parsed = url_parsed._replace(
                query=urllib.parse.urlencode({
                    's': search_string,
                    'q': 0,
                    'page': page
                    })
                )
        return urllib.parse.urlunparse(url_parsed)

    async def list_page(self, search_string: str) -> collections.AsyncIterable:
        """
        Iterate search result pages
        :param search_string: string to search
        :return: string with html of search result page
        """
        headers = {}
        async with aiohttp.ClientSession(headers=headers) as session:
            page = 1
            while True:
                response = await session.get(self.page_url(search_string, page))
                if response.status != 200:
                    break
                yield await response.text()
                page += 1

    @staticmethod
    def extract_details(page_html) -> dict:
        """
        Extracts episode details from detail page
        :param page_html:
        :return:
        """
        def extract_tech_field(details_selector, title):
            return re.search(rf'{title}:[^>]+>([^<]+)', details_selector.css('div.bx1').re(rf'.*{title}:.*')[0]).group(
                1).strip()

        tree = html.fromstring(page_html)
        details_selector = Selector(text=details).css('div.content')
        movie['audio'] = extract_tech_field(details_selector, 'Аудио')
        movie['name'] = extract_tech_field(details_selector, 'Название')
        movie['quality'] = extract_tech_field(details_selector, 'Качество')
        movie['subtitles'] = extract_tech_field(details_selector, 'Субтитры')
        movie['has_english_subtitles'] = 'нглийские' in movie['subtitles']
        movie['has_english_audio'] = 'нглийский' in movie['audio']
        download_link_parsed = urllib.parse.urlparse('http://dl.kinozal.tv/download.php')._replace(
            query=details_link_parsed.query
        )
        movie['torrent_link'] = urllib.parse.urlunparse(download_link_parsed)
        yield movie

    @staticmethod
    def extract_episode(page_html) -> collections.Iterable:
        """
        Extracts episode data from search result page.
        :param search_string:
        :return: dict with extracted episode data
        """
        KINOZAL_ID_PREFIX = 'ktv_'  # Prefix to uniqualize movies ids from different scraping sources

        def size_processor(size_str):
            MULT = {
                ' МБ': 10 ** 6,
                ' ГБ': 10 ** 9,
            }
            for mult in MULT:
                if size_str.endswith(mult):
                    return int(float(size_str[:-len(mult)]) * MULT[mult])
            return int(size_str)

        tree = html.fromstring(page_html)
        movies_selector = tree.xpath('.//table[contains(@class, "t_peer")]/tr')
        for movie_selector in movies_selector:
            has_data_cells = movie_selector.xpath('.//td[@class="s"]/text()')
            if has_data_cells:
                movie = {}
                title_cell_xpath = './/td[@class="nam"]/a'
                movie['title'] = movie_selector.xpath(title_cell_xpath + '/text()')[0]
                movie['details_link'] = movie_selector.xpath(title_cell_xpath + '/@href')[0]
                movie['seeds_num'] = movie_selector.xpath('.//td[@class="sl_s"]/text()')[0]
                movie['size'] = size_processor(movie_selector.xpath('.//td[@class="s"]/text()')[0])
                details_link_parsed = urllib.parse.urlparse(movie['details_link'])
                movie['id'] = KINOZAL_ID_PREFIX + parse_qs(details_link_parsed.query)['id'][0]
                title_match = re.search(r'((\d+)-)?(\d+) сезон(ы)?: ((\d+)-)?(\d+) +сери(и|я) из (\d+)', movie['title'])
                #assert title_match, f'Cannot parse title {movie["title"]}'
                if title_match:
                    first_season = title_match.group(2)
                    movie['last_season'] = int(title_match.group(3))
                    movie['last_episode'] = int(title_match.group(7))
                    if not first_season:
                        first_season = movie['last_season']
                    movie['seasons'] = list(range(int(first_season), movie['last_season'] + 1))
                yield movie

    async def episodes(self, search_string: str) -> collections.AsyncIterable:
        """
        Extracts episode data from list in search results.
        Downloads the search result pages.
        For more data you have to download details with routine episode_detail
        :param search_string:
        :return: dict with extracted episode data
        """
        async for page_html in self.list_page(search_string):
            for movie in self.extract_episode(page_html):
                yield movie