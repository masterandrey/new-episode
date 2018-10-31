from django.http import HttpResponse
from webui_list.scrape_movie import scrape_movie
import logging
import asyncio
from .models import MovieList, Movie
from django.template import loader


logger = logging.getLogger(__name__)


def lists(request):
    #logger.error('from view')
    # #loop = asyncio.get_event_loop()
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    # loop.run_until_complete(asyncio.wait([scrape_movie()]))
    # loop.close()
    # return HttpResponse("Hello: ")
    movie_list = MovieList.objects.order_by('name')[:35]  # .filter(user=request.user)
    template = loader.get_template('lists.html')
    context = {
        'movie_list': movie_list,
    }
    return HttpResponse(template.render(context, request))


def progress(request):
    template = loader.get_template('progress.html')
    context = {
    }
    return HttpResponse(template.render(context, request))


def list_movies(request, list_id):
    """
    List of movies in the movies list
    :param request:
    :return:
    """
    #logger.error('from view')
    # #loop = asyncio.get_event_loop()
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    # loop.run_until_complete(asyncio.wait([scrape_movie()]))
    # loop.close()
    # return HttpResponse("Hello: ")
    list_movies = Movie.objects.filter(list=list_id).order_by('title')[:35]  # .filter(user=request.user)
    template = loader.get_template('list_movies.html')
    context = {
        'list_movies': list_movies,
    }
    return HttpResponse(template.render(context, request))


def details(request, movie_id):
    return HttpResponse(f'details of movie id={movie_id}')

