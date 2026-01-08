.PHONY: help install dev api bot frontend test lint db-up db-down clean

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

# (Removed) JSON Schema code generation targets

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
# CI
# ═══════════════════════════════════════════════════════════════════════════════

ci: lint test ## Run CI checks (lint + test)

# ═══════════════════════════════════════════════════════════════════════════════
# CLEANUP
# ═══════════════════════════════════════════════════════════════════════════════

clean: ## Clean build artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .coverage htmlcov/
	cd frontend && rm -rf dist .parcel-cache node_modules/.cache 2>/dev/null || true
