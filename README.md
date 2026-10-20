# 🎬 Кинотека — хранение данных в файлах и в базе данных

Django-приложение, которое развивает предыдущий проект (хранение в JSON/XML)
и добавляет полноценную работу с базой данных SQLite.

Пользователь сам выбирает, **куда сохранить** введённые с формы данные — в файл
(JSON или XML) или в базу данных. При сохранении в БД работает проверка на
дубликаты. Данные можно **просматривать из любого источника** (файлы или БД),
а для записей в базе доступны **AJAX-поиск, редактирование и удаление**.

---

## ✨ Возможности

| Возможность | Где реализовано |
|---|---|
| Форма сохранения фильма с выбором источника (файл / БД) | `movies/forms.py`, `movies/views.py` (`add_movie`) |
| Сохранение в файл JSON/XML | `movies/utils.py` (`save_movie_to_file`) |
| Сохранение в БД с проверкой на дубликаты | `movies/services.py` (`save_movie_to_db`), `movies/models.py` (UniqueConstraint) |
| Сообщение о найденном дубликате | `movies/views.py` (`_save_to_database`), `UniqueConstraint.violation_error_message` |
| Выбор источника вывода данных (БД / файлы) | `movies/views.py` (`data_view`), `movies/templates/movies/data.html` |
| AJAX-поиск по текстовым полям БД | `movie_search` + `movies/static/movies/js/movies.js` |
| Редактирование записей БД с валидацией | `movie_edit`, `MovieEditForm` |
| Удаление записей БД | `movie_delete` |
| Интерфейс на Bootstrap 5 | `movies/templates/movies/base.html` |
| Загрузка готовых JSON/XML-файлов | `upload_file` |

Поиск по базе выполняется **без перезагрузки страницы** по полям текстового
формата: `title` (название), `director` (режиссёр) и `genre` (жанр).

---

## 🗂️ Структура проекта

```
Lab3/
├── manage.py
├── requirements.txt
├── db.sqlite3                # база данных SQLite (создаётся миграциями)
├── data/                     # каталог для файлов JSON/XML
├── movie_project/            # настройки проекта
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── movies/                   # основное приложение
    ├── models.py             # модель Movie + ограничение уникальности
    ├── forms.py              # формы добавления и редактирования
    ├── services.py           # работа с БД: дубликаты, поиск, сериализация
    ├── utils.py              # чтение/запись JSON и XML
    ├── views.py              # представления
    ├── urls.py               # маршруты
    ├── admin.py              # регистрация модели в админке
    ├── tests.py              # 24 теста
    ├── migrations/
    ├── static/movies/js/movies.js   # AJAX-поиск и удаление
    └── templates/movies/
        ├── base.html
        ├── index.html
        ├── add_movie.html
        ├── edit_movie.html
        ├── data.html
        ├── upload.html
        └── files.html
---

## 🚀 Запуск локально

```bash
# 1. Создать и активировать виртуальное окружение
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux / macOS

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Применить миграции (создадут файл db.sqlite3 и таблицу movies_movie)
python manage.py migrate

# 4. Запустить сервер разработки
python manage.py runserver
```

Приложение откроется по адресу <http://127.0.0.1:8000/>.

Дополнительно:

```bash
python manage.py createsuperuser   # доступ к админке /admin/
python manage.py test              # запуск тестов
python manage.py collectstatic     # сбор статики для продакшена
```

---

## 🧱 Модель данных

Таблица `movies_movie` (создаётся миграцией `0001_initial`):

| Поле | Тип | Описание |
|---|---|---|
| `id` | BigAutoField | Первичный ключ |
| `title` | CharField(200) | Название фильма |
| `director` | CharField(200) | Режиссёр |
| `year` | IntegerField | Год выпуска (1888–2100) |
| `genre` | CharField(100) | Жанр |
| `rating` | FloatField | Рейтинг (0–10) |
| `created_at` | DateTimeField | Дата добавления (автоматически) |

Миграция `0002` добавляет поле `created_at` и ограничение уникальности
`unique_movie_title_director_year` по полям
`(title, director, year)` — оно и защищает базу от дубликатов на уровне СУБД.

---

## 🔍 Как это работает

**Сохранение с формы.** В форме есть переключатель «Куда сохранить»:

* *База данных SQLite* — запись проверяется на дубликаты и сохраняется в таблицу
  `movies_movie`. Если такая запись уже есть, она **не добавляется**, а
  пользователь видит предупреждение «Такая запись уже есть в базе данных…».
* *Файл (JSON/XML)* — данные пишутся в файл в каталоге `data/`
  (имя файла генерируется из названия фильма и UUID).

**Просмотр данных.** Страница `/data/` переключает источник:

* `?source=db` — таблица записей из базы с кнопками «Редактировать» и «Удалить»;
* `?source=files` — содержимое всех файлов `data/*.json` и `data/*.xml`.

**AJAX-поиск.** Поле поиска на странице `/data/?source=db` отправляет запросы на
`/movies/search/?q=...` с задержкой 300 мс и перерисовывает таблицу из JSON-ответа
без перезагрузки страницы. Поиск идёт по `title`, `director` и `genre`
(регистронезависимо, `icontains`).

**Редактирование и удаление.** Редактирование открывает форму, которая проверяет
корректность значений перед сохранением. Удаление выполняется POST-запросом после
подтверждения и защищено CSRF-токеном.

---

## 🌐 Публикация на PythonAnywhere

1. Зарегистрируйтесь на <https://www.pythonanywhere.com/> и откройте **Consoles → Bash**.
2. Склонируйте репозиторий:

   ```bash
   git clone https://github.com/kord73333/Lab3_Sorokin.git
   cd Lab3_Sorokin
   ```

3. Создайте виртуальное окружение и установите зависимости:

   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 venv
   pip install -r requirements.txt
   ```

4. Примените миграции и соберите статику:

   ```bash
   python manage.py migrate
   python manage.py collectstatic
   python manage.py createsuperuser
   ```

5. На вкладке **Web** создайте новое веб-приложение (Manual configuration),
   выберите то же виртуальное окружение и отредактируйте **WSGI-файл**, заменив
   его содержимое на:

   ```python
   import os
   import sys

   path = '/home/<ваш_логин>/Lab3_Sorokin'
   if path not in sys.path:
       sys.path.insert(0, path)

   os.environ['DJANGO_SETTINGS_MODULE'] = 'movie_project.settings'
   os.environ['DJANGO_DEBUG'] = 'False'
   os.environ['DJANGO_SECRET_KEY'] = '<новый-секретный-ключ>'
   os.environ['DJANGO_ALLOWED_HOSTS'] = '<ваш_логин>.pythonanywhere.com'
   os.environ['DJANGO_CSRF_TRUSTED_ORIGINS'] = 'https://<ваш_логин>.pythonanywhere.com'

   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```

6. На вкладке **Web → Static files** добавьте сопоставление:

   | URL | Directory |
   |---|---|
   | `/static/` | `/home/<ваш_логин>/Lab3_Sorokin/staticfiles` |

7. Нажмите **Reload** — приложение будет доступно по адресу
   `https://<ваш_логин>.pythonanywhere.com/`.

### Переменные окружения

Настройки читаются из окружения (см. `movie_project/settings.py`):

| Переменная | По умолчанию | Назначение |
|---|---|---|
| `DJANGO_SECRET_KEY` | небезопасный ключ из репозитория | Секретный ключ Django |
| `DJANGO_DEBUG` | `True` | Режим отладки |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1,0.0.0.0,.pythonanywhere.com` | Разрешённые хосты |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | пусто | Доверенные источники для CSRF |

---

## ✅ Тесты

```bash
python manage.py test
```

Покрыто 24 теста: сохранение в БД и в файлы, проверка на дубликаты, валидация
полей, AJAX-поиск, переключение источника данных, редактирование с проверкой
корректности, удаление и защита от GET-удаления.
