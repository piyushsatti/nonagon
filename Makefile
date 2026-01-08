.PHONY: help install install-backend install-frontend dev api bot frontend test test-core test-api test-bot test-cov lint lint-fix format ci clean

POETRY ?= poetry
BACKEND := backend
FRONTEND := frontend
PP := api:bot
ENV := POETRY_VIRTUALENVS_IN_PROJECT=true

help:
	@echo "Available targets:"
	@printf "  %-18s %s\n" "install" "Install backend and frontend deps"
	@printf "  %-18s %s\n" "install-backend" "Install backend dependencies"
	@printf "  %-18s %s\n" "install-frontend" "Install frontend dependencies"
	@printf "  %-18s %s\n" "dev" "Run api, bot, and frontend"
	@printf "  %-18s %s\n" "api" "Run FastAPI with reload"
	@printf "  %-18s %s\n" "bot" "Run Discord bot"
	@printf "  %-18s %s\n" "frontend" "Run frontend dev server"

install: install-backend install-frontend

install-backend:
	@if [ ! -d "backend" ]; then \
		echo "Error: backend directory not found!"; \
		exit 1; \
	fi
	cd $(BACKEND) && $(ENV) $(POETRY) install --no-root

install-frontend:
	@if [ ! -d "frontend" ]; then \
		echo "Error: frontend directory not found!"; \
		exit 1; \
	fi
	cd $(FRONTEND) && npm install

dev:
	$(MAKE) -j3 api bot frontend

api:
	cd $(BACKEND) && $(ENV) PYTHONPATH=$(PP) $(POETRY) run python -m uvicorn nonagon_api.main:app --reload --host 0.0.0.0 --port 8000

bot:
	cd $(BACKEND) && $(ENV) PYTHONPATH=$(PP) $(POETRY) run python -m nonagon_bot.main

frontend:
	cd $(FRONTEND) && npm run dev