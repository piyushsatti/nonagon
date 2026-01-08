.PHONY: help install dev api bot frontend test lint build up down logs generate clean

# ═══════════════════════════════════════════════════════════════════════════════
# HELP
# ═══════════════════════════════════════════════════════════════════════════════

help: ## Show this help
	@echo "Nonagon Monorepo - Available Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*##"}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

# ═══════════════════════════════════════════════════════════════════════════════
# INSTALLATION
# ═══════════════════════════════════════════════════════════════════════════════

install: ## Install all packages in dev mode
	pip install -e "backend/[dev]"
	cd frontend && npm install

install-backend: ## Install only backend package
	pip install -e "backend/[dev]"

install-frontend: ## Install only frontend packages
	cd frontend && npm install

hooks: ## Install pre-commit hooks
	pre-commit install

# ═══════════════════════════════════════════════════════════════════════════════
# DEVELOPMENT
# ═══════════════════════════════════════════════════════════════════════════════

dev: ## Start all services for local development (parallel)
	$(MAKE) -j3 api bot frontend

api: ## Run API with hot reload
	uvicorn nonagon_api.main:app --reload --host 0.0.0.0 --port 8000

bot: ## Run Discord bot
	python -m nonagon_bot.main

frontend: ## Run frontend dev server
	cd frontend && npm run dev

# ═══════════════════════════════════════════════════════════════════════════════
# CODE GENERATION
# ═══════════════════════════════════════════════════════════════════════════════

generate: ## Generate types from JSON Schema (Python + TypeScript)
	./scripts/generate-types.sh

generate-python: ## Generate only Python Pydantic models
	datamodel-codegen \
		--input shared/schemas \
		--output backend/api/nonagon_api/generated/schemas.py \
		--input-file-type jsonschema \
		--output-model-type pydantic_v2.BaseModel \
		--target-python-version 3.11

validate-schemas: ## Validate JSON Schema files
	./scripts/validate-schemas.sh

# ═══════════════════════════════════════════════════════════════════════════════
# TESTING
# ═══════════════════════════════════════════════════════════════════════════════

test: ## Run all tests
	pytest tests/ -v

test-core: ## Run core/domain tests
	pytest tests/domain/ tests/infra/ -v

test-api: ## Run API tests
	pytest tests/api/ -v

test-bot: ## Run bot tests
	pytest tests/bot/ -v

test-cov: ## Run tests with coverage
	pytest tests/ --cov=backend --cov-report=html --cov-report=term

# ═══════════════════════════════════════════════════════════════════════════════
# LINTING
# ═══════════════════════════════════════════════════════════════════════════════

lint: ## Run all linters
	ruff check backend/
	cd frontend && npm run lint 2>/dev/null || true

lint-fix: ## Run linters and fix issues
	ruff check backend/ --fix
	cd frontend && npm run lint:fix 2>/dev/null || true

format: ## Format code
	ruff format backend/

# ═══════════════════════════════════════════════════════════════════════════════
# DOCKER
# ═══════════════════════════════════════════════════════════════════════════════

build: ## Build all Docker images
	docker compose build

build-api: ## Build API Docker image
	docker compose build api

build-bot: ## Build bot Docker image
	docker compose build bot

build-frontend: ## Build frontend Docker image
	docker compose build frontend

up: ## Start all services in background
	docker compose up -d

up-backend: ## Start only backend services (api, bot, mongo)
	docker compose up -d api bot mongo

down: ## Stop all services
	docker compose down

restart: ## Restart all services
	docker compose restart

logs: ## Tail logs from all services
	docker compose logs -f --tail=200

logs-api: ## Tail API logs
	docker compose logs -f --tail=200 api

logs-bot: ## Tail bot logs
	docker compose logs -f --tail=200 bot

# ═══════════════════════════════════════════════════════════════════════════════
# CI
# ═══════════════════════════════════════════════════════════════════════════════

ci: lint test ## Run CI checks (lint + test)

ci-check-generated: ## Check if generated files are up-to-date
	$(MAKE) generate
	git diff --exit-code backend/api/nonagon_api/generated/
	git diff --exit-code frontend/src/types/generated/

# ═══════════════════════════════════════════════════════════════════════════════
# CLEANUP
# ═══════════════════════════════════════════════════════════════════════════════

clean: ## Clean build artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .coverage htmlcov/
	cd frontend && rm -rf .next node_modules/.cache 2>/dev/null || true

clean-docker: ## Remove Docker volumes and images
	docker compose down -v --rmi local
