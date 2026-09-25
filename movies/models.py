from django.db import models


class Movie(models.Model):
    title = models.CharField('Название', max_length=200)
    director = models.CharField('Режиссёр', max_length=200)
    year = models.IntegerField('Год')
    genre = models.CharField('Жанр', max_length=100)
    rating = models.FloatField('Рейтинг')

    def __str__(self):
        return self.title