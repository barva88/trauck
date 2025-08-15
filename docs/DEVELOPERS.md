# Developers Guide

## Setup
- Create and activate a virtualenv (Python 3.11+)
- make setup
- Copy .env.example to .env and adjust values

## Running
- make dev (local)
- make run (gunicorn prod settings)

## Quality
- Install pre-commit and enable hooks:
  - pip install pre-commit; pre-commit install
- Format: `make format` (isort + black)
- Lint: `make lint`
- Security: `make security`

## Tests
- `make test` or `make cov`
