#!/bin/sh
# Сервер разработки: перезапуск при правке кода, раздача статики и media (DEBUG=True)
exec python manage.py runserver 0.0.0.0:8000