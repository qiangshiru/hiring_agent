.PHONY: install lint typecheck test run migrate revision docker-up docker-down

install:
	poetry install

lint:
	poetry run ruff check .

typecheck:
	poetry run mypy src tests

test:
	poetry run pytest

run:
	poetry run uvicorn src.main:app --host $${APP_HOST:-0.0.0.0} --port $${APP_PORT:-8000} --reload

migrate:
	poetry run alembic upgrade head

revision:
	poetry run alembic revision --autogenerate -m "$${MESSAGE:-schema change}"

docker-up:
	docker compose up -d

docker-down:
	docker compose down
