from django.db.models import Q

from .models import Movie


class DuplicateMovieError(Exception):

    def __init__(self, movie):
        self.movie = movie
        super().__init__('Дубликат фильма')


def find_duplicate(title, director, year):
    return Movie.objects.filter(
        title=title, director=director, year=year
    ).first()


def save_movie_to_db(data):
    duplicate = find_duplicate(data['title'], data['director'], data['year'])
    if duplicate is not None:
        raise DuplicateMovieError(duplicate)
    return Movie.objects.create(
        title=data['title'],
        director=data['director'],
        year=data['year'],
        genre=data['genre'],
        rating=data['rating'],
    )


def search_movies(query):
    queryset = Movie.objects.all()
    query = (query or '').strip()
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query)
            | Q(director__icontains=query)
            | Q(genre__icontains=query)
        )
    return queryset


def movie_to_dict(movie):
    return {
        'id': movie.id,
        'title': movie.title,
        'director': movie.director,
        'year': movie.year,
        'genre': movie.genre,
        'rating': movie.rating,
        'created_at': movie.created_at.strftime('%d.%m.%y %H:%M'),
    }
