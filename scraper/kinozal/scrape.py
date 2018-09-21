import scrapy
from scrapy.loader.processors import Join, MapCompose, TakeFirst
from scrapy.selector import Selector
from scrapy.loader import ItemLoader
import re
from urllib.parse import urlsplit, parse_qs
import urllib.parse


KINOZAL_ID_PREFIX = 'ktv_'  # Prefix to uniqualize movies ids from different scraping sources


def size_processor(size_str):
    MULT = {
        ' МБ': 10 ** 6,
        ' ГБ': 10**9,
    }
    for mult in MULT:
        if size_str.endswith(mult):
            return int(float(size_str[:-len(mult)]) * MULT[mult])
    return int(size_str)


def scrape(search_string, check_func):
    """

    :param search_string:
    :param check_func: get fetched from list movie and decides if we need it and have to load details
    :return:
    """
    def extract_tech_field(details_selector, title):
        return re.search(rf'{title}:[^>]+>([^<]+)', details_selector.css('div.bx1').re(rf'.*{title}:.*')[0]).group(
            1).strip()

    for page in range(1):  # page number from 0
        url_parsed = urllib.parse.urlparse('http://kinozal.tv/browse.php')._replace(
            query=urllib.parse.urlencode({'s': search_string, 'q': 0, 'page': page})
        )
        url = urllib.parse.urlunparse(url_parsed)

        body = open('scraper/kinozal/list.html', 'r', encoding='CP1251').read()
        movies_selector = Selector(text=body).css('table.t_peer')
        for movie_selector in movies_selector.xpath('//tr'):
            if movie_selector.css('td.s::text').extract():
                movie = {}
                title_cell = movie_selector.xpath('.//td[@class="nam"]/a')
                movie['title'] = title_cell.xpath('.//text()').extract_first()
                movie['details_link'] = title_cell.xpath('.//@href').extract_first()
                movie['seeds_num'] = movie_selector.xpath('.//td[@class="sl_s"]/text()').extract_first()
                movie['size'] = size_processor(movie_selector.xpath('.//td[@class="s"]/text()').extract_first())

                details_link_parsed = urllib.parse.urlparse(movie['details_link'])
                movie['id'] = KINOZAL_ID_PREFIX + parse_qs(details_link_parsed.query)['id'][0]
                title_match = re.search(r'((\d+)-)?(\d+) сезон: ((\d+)-)?(\d+) сери(и|я) из (\d+)', movie['title'])
                if not title_match:
                    print('Cannot parse title ', movie['title'])
                    continue
                first_season = title_match.group(2)
                movie['last_season'] = int(title_match.group(3))
                movie['last_episode'] = int(title_match.group(6))
                if not first_season:
                    first_season = movie['last_season']
                movie['seasons'] = list(range(int(first_season), movie['last_season'] + 1))

                if check_func(movie):
                    details = open('scraper/kinozal/details.html', 'r', encoding='CP1251').read()
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
