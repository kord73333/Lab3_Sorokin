from django.db import models


class Movie(models.Model):

    title = models.CharField('Название', max_length=200)
    director = models.CharField('Режиссёр', max_length=200)
    year = models.IntegerField('Год')
    genre = models.CharField('Жанр', max_length=100)
    rating = models.FloatField('Рейтинг')
    created_at = models.DateTimeField('Дата добавления', auto_now_add=True)

    class Meta:
        verbose_name = 'Фильм'
        verbose_name_plural = 'Фильмы'
        ordering = ['-created_at', '-id']
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'director', 'year'],
                name='unique_movie_title_director_year',
                violation_error_message=(
                    'Такая запись уже есть в базе данных: фильм с таким '
                    'названием, режиссёром и годом уже существует.'
                ),
            ),
        ]

    def __str__(self):
        return f'{self.title} ({self.year})'
