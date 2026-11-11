# Локальная разработка.
#   Без Docker (SQLite):    make setup && make run
#   В Docker (Postgres):    make up
# Список команд: make help

MANAGE := uv run python manage.py
DC := docker compose -f docker-compose.dev.yml
DC_MANAGE := $(DC) exec backend python manage.py
HOST ?= 127.0.0.1
PORT ?= 8000

.DEFAULT_GOAL := help
.PHONY: help setup install env migrate migrations seed superuser run test lint format check shell clean \
	up down build logs ps dc-shell dc-manage dc-test dc-lint dc-reset

help: ## Показать список команд
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  make %-14s %s\n", $$1, $$2}'

setup: install env migrate seed ## Первый запуск: зависимости, .env, миграции, комплекты для примера
	@echo ""
	@echo "Готово. Запуск: make run → http://$(HOST):$(PORT)/"
	@echo "Админка: make superuser → http://$(HOST):$(PORT)/admin/"

install: ## Установить зависимости (uv sync)
	uv sync

env: ## Создать .env из example.env, если его ещё нет
	@if [ -f .env ]; then \
		echo ".env уже есть — не трогаю"; \
	else \
		cp example.env .env; \
		echo "Создан .env из example.env"; \
	fi

migrate: ## Применить миграции
	$(MANAGE) migrate

migrations: ## Создать миграции после правки моделей
	$(MANAGE) makemigrations

seed: ## Комплекты для примера (JAC T9, Haval H3, «Ваша модель»); повторный запуск дублей не создаёт
	$(MANAGE) seed_demo

superuser: ## Создать администратора для /admin/
	$(MANAGE) createsuperuser

run: ## Запустить сервер разработки (HOST, PORT можно переопределить: make run PORT=8080)
	$(MANAGE) runserver $(HOST):$(PORT)

test: ## Запустить тесты
	$(MANAGE) test apps

lint: ## Проверить код линтером и форматирование
	uv run ruff check .
	uv run ruff format --check .

format: ## Отформатировать код и исправить то, что ruff умеет сам
	uv run ruff check --fix .
	uv run ruff format .

check: lint test ## Линтер, тесты и проверка, что миграции не забыты
	$(MANAGE) check
	$(MANAGE) makemigrations --check --dry-run

shell: ## Django shell
	$(MANAGE) shell

clean: ## Удалить кеши Python и ruff (база и media не трогаются)
	find . -path ./.venv -prune -o -type d -name __pycache__ -exec rm -rf {} +
	rm -rf .ruff_cache

# ===== Docker (docker-compose.dev.yml: backend + postgres) =====

up: env ## Docker: собрать и запустить в фоне → http://localhost:8000/ (admin / admin)
	$(DC) up -d --build
	@echo "Готово: http://localhost:8000/  ·  логи: make logs  ·  остановить: make down"

down: ## Docker: остановить контейнеры (данные в volumes сохраняются)
	$(DC) down

build: ## Docker: пересобрать образ
	$(DC) build

logs: ## Docker: логи backend (Ctrl+C — выход)
	$(DC) logs -f backend

ps: ## Docker: состояние контейнеров
	$(DC) ps

dc-shell: ## Docker: Django shell внутри контейнера
	$(DC_MANAGE) shell

dc-manage: ## Docker: любая команда manage.py, например make dc-manage cmd="createsuperuser"
	$(DC_MANAGE) $(cmd)

dc-test: ## Docker: тесты на Postgres
	$(DC_MANAGE) test apps

dc-lint: ## Docker: ruff в контейнере
	$(DC) run --rm lint

dc-reset: ## Docker: остановить и УДАЛИТЬ volumes (база, media, venv) — спросит подтверждение
	@printf "Удалить базу, media и venv Docker-окружения? [y/N] " && read ans && [ "$$ans" = "y" ]
	$(DC) down -v
