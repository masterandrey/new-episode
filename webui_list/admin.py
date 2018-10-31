from django.contrib import admin

from .models import Movie, MovieList, SearchString

admin.site.register(Movie)
admin.site.register(MovieList)
admin.site.register(SearchString)
#admin.site.register(TaskResult)
