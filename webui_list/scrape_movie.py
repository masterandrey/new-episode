from scraper.kinozal.kinozal_scraper import scrape
from webui_list.models import Movie

def scrape_movie():
    def check_func(movie):
        """
        :param movie: fetched from list movie (without details)
        :return: True if we need it and have to load details
        """
        #todo check if we already have movie with such an id and return False to prevent
        #scraping it again
        #todo check movie['seasons'], movie['last_episode']
        return True

    for scraped_movie in scrape('Better Call Saul', check_func):
        movie = Movie(**scraped_movie)
        movie.save()
