#!/bin/sh
set -e

# venv лежит в volume: при первом запуске или после смены lock-файла — досинхронизировать
uv sync --locked --dev --no-install-project --quiet

python manage.py migrate --noinput
python manage.py ensure_superuser
python manage.py seed_demo

exec "$@"
