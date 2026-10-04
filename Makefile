.DEFAULT_GOAL := help
.PHONY: help api web migrate

help: ## List available commands
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  make %-8s %s\n", $$1, $$2}'

api: ## Run the FastAPI dev server on http://localhost:8000
	uv run --package aesthetic-api fastapi dev apps/api/aesthetic_api/main.py

web: ## Run the Next.js dev server on http://localhost:3000
	pnpm dev:web

migrate: ## Apply database migrations to DATABASE_URL from .env
	uv run --package aesthetic-api alembic -c apps/api/alembic.ini upgrade head
