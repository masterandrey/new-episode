"""
If run as script serve as fake web-server with materials to scrape
"""
from aiohttp import web
import mimetypes
import aiohttp_jinja2
import jinja2
from hypothesis import given
from hypothesis import strategies as st
from scraper.kinozal.kinozal_scraper import KinozalScraper
import urllib.parse
import pytest
import itertools
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop, TestServer
from aiohttp.web import HTTPNotFound
import logging
import time


skip_all = False # True  # to run specific test we just skip all other tests

logging.basicConfig(filename='test_scraping.log', level=logging.DEBUG)
TEST_SERVER_PORT=4434  # differs from production so we can run tests and production at the same machine simultaniously


async def list_handler(request):
    """
    Test web server.
    Returns 3 pages of search result (does not depends on the actual search string)
    :param request:
    :return:
    """
    params = request.rel_url.query
    page = int(params['page'])
    if page > 3:
        raise HTTPNotFound()
    response = aiohttp_jinja2.render_template(f'better_call_saul_{page}.html',
                                              request,
                                              {})
    response.headers['Content-Language'] = 'ru'
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    return response


async def details_handler(request):
    """
    Test web server.
    For any movie details page request returns one of the 5 predefined pages.
    """
    params = request.rel_url.query
    id = int(params['id'])
    card_num = id % 5 + 1
    response = aiohttp_jinja2.render_template(f'better_call_saul_card_{card_num}.html',
                                              request,
                                              {})
    response.headers['Content-Language'] = 'ru'
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    return response


def aioapp():
    app = web.Application()
    # app.router.add_static('/', 'scraper/kinozal', name='static', )
    app.router.add_get('/browse.php', list_handler)
    app.router.add_get('/details.php', details_handler)

    mimetypes.init()
    mimetypes.types_map['.php'] = 'text/html; charset=windows-1251'

    aiohttp_jinja2.setup(app,
                         loader=jinja2.FileSystemLoader('test'))
    return app


@pytest.fixture(params=['localhost', 'example.com', 'http://my.domain.com/'])
def host(request):
    return request.param


@pytest.fixture(params=['Better Call Saul', 'Лучше позвать Сола', 'h834687564325435%$^^%$$^%32sdgvD'])
def search_string(request):
    return request.param


@pytest.mark.skipif(skip_all, reason='Do not test this case')
@given(page=st.integers(min_value=1, max_value=1000))
def test_kinozal_url(host, search_string, page):
    s = KinozalScraper(host)
    page_url = s.search_list_url(search_string, page)
    parsed_url = urllib.parse.urlparse(page_url)
    assert parsed_url.scheme == '' or parsed_url.scheme.startswith('http')
    #assert parsed_url.netloc - could be empty or localhost, or example.com, no feasible way to test
    assert parsed_url.path == '/browse.php'
    assert 's=' in parsed_url.query
    assert 'q=0' in parsed_url.query
    assert f'page={page}' in parsed_url.query
    assert search_string in itertools.chain.from_iterable(urllib.parse.parse_qsl(parsed_url.query))


@pytest.mark.skipif(skip_all, reason='Do not test this case')
@given(id=st.integers(min_value=100000, max_value=10000000))
def test_details_url(host, id):
    s = KinozalScraper(host)
    page_url = s.details_url(f'details.php?id={id}')
    parsed_url = urllib.parse.urlparse(page_url)
    assert parsed_url.scheme == '' or parsed_url.scheme.startswith('http')
    #assert parsed_url.netloc - could be empty or localhost, or example.com, no feasible way to test
    assert parsed_url.path == '/details.php'

@pytest.mark.skipif(skip_all, reason='Do not test this case')
def test_extract_episode():
    scraper = KinozalScraper(f'localhost:{TEST_SERVER_PORT}', max_not_a_robot_delay=0)
    page_html = open('test/better_call_saul_1.html', 'r').read()
    movies_count = 0
    for movie in scraper.extract_episode(page_html, 'fake_url'):
        movies_count += 1
        if movies_count == 2:
            assert movie['title'] == 'Лучше звоните Солу (4 сезон: 1-10 серии из 10) / Better Call Saul / 2018 / ПД (Кубик в Кубе) / WEBRip (720p)'
            assert movie['details_link'] == '/details.php?id=1638000'
            assert movie['seeds_num'] == '15'
            assert movie['size'] == 15190000000
            assert movie['id'] == 'ktv_1638000'
            assert movie['last_season'] == 4
            assert movie['last_episode'] == 10
            assert movie['seasons'] == [4]
            assert movie['torrent_link'] == 'http://dl.kinozal.tv/download.php?id=1638000'
    assert movies_count == 50


@pytest.mark.skipif(skip_all, reason='Do not test this case')
def test_extract_details():
    scraper = KinozalScraper('localhost:4433', max_not_a_robot_delay=0)
    page_html = open('test/better_call_saul_card_1.html', 'r').read()
    movie = scraper.extract_details(page_html)
    assert movie['audio'] == 'Русский (AC3, 6 ch, 640 Кбит/с), английский (E-AC3, 6 ch, 640 Кбит/с)'
    assert movie['quality'] == 'WEBRip ( 2160p)'
    assert movie['subtitles'] == 'Русские, английские'
    assert movie['has_english_subtitles'] == True
    assert movie['has_english_audio'] == True


class TestScrapingAsync(AioHTTPTestCase):
    async def get_application(self):
        return aioapp()

    async def get_server(self, app):
        return TestServer(app, loop=self.loop, host='127.0.0.1', port=TEST_SERVER_PORT)

    """
    aiohttp test case is not pytest, but unittest. 
    So we have to replace pytest fixtures
    """
    search_string = 'Better Call Saul'

    @pytest.mark.skipif(skip_all, reason='Do not test this case')
    @unittest_run_loop
    async def test_i_am_not_a_robot_delay(self):
        scraper = KinozalScraper(f'localhost:{TEST_SERVER_PORT}')
        start = time.time()
        await scraper.i_am_not_a_robot_delay()
        assert time.time() - start > 0.009


    @pytest.mark.skipif(skip_all, reason='Do not test this case')
    @unittest_run_loop
    async def test_list_page(self):
        scraper = KinozalScraper(f'localhost:{TEST_SERVER_PORT}', max_not_a_robot_delay=0)
        page_count = 0
        async for _ in scraper.list_page(self.search_string):
            page_count += 1
        assert page_count == 3, 'Test web-server returns exactly three pages with search results'

    @pytest.mark.skipif(skip_all, reason='Do not test this case')
    @unittest_run_loop
    async def test_episodes(self):
        scraper = KinozalScraper(f'localhost:{TEST_SERVER_PORT}', max_not_a_robot_delay=0)
        movies_count = 0
        async for movie in scraper.episodes(self.search_string):
            movies_count += 1
            if movies_count == 130:
                assert movie['title'] == 'Лучше звоните Солу (1 сезон: 1-10 серии из 10) / Better Call Saul  / 2015 / ЛО (Kerob) / WEB-DLRip'
                assert movie['details_link'] == '/details.php?id=1307895'
                assert movie['seeds_num'] == '0'
                assert movie['size'] == 4110000000
                assert movie['id'] == 'ktv_1307895'
                assert movie['last_season'] == 1
                assert movie['last_episode'] == 10
                assert movie['seasons'] == [1]
            if movies_count == 86:
                assert movie['title'] == 'Лучше звоните Солу (1-2 сезон) / Better Call Saul (Unofficial) / Soundtrack / 2015-2016 / MP3'
                assert movie['details_link'] == '/details.php?id=1453060'
                assert movie['seeds_num'] == '0'
                assert movie['size'] == 637000000
                assert movie['id'] == 'ktv_1453060'
        assert movies_count == 130

    @pytest.mark.skipif(skip_all, reason='Do not test this case')
    @unittest_run_loop
    async def test_details(self):
        scraper = KinozalScraper(f'localhost:{TEST_SERVER_PORT}', max_not_a_robot_delay=0)
        movie = await scraper.details('/details.php?id=1534654')
        assert movie['audio'] == 'AC3, 2 ch, 192 Кбит/с'
        assert movie['has_english_subtitles'] == False

    @pytest.mark.skipif(skip_all, reason='Do not test this case')
    @unittest_run_loop
    async def test_find_episodes(self):
        scraper = KinozalScraper(f'localhost:{TEST_SERVER_PORT}', max_not_a_robot_delay=0)
        movies_count = 0
        async for movie in scraper.find_episodes(self.search_string, season=3, min_episode=9):
            movies_count += 1
        assert movies_count == 36

def run_fake_web_server():
    web.run_app(aioapp(), host='127.0.0.1', port=4433)  # the same port as for production for integration tests


if __name__ == '__main__':
    run_fake_web_server()

