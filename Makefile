.PHONY: dev test lint format build up down migrate clean setup setup-db setup-keycloak

# ---------------------------------------------------------------------------
# Development
# ---------------------------------------------------------------------------

dev:
	docker compose up -d postgres redis keycloak
	uvicorn src.runtime.app:app --reload --host 0.0.0.0 --port 8000

run:
	uvicorn src.runtime.app:app --reload --host 0.0.0.0 --port 8000

# ---------------------------------------------------------------------------
# Quality
# ---------------------------------------------------------------------------

test:
	pytest tests/ --cov=src --cov-fail-under=80 -v

lint:
	py .claude/linters/lint_all.py
	ruff check src/ tests/

format:
	ruff format src/ tests/
	ruff check --fix src/ tests/

# ---------------------------------------------------------------------------
# Docker
# ---------------------------------------------------------------------------

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

migrate:
	alembic upgrade head

# ---------------------------------------------------------------------------
# Frontend
# ---------------------------------------------------------------------------

frontend-install:
	cd frontend && npm ci

frontend-dev:
	cd frontend && npm run dev

frontend-build:
	cd frontend && npm run build

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

setup:
	py scripts/setup_all.py

setup-db:
	py scripts/setup_db.py

setup-keycloak:
	py scripts/setup_keycloak.py

# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov
	rm -rf frontend/dist frontend/node_modules/.cache
