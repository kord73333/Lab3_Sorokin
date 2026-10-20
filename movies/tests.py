import json
import os
import shutil
import tempfile

from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Movie
from .services import DuplicateMovieError, save_movie_to_db


class MovieDataDirMixin:
    """Изолирует каталог файлов данных во временной папке на время теста."""

    def setUp(self):
        super().setUp()
        self._temp_data_dir = tempfile.mkdtemp(prefix='movies_test_')
        self._override = override_settings(DATA_DIR=self._temp_data_dir)
        self._override.enable()
        self.addCleanup(self._cleanup_data_dir)

    def _cleanup_data_dir(self):
        self._override.disable()
        shutil.rmtree(self._temp_data_dir, ignore_errors=True)

    def list_data_files(self):
        return sorted(os.listdir(self._temp_data_dir))


class AddMovieDBTests(MovieDataDirMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('add_movie')
        self.payload = {
            'title': 'Матрица',
            'director': 'Вачowski',
            'year': 1999,
            'genre': 'Фантастика',
            'rating': 8.7,
            'save_target': 'db',
        }

    def test_saves_to_database(self):
        response = self.client.post(self.url, self.payload)
        self.assertRedirects(response, self.url)
        self.assertEqual(Movie.objects.count(), 1)
        movie = Movie.objects.first()
        self.assertEqual(movie.title, 'Матрица')
        self.assertEqual(movie.year, 1999)

    def test_saves_nothing_to_files(self):
        self.client.post(self.url, self.payload)
        self.assertEqual(self.list_data_files(), [])

    def test_duplicate_is_not_saved(self):
        self.client.post(self.url, self.payload)
        response = self.client.post(self.url, self.payload, follow=True)
        self.assertEqual(Movie.objects.count(), 1)
        content = response.content.decode('utf-8')
        self.assertIn('уже есть в базе данных', content)

    def test_invalid_year_not_saved(self):
        payload = dict(self.payload, year=1500)
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Movie.objects.count(), 0)
        self.assertContains(response, 'Год должен быть между 1888 и 2100')

    def test_duplicate_different_director_is_saved(self):
        self.client.post(self.url, self.payload)
        second = dict(self.payload, director='Другой', title='Матрица', year=1999)
        self.client.post(self.url, second)
        self.assertEqual(Movie.objects.count(), 2)


class AddMovieFileTests(MovieDataDirMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('add_movie')
        self.payload = {
            'title': 'Начало',
            'director': 'Кристофер Нолан',
            'year': 2010,
            'genre': 'Триллер',
            'rating': 8.8,
            'save_target': 'file',
        }

    def test_saves_json_file(self):
        self.client.post(self.url, dict(self.payload, file_format='json'))
        files = self.list_data_files()
        self.assertEqual(len(files), 1)
        self.assertTrue(files[0].endswith('.json'))
        with open(os.path.join(self._temp_data_dir, files[0]), encoding='utf-8') as f:
            data = json.load(f)
        self.assertEqual(data['title'], 'Начало')

    def test_saves_xml_file(self):
        self.client.post(self.url, dict(self.payload, file_format='xml'))
        files = self.list_data_files()
        self.assertEqual(len(files), 1)
        self.assertTrue(files[0].endswith('.xml'))

    def test_nothing_saved_to_database(self):
        self.client.post(self.url, dict(self.payload, file_format='json'))
        self.assertEqual(Movie.objects.count(), 0)


class MovieSearchAjaxTests(TestCase):
    def setUp(self):
        self.url = reverse('movie_search')
        Movie.objects.create(
            title='Матрица', director='Вачовски', year=1999,
            genre='Фантастика', rating=8.7,
        )
        Movie.objects.create(
            title='Начало', director='Нолан', year=2010,
            genre='Триллер', rating=8.8,
        )

    def test_search_by_title(self):
        response = self.client.get(self.url, {'q': 'Матриц'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['results'][0]['title'], 'Матрица')

    def test_search_by_director_and_genre(self):
        self.assertEqual(
            self.client.get(self.url, {'q': 'Нолан'}).json()['count'], 1
        )
        self.assertEqual(
            self.client.get(self.url, {'q': 'Фантаст'}).json()['count'], 1
        )

    def test_search_empty_returns_all(self):
        self.assertEqual(self.client.get(self.url).json()['count'], 2)

    def test_search_no_match(self):
        response = self.client.get(self.url, {'q': 'нетакого'})
        self.assertEqual(response.json()['count'], 0)
        self.assertEqual(response.json()['results'], [])


class MovieEditDeleteTests(TestCase):
    def setUp(self):
        self.movie = Movie.objects.create(
            title='Интерстеллар', director='Нолан', year=2014,
            genre='Фантастика', rating=8.6,
        )

    def test_edit_updates_record(self):
        url = reverse('movie_edit', args=[self.movie.pk])
        response = self.client.post(url, {
            'title': 'Интерстеллар',
            'director': 'Кристофер Нолан',
            'year': 2014,
            'genre': 'Фантастика',
            'rating': 9.0,
        })
        self.assertEqual(response.status_code, 302)
        self.movie.refresh_from_db()
        self.assertEqual(self.movie.director, 'Кристофер Нолан')
        self.assertEqual(self.movie.rating, 9.0)

    def test_edit_invalid_rating_rejected(self):
        url = reverse('movie_edit', args=[self.movie.pk])
        response = self.client.post(url, {
            'title': 'Интерстеллар',
            'director': 'Нолан',
            'year': 2014,
            'genre': 'Фантастика',
            'rating': 99,
        })
        self.assertEqual(response.status_code, 200)
        self.movie.refresh_from_db()
        self.assertEqual(self.movie.rating, 8.6)
        self.assertContains(response, 'Рейтинг должен быть от 0 до 10')

    def test_edit_to_duplicate_rejected(self):
        Movie.objects.create(
            title='Дюна', director='Вильнёв', year=2021,
            genre='Фантастика', rating=8.0,
        )
        url = reverse('movie_edit', args=[self.movie.pk])
        response = self.client.post(url, {
            'title': 'Дюна',
            'director': 'Вильнёв',
            'year': 2021,
            'genre': 'Фантастика',
            'rating': 8.0,
        })
        self.assertEqual(response.status_code, 200)
        self.movie.refresh_from_db()
        self.assertEqual(self.movie.title, 'Интерстеллар')
        self.assertContains(response, 'уже есть в базе данных')

    def test_delete_removes_record(self):
        url = reverse('movie_delete', args=[self.movie.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Movie.objects.count(), 0)

    def test_delete_requires_post(self):
        url = reverse('movie_delete', args=[self.movie.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(Movie.objects.count(), 1)


class DataViewTests(MovieDataDirMixin, TestCase):
    def test_db_source_lists_movies(self):
        Movie.objects.create(
            title='Аватар', director='Кэмерон', year=2009,
            genre='Фантастика', rating=7.9,
        )
        response = self.client.get(reverse('data_view'), {'source': 'db'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Аватар')

    def test_files_source_renders(self):
        response = self.client.get(reverse('data_view'), {'source': 'files'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Файлов не найдено')

    def test_invalid_source_falls_back_to_db(self):
        response = self.client.get(reverse('data_view'), {'source': 'hack'})
        self.assertEqual(response.context['source'], 'db')


class MovieModelTests(TestCase):
    def test_str(self):
        movie = Movie(title='Тест', director='Режиссёр', year=2000,
                      genre='Жанр', rating=5.0)
        self.assertEqual(str(movie), 'Тест (2000)')

    def test_duplicate_via_model_raises(self):
        from django.db import IntegrityError

        Movie.objects.create(title='A', director='B', year=2000,
                             genre='G', rating=5.0)
        with self.assertRaises(IntegrityError):
            Movie.objects.create(title='A', director='B', year=2000,
                                 genre='G', rating=5.0)


class MovieServiceTests(TestCase):
    def test_save_movie_to_db_creates_record(self):
        movie = save_movie_to_db({
            'title': 'Три идиота', 'director': 'Хирани', 'year': 2009,
            'genre': 'Комедия', 'rating': 8.4,
        })
        self.assertEqual(movie.pk, Movie.objects.get().pk)

    def test_save_movie_to_db_raises_on_duplicate(self):
        data = {
            'title': 'Три идиота', 'director': 'Хирани', 'year': 2009,
            'genre': 'Комедия', 'rating': 8.4,
        }
        save_movie_to_db(data)
        with self.assertRaises(DuplicateMovieError):
            save_movie_to_db(data)
        self.assertEqual(Movie.objects.count(), 1)
