from django.db import models


class Movie(models.Model):
    title = models.CharField(max_length=200)
    seeds_num = models.IntegerField()
    size = models.IntegerField()
    details_link = models.CharField(max_length=200)
    seasons = models.CharField(max_length=200)
    last_season = models.IntegerField()
    audio = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    quality = models.CharField(max_length=200)
    original_name = models.CharField(max_length=200)
    last_episode = models.IntegerField()
    subtitles = models.CharField(max_length=200)
    has_english_subtitles = models.BooleanField(default=False)
    has_english_audio = models.BooleanField(default=False)
    torrent_link = models.CharField(max_length=200)
    id = models.CharField(max_length=32, primary_key=True)

    def __str__(self):
        return self.title


class MovieList(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    search_string = models.CharField(max_length=200)

    def __str__(self):
        return self.search_string
