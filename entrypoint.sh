#!/bin/bash
set -e

echo "Ожидание PostgreSQL..."
until python -c "import socket; socket.create_connection(('db', 5432), timeout=3)" 2>/dev/null; do
  sleep 1
done

echo "Применение миграций..."
python manage.py migrate --noinput

echo "Сбор статических файлов..."
python manage.py collectstatic --noinput

echo "Запуск сервера..."
exec python manage.py runserver 0.0.0.0:8000