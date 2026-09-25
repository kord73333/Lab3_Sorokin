import json
import os
import re
import uuid
import xml.etree.ElementTree as ET
from xml.dom import minidom

REQUIRED_FIELDS = ['title', 'director', 'year', 'genre', 'rating']
ALLOWED_EXT = {'.json', '.xml'}


def sanitize_filename(original_name: str) -> str:
    ext = os.path.splitext(original_name)[1].lower()
    if ext not in ALLOWED_EXT:
        ext = '.json'
    base = os.path.splitext(os.path.basename(original_name))[0]
    base = re.sub(r'[^A-Za-z0-9_\-]', '_', base)[:40] or 'file'
    return f"{uuid.uuid4().hex[:8]}_{base}{ext}"


def validate_movie_data(data: dict):
    errors = []
    if not isinstance(data, dict):
        return False, ['Запись не является объектом']

    for field in REQUIRED_FIELDS:
        if field not in data or data[field] in (None, ''):
            errors.append(f'Отсутствует поле "{field}"')

    if errors:
        return False, errors

    try:
        year = int(data['year'])
        if year < 1888 or year > 2100:
            errors.append('Год должен быть между 1888 и 2100')
    except (ValueError, TypeError):
        errors.append('Год должен быть числом')

    try:
        rating = float(data['rating'])
        if not (0 <= rating <= 10):
            errors.append('Рейтинг должен быть от 0 до 10')
    except (ValueError, TypeError):
        errors.append('Рейтинг должен быть числом')

    if not str(data['title']).strip():
        errors.append('Название не может быть пустым')
    if not str(data['director']).strip():
        errors.append('Режиссёр не может быть пустым')
    if not str(data['genre']).strip():
        errors.append('Жанр не может быть пустым')

    return (False, errors) if errors else (True, None)


def validate_json_file(path: str):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return False, f'Ошибка разбора JSON: {e}', None

    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        return False, 'JSON должен содержать объект или массив объектов', None

    for i, item in enumerate(data):
        ok, errs = validate_movie_data(item)
        if not ok:
            return False, f'Ошибка в записи №{i + 1}: ' + '; '.join(errs), None
    return True, None, data


def validate_xml_file(path: str):
    try:
        tree = ET.parse(path)
        root = tree.getroot()
    except ET.ParseError as e:
        return False, f'Ошибка разбора XML: {e}', None

    if root.tag == 'movie':
        items = [root]
    else:
        items = root.findall('movie')
        if not items:
            return False, 'В XML нет ни одного элемента <movie>', None

    movies = []
    for i, item in enumerate(items):
        data = {}
        for field in REQUIRED_FIELDS:
            el = item.find(field)
            data[field] = el.text if el is not None else None
        ok, errs = validate_movie_data(data)
        if not ok:
            return False, f'Ошибка в записи №{i + 1}: ' + '; '.join(errs), None
        movies.append({
            'title': str(data['title']),
            'director': str(data['director']),
            'year': int(data['year']),
            'genre': str(data['genre']),
            'rating': float(data['rating']),
        })
    return True, None, movies


def save_movie_to_file(movie: dict, fmt: str, data_dir: str) -> str:
    safe = sanitize_filename(f"{movie['title']}.{fmt}")
    path = os.path.join(data_dir, safe)

    if fmt == 'json':
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(movie, f, ensure_ascii=False, indent=2)
    else:
        root = ET.Element('movies')
        m = ET.SubElement(root, 'movie')
        for k, v in movie.items():
            child = ET.SubElement(m, k)
            child.text = str(v)
        xml_str = minidom.parseString(ET.tostring(root, 'utf-8')).toprettyxml(
            indent='  ', encoding='utf-8'
        )
        with open(path, 'wb') as f:
            f.write(xml_str)
    return safe