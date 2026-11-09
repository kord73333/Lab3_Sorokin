# 🎬 Кинотека — Docker + PostgreSQL

Django-приложение для хранения данных о фильмах: пользователь выбирает, **куда сохранить** запись — в **PostgreSQL** или в файл **JSON/XML**.  
Для записей в базе доступны проверка на дубликаты, AJAX-поиск, редактирование и удаление.

Проект упакован в Docker-контейнеры (Django + PostgreSQL) и использует переменные окружения для конфигурации.

---

## ✨ Возможности

| Возможность | Где реализовано |
|-------------|-----------------|
| Форма с выбором хранилища (файл / PostgreSQL) | `movies/forms.py`, `movies/views.py` (`add_movie`) |
| Сохранение в JSON/XML | `movies/utils.py` (`save_movie_to_file`) |
| Сохранение в БД с проверкой дубликатов | `movies/services.py`, `movies/models.py` (`UniqueConstraint`) |
| Просмотр данных из БД или файлов | `movies/views.py` (`data_view`) |
| AJAX-поиск по названию, режиссёру, жанру | `movie_search` + `movies/static/movies/js/movies.js` |
| Редактирование и удаление записей БД | `movie_edit`, `movie_delete` |
| Загрузка готовых JSON/XML | `upload_file` |
| Интерфейс Bootstrap 5 | `movies/templates/movies/base.html` |

---

## 🗂️ Структура проекта
Lab3/
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env.example          # шаблон переменных (без секретов)
├── .gitignore
├── entrypoint.sh         # ожидание БД → migrate → collectstatic → runserver
├── manage.py
├── requirements.txt
├── datadump.json         # пример дампа для миграции данных (опционально)
├── movie_project/
│   ├── settings.py       # PostgreSQL через env, опция USE_SQLITE
│   ├── urls.py
│   └── wsgi.py
└── movies/
├── models.py
├── forms.py
├── services.py
├── utils.py
├── views.py
├── urls.py
├── tests.py
├── static/movies/js/movies.js
└── templates/movies/

---

## 🚀 Запуск через Docker (основной способ)

### 1. Подготовка

```bash
# Клонировать репозиторий
git clone https://github.com/kord73333/Lab3_Sorokin.git
cd Lab3_Sorokin

HEAD
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
=======
# Создать файл окружения
cp .env.example .env
d00635b (5 commit)
