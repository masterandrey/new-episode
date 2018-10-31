from django.db import models


class MovieList(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


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
    user = models.CharField(max_length=50)
    list = models.ForeignKey(MovieList, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title


class SearchString(models.Model):
    search_string = models.CharField(max_length=200)
    list = models.ForeignKey(MovieList, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.search_string


