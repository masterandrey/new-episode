from django.urls import path

from . import views

urlpatterns = [
    path('lists', views.lists, name='lists'),
    path('progress', views.progress, name='progress'),
    path('list_movies/<int:list_id>', views.list_movies, name='list_movies'),
    path('movie/<int:movie_id>', views.details, name='details'),
]