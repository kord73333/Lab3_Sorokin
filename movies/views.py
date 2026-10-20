import os

from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST

from .forms import MovieEditForm, MovieForm
from .models import Movie
from .services import (
    DuplicateMovieError,
    movie_to_dict,
    save_movie_to_db,
    search_movies,
)
from .utils import (
    sanitize_filename,
    save_movie_to_file,
    validate_json_file,
    validate_xml_file,
)

def _data_dir():
    return str(settings.DATA_DIR)


def _ensure_data_dir():
    os.makedirs(_data_dir(), exist_ok=True)


def index(request):
    return render(request, 'movies/index.html')


def add_movie(request):
    _ensure_data_dir()
    if request.method == 'POST':
        form = MovieForm(request.POST)
        if form.is_valid():
            data = {
                'title': form.cleaned_data['title'],
                'director': form.cleaned_data['director'],
                'year': form.cleaned_data['year'],
                'genre': form.cleaned_data['genre'],
                'rating': form.cleaned_data['rating'],
            }
            target = form.cleaned_data['save_target']
            if target == 'db':
                return _save_to_database(request, data)
            return _save_to_file(request, data, form.cleaned_data['file_format'])
    else:
        form = MovieForm()
    return render(request, 'movies/add_movie.html', {'form': form})


def _save_to_database(request, data):
    try:
        movie = save_movie_to_db(data)
    except DuplicateMovieError as error:
        messages.warning(
            request,
            f'Такая запись уже есть в базе данных: «{error.movie.title}» '
            f'({error.movie.director}, {error.movie.year}). Фильм не добавлен.',
        )
    else:
        messages.success(
            request,
            f'Фильм «{movie.title}» сохранён в базу данных (id={movie.id})',
        )
    return redirect('add_movie')


def _save_to_file(request, data, fmt):
    try:
        filename = save_movie_to_file(data, fmt, _data_dir())
    except OSError as error:
        messages.error(request, f'Не удалось сохранить файл: {error}')
    else:
        messages.success(
            request, f'Фильм сохранён в файл «{filename}» ({fmt.upper()})'
        )
    return redirect('add_movie')


def upload_file(request):
    _ensure_data_dir()
    if request.method == 'POST':
        uploaded = request.FILES.get('file')
        if not uploaded:
            messages.error(request, 'Файл не выбран')
            return redirect('upload_file')

        ext = os.path.splitext(uploaded.name)[1].lower()
        if ext not in ('.json', '.xml'):
            messages.error(request, 'Поддерживаются только файлы .json и .xml')
            return redirect('upload_file')

        safe_name = sanitize_filename(uploaded.name)
        path = os.path.join(_data_dir(), safe_name)

        with open(path, 'wb+') as dest:
            for chunk in uploaded.chunks():
                dest.write(chunk)

        if ext == '.json':
            ok, err, _ = validate_json_file(path)
        else:
            ok, err, _ = validate_xml_file(path)

        if not ok:
            os.remove(path)
            messages.error(
                request, f'Файл невалиден и был удалён. Причина: {err}'
            )
            return redirect('upload_file')

        messages.success(request, f'Файл «{safe_name}» успешно загружен')
        return redirect('list_files')

    return render(request, 'movies/upload.html')


def _read_files_data():
    _ensure_data_dir()
    files_data = []

    for name in sorted(os.listdir(_data_dir())):
        ext = os.path.splitext(name)[1].lower()
        if ext not in ('.json', '.xml'):
            continue

        path = os.path.join(_data_dir(), name)
        item = {
            'name': name,
            'type': ext[1:].upper(),
            'movies': [],
            'error': None,
        }

        if ext == '.json':
            ok, err, data = validate_json_file(path)
        else:
            ok, err, data = validate_xml_file(path)

        if ok:
            item['movies'] = data
        else:
            item['error'] = err

        files_data.append(item)

    return files_data


def list_files(request):
    files_data = _read_files_data()
    return render(request, 'movies/files.html', {
        'files_data': files_data,
        'count': len(files_data),
    })


def data_view(request):
    source = request.GET.get('source', 'db')
    if source not in ('db', 'files'):
        source = 'db'

    context = {
        'source': source,
        'db_movies': Movie.objects.all(),
        'db_count': Movie.objects.count(),
    }

    if source == 'files':
        files_data = _read_files_data()
        context['files_data'] = files_data
        context['files_count'] = len(files_data)

    return render(request, 'movies/data.html', context)


def movie_edit(request, pk):
    movie = get_object_or_404(Movie, pk=pk)

    if request.method == 'POST':
        form = MovieEditForm(request.POST, instance=movie)
        if form.is_valid():
            form.save()
            messages.success(request, f'Фильм «{movie.title}» обновлён')
            return redirect(f"{reverse('data_view')}?source=db")
    else:
        form = MovieEditForm(instance=movie)

    return render(request, 'movies/edit_movie.html', {'form': form, 'movie': movie})


@require_POST
def movie_delete(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    title = movie.title
    movie.delete()
    messages.success(request, f'Фильм «{title}» удалён из базы данных')
    return redirect(f"{reverse('data_view')}?source=db")


@require_GET
def movie_search(request):
    query = request.GET.get('q', '')
    movies = search_movies(query)
    return JsonResponse({
        'query': query,
        'count': movies.count(),
        'results': [movie_to_dict(movie) for movie in movies],
    })
