import os

from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect

from .forms import MovieForm
from .utils import (
    sanitize_filename,
    save_movie_to_file,
    validate_json_file,
    validate_xml_file,
)

DATA_DIR = settings.DATA_DIR


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def index(request):
    return render(request, 'movies/index.html')

def add_movie(request):
    _ensure_data_dir()
    if request.method == 'POST':
        form = MovieForm(request.POST)
        if form.is_valid():
            movie = {
                'title': form.cleaned_data['title'],
                'director': form.cleaned_data['director'],
                'year': form.cleaned_data['year'],
                'genre': form.cleaned_data['genre'],
                'rating': form.cleaned_data['rating'],
            }
            fmt = form.cleaned_data['file_format']
            try:
                filename = save_movie_to_file(movie, fmt, DATA_DIR)
                messages.success(
                    request, f'Фильм сохранён в файл «{filename}» ({fmt.upper()})'
                )
                return redirect('add_movie')
            except OSError as e:
                messages.error(request, f'Не удалось сохранить файл: {e}')
    else:
        form = MovieForm()
    return render(request, 'movies/add_movie.html', {'form': form})


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
        path = os.path.join(DATA_DIR, safe_name)

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


def list_files(request):
    _ensure_data_dir()
    files_data = []

    for name in sorted(os.listdir(DATA_DIR)):
        ext = os.path.splitext(name)[1].lower()
        if ext not in ('.json', '.xml'):
            continue

        path = os.path.join(DATA_DIR, name)
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

    return render(request, 'movies/files.html', {
        'files_data': files_data,
        'count': len(files_data),
    })