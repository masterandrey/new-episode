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
import aiohttp


async def list_handler(request):
    params = request.rel_url.query
    page = int(params['page'])
    if page > 3:
        raise Exception('No more list pages')
    response = aiohttp_jinja2.render_template(f'better_call_saul_{page}.html',
                                              request,
                                              {})
    response.headers['Content-Language'] = 'ru'
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    return response


async def details_handler(request):
    params = request.rel_url.query
    id = int(params['id'])
    card_num = id // 5 + 1
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


@pytest.mark.skip
@given(page=st.integers(min_value=1, max_value=1000))
def test_kinozal_url(host, search_string, page):
    s = KinozalScraper(host)
    page_url = s.page_url(search_string, page)
    parsed_url = urllib.parse.urlparse(page_url)
    assert parsed_url.scheme == '' or parsed_url.scheme.startswith('http')
    #assert parsed_url.netloc - could be empty or localhost, or example.com, no feasible way to test
    assert parsed_url.path == '/browse.php'
    assert 's=' in parsed_url.query
    assert 'q=0' in parsed_url.query
    assert f'page={page}' in parsed_url.query
    assert search_string in itertools.chain.from_iterable(urllib.parse.parse_qsl(parsed_url.query))


class TestScraping(AioHTTPTestCase):
    async def get_application(self):
        return aioapp()

    async def get_server(self, app):
        return TestServer(app, loop=self.loop, host='127.0.0.1', port=4433)

    @pytest.mark.skip
    @unittest_run_loop
    async def test_list_page(self):
        scraper = KinozalScraper('localhost:4433')
        page_count = 0
        async for _ in scraper.list_page(search_string):
            page_count += 1
        assert page_count == 3, 'Test web-server returns exactly three pages with search results'

    def test_extract_episode(self):
        scraper = KinozalScraper('localhost:4433')
        page_html = open('test/better_call_saul_1.html', 'r').read()
        movies_count = 0
        for movie in scraper.extract_episode(page_html):
            movies_count += 1
            if movies_count == 2:
                assert movie['title'] == 'Лучше звоните Солу (4 сезон: 1-10 серии из 10) / Better Call Saul / 2018 / ПД (Кубик в Кубе) / WEBRip (720p)'
                assert movie['details_link'] == '/details.php?id=1638000'
                assert movie['seeds_num'] == '15'
                assert movie['size'] == 2
                assert movie['id'] == 'ktv_1638000'
                assert movie['last_season'] == 4
                assert movie['last_episode'] == 10
                assert movie['seasons'] == [4]
        assert movies_count == 50

    @unittest_run_loop
    async def test_episodes(self):
        scraper = KinozalScraper('localhost:4433')
        movies_count = 0
        async for movie in scraper.episodes(search_string):
            movies_count += 1
            if movies_count == 130:
                assert movie['title'] == 'Лучше звоните Солу (1 сезон: 1-10 серии из 10) / Better Call Saul  / 2015 / ЛО (Kerob) / WEB-DLRip'
                assert movie['details_link'] == '/details.php?id=1307895'
                assert movie['seeds_num'] == '0'
                assert movie['size'] == 9
                assert movie['id'] == 'ktv_1307895'
                assert movie['last_season'] == 1
                assert movie['last_episode'] == 10
                assert movie['seasons'] == [1]
            if movies_count == 86:
                assert movie['title'] == 'Лучше звоните Солу (1-2 сезон) / Better Call Saul (Unofficial) / Soundtrack / 2015-2016 / MP3'
                assert movie['details_link'] == '/details.php?id=1453060'
                assert movie['seeds_num'] == '0'
                assert movie['size'] == 3
                assert movie['id'] == 'ktv_1453060'
        assert movies_count == 130

    def test_extract_details(self):
        scraper = KinozalScraper('localhost:4433')
        page_html = open('test/better_call_saul_card_1.html', 'r').read()
        movie = scraper.extract_details(page_html)


def run_fake_web_server():
    web.run_app(aioapp(), host='127.0.0.1', port=4433)


if __name__ == '__main__':
    run_fake_web_server()

