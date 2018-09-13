from django.contrib import admin

from .models import Movie, MovieList
from django_celery_results.models import TaskResult

admin.site.register(Movie)
admin.site.register(MovieList)
#admin.site.register(TaskResult)
