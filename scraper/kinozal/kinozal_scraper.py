import re
from urllib.parse import urlsplit, parse_qs
import urllib.parse
from ..episodes_scraper import EpisodesScraper
import aiohttp
import re
import collections
from lxml import html
from lxml.etree import tostring


class KinozalScraper(EpisodesScraper):
    def __init__(self, host: str) -> None:
        """
        :param host: full host address, including proto and port.
        Example:
        """
        self.host = host if re.match(r'\w+://', host) else 'http://' + host

    def search_list_url(self, search_string: str, page: int):
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

    def details_url(self, link: str):
        """
        Url of the movie details.
        :param link: relative link from search results list
        :return: url
        """
        return urllib.parse.urljoin(
                self.host,
                link
            )

    async def list_page(self, search_string: str) -> collections.AsyncIterable:
        """
        Iterate search result pages
        :param search_string: string to search
        :return: string with html of search result page
        """
        async with aiohttp.ClientSession() as session:
            page = 1
            while True:
                response = await session.get(self.search_list_url(search_string, page))
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
        FIELDS = {
            'audio': 'Аудио',
            'name': 'Название',
            'quality': 'Качество',
            'subtitles': 'Субтитры'
        }

        movie = {}
        tree = html.fromstring(page_html)
        details = tostring(tree.xpath('.//div[contains(@class, "content")]//div[@id="tabs"]')[0], encoding=str)
        for field in FIELDS:
            if FIELDS[field] in details:
                movie[field] = re.search(rf'{FIELDS[field]}:[^>]+>([^<]+)', details).group(1).strip()

        movie['has_english_subtitles'] = 'subtitles' in movie and 'нглийские' in movie['subtitles']
        movie['has_english_audio'] = 'audio' in movie and 'нглийский' in movie['audio']
        return movie

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
                    try:
                        first_season = title_match.group(2)
                        movie['last_season'] = int(title_match.group(3))
                        movie['last_episode'] = int(title_match.group(7))
                        if not first_season:
                            first_season = movie['last_season']
                        movie['seasons'] = list(range(int(first_season), movie['last_season'] + 1))
                    except ValueError:
                        pass  # just suppress the exception and do not return fields that we could not convert
                download_link_parsed = urllib.parse.urlparse('http://dl.kinozal.tv/download.php')._replace(
                    query=details_link_parsed.query
                )
                movie['torrent_link'] = urllib.parse.urlunparse(download_link_parsed)
                yield movie

    async def details(self, link: str) -> dict:
        async with aiohttp.ClientSession() as session:
            response = await session.get(self.details_url(link))
            if response.status != 200:
                return {}
            return self.extract_details(await response.text())

    async def episodes(self, search_string: str) -> collections.AsyncIterable:
        """
        Extracts episode data from list in search results.
        Downloads the search result pages.
        For more data you have to download details with routine episode_detail
        :param search_string:
        :return: dicts with the episodes data
        """
        async for page_html in self.list_page(search_string):
            for movie in self.extract_episode(page_html):
                yield movie

    async def find_episodes(self, search_string: str, season: int, min_episode: int) -> collections.AsyncIterable:
        """
        Loads all torrents that contain the season with minimum min_episode in them.
        Downloads details for them.
        :param search_string:
        :param season:
        :param min_episode:
        :return: dicts with the episodes data
        """
        async for page_html in self.list_page(search_string):
            for movie in self.extract_episode(page_html):
                if 'seasons' in movie and season in movie['seasons'] and 'last_episode' in movie and min_episode <= movie['last_episode']:
                    movie.update(await self.details(movie['details_link']))
                    yield movie
