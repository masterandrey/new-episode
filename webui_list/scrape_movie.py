from scraper.kinozal.scrape import scrape
from webui_list.models import Movie

def scrape_movie():
    for scraped_movie in scrape('Better Call Saul'):
        movie = Movie(**scraped_movie)
        movie.save()
