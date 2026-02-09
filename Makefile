.PHONY: help db-up db-down db-reset migrate run shell test clean

GREEN = \033[0;32m
NC = \033[0m

help:
	@echo "Использование: make [цель]"
	@echo ""
	@echo "Цели:"
	@echo "  make db-up           - Запустить базу данных"
	@echo "  make db-down         - Остановить базу данных"
	@echo "  make db-reset        - Перезапустить базу данных"
	@echo "  make migrate         - Создать и применить миграции"
	@echo "  make run             - Запустить сервер Django"
	@echo "  make shell           - Открыть Django shell"
	@echo "  make createsuperuser - Создать суперпользователя"
	@echo "  make test            - Запустить тесты"
	@echo "  make clean           - Очистить кэш и временные файлы"
	@echo "  make requirements    - Обновить requirements.txt"
	@echo "  make install         - Установить зависимости"

db-up:
	@echo "Запуск PostgreSQL..."
	cd storage/docker && docker-compose up -d
	@echo "База данных запущена на localhost:5433"

db-down:
	@echo "Остановка базы данных..."
	cd storage/docker && docker-compose down
	@echo "База данных остановлена"

db-reset: db-down db-up

migrate:
	@echo "Создание миграций..."
	cd django_proj && python manage.py makemigrations comments
	@echo "Применение миграций..."
	cd django_proj && python manage.py migrate
	@echo "Миграции применены"

run:
	@echo "Запуск сервера Django..."
	cd django_proj && python manage.py runserver

shell:
	cd django_proj && python manage.py shell

createsuperuser:
	cd django_proj && python manage.py createsuperuser

test:
	cd django_proj && python manage.py test comments

clean:
	@echo "Очистка временных файлов..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name ".DS_Store" -delete
	@echo "Очистка завершена"

requirements:
	cd django_proj && pip freeze > requirements.txt

install:
	cd django_proj && pip install -r requirements.txt