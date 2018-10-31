from scraper.kinozal.kinozal_scraper import KinozalScraper
from webui_list.models import Movie


async def scrape_movie():
    scraper = KinozalScraper('localhost:4433')
    async for scraped_movie in scraper.find_episodes('Better Call Saul', 1, 1):
        movie = Movie(**scraped_movie)
        movie.save()
