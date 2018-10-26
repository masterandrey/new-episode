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


async def list_handler(request):
    context = {}
    response = aiohttp_jinja2.render_template('browse.php',
                                              request,
                                              context)
    response.headers['Content-Language'] = 'ru'
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    print('served!!')
    return response


def aioapp():
    app = web.Application()
    # app.router.add_static('/', 'scraper/kinozal', name='static', )
    app.router.add_get('/browse.php', list_handler)

    mimetypes.init()
    mimetypes.types_map['.php'] = 'text/html; charset=windows-1251'

    aiohttp_jinja2.setup(app,
                         loader=jinja2.FileSystemLoader('scraper/kinozal'))
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


async def test_list_page(aiohttp_server):
    server = await aiohttp_server(aioapp(), host='127.0.0.1', port=4433)
    s = KinozalScraper('localhost:4433')
    async for page in s.list_page(search_string):
        print(page)


def run_fake_web_server():
    web.run_app(aioapp(), host='127.0.0.1', port=4433)


if __name__ == '__main__':
    run_fake_web_server()

