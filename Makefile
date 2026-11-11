# Локальная разработка. Первый запуск: make setup && make run
# Список команд: make help

MANAGE := uv run python manage.py
HOST ?= 127.0.0.1
PORT ?= 8000

.DEFAULT_GOAL := help
.PHONY: help setup install env migrate migrations seed superuser run test lint format check shell clean

help: ## Показать список команд
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  make %-12s %s\n", $$1, $$2}'

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
