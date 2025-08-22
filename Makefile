.PHONY: setup dev run lint format security test cov collectstatic check deploy install migrate collect

setup:
	python -m pip install --upgrade pip wheel
	pip install -r requirements.txt

# Portable install using local venv
VENV=.venv
PY=$(VENV)/bin/python
PIP=$(VENV)/bin/pip

install:
	python3 -m venv $(VENV) || true
	$(PIP) install --upgrade pip wheel setuptools
	$(PIP) install -r requirements.txt

dev:
	DJANGO_SETTINGS_MODULE=config.settings.dev python manage.py runserver 0.0.0.0:8000

run:
	DJANGO_SETTINGS_MODULE=config.settings.prod gunicorn config.wsgi:application -b 127.0.0.1:8000 -w 3 --timeout 60

lint:
	black --check .
	isort --check-only .
	flake8 .

format:
	isort .
	black .

security:
	bandit -r . -x ./tests,./migrations || true

test:
	pytest

cov:
	pytest --cov=. --cov-report=term-missing --cov-report=xml

collectstatic:
	DJANGO_SETTINGS_MODULE=config.settings.prod python manage.py collectstatic --noinput

# Uniform shortcuts
migrate:
	$(PY) manage.py migrate --noinput || DJANGO_SETTINGS_MODULE=config.settings.prod python manage.py migrate --noinput

collect:
	$(PY) manage.py collectstatic --noinput || DJANGO_SETTINGS_MODULE=config.settings.prod python manage.py collectstatic --noinput

check:
	DJANGO_SETTINGS_MODULE=config.settings.prod python manage.py check --deploy
