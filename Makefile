.PHONY: help install backend frontend dev api bot

BACKEND_DIR  ?= backend
FRONTEND_DIR ?= frontend

help:
	@echo "Targets:"
	@echo "  install    Install backend and frontend deps"
	@echo "  backend    Install backend deps (poetry)"
	@echo "  frontend   Install frontend deps (npm)"
	@echo "  dev        Run api + bot + frontend (parallel)"
	@echo "  api        Run FastAPI (reload) on :8000"
	@echo "  bot        Run Discord bot"
	@echo "  frontend   Run frontend dev server"

install: backend frontend

backend:
	@test -d "$(BACKEND_DIR)" || (echo "Missing $(BACKEND_DIR)/" && exit 1)
	cd "$(BACKEND_DIR)" && poetry install

frontend:
	@test -d "$(FRONTEND_DIR)" || (echo "Missing $(FRONTEND_DIR)/" && exit 1)
	cd "$(FRONTEND_DIR)" && npm install

dev:
	$(MAKE) -j3 api bot frontend

api:
	cd "$(BACKEND_DIR)" && poetry run uvicorn nonagon_api.main:app --reload --host 0.0.0.0 --port 8000

bot:
	cd "$(BACKEND_DIR)" && poetry run python -m nonagon_bot.main

frontend:
	cd "$(FRONTEND_DIR)" && npm run dev