# Локально
install:
	uv sync

dev:
	uv run flask --debug --app page_analyzer:app run

lint:
	uv run ruff check --fix

PORT ?= 8000
start:
	uv run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

# Для Render
build:
	pip install -r requirements.txt && \
	psql -a -d $(DATABASE_URL) -f database.sql

render-start:
	gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app
