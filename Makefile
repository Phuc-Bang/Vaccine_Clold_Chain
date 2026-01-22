# Common commands for Vaccine Cold Chain Monitor

.PHONY: help dev-backend dev-frontend test deps install clean docker-up docker-down test-backend test-coverage lint format

# Default target
.DEFAULT_GOAL := help

# Help
help:
	@echo "╔════════════════════════════════════════════════════════╗"
	@echo "║  VaccineColdChain - Make Commands                      ║"
	@echo "╚════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "🚀 Development Commands:"
	@echo "  make dev-backend       Start FastAPI backend (uvicorn)"
	@echo "  make dev-frontend      Start Next.js frontend dev server"
	@echo "  make docker-up         Start Docker containers (MQTT, PostgreSQL)"
	@echo "  make docker-down       Stop Docker containers"
	@echo ""
	@echo "🧪 Testing & Quality:"
	@echo "  make test              Run all tests with pytest"
	@echo "  make test-coverage     Run tests with coverage report"
	@echo "  make lint              Run linters (Pylint, Black)"
	@echo "  make format            Format code with Black"
	@echo ""
	@echo "📦 Dependency Management:"
	@echo "  make deps              Install all dependencies"
	@echo "  make clean             Clean cache files"
	@echo ""
	@echo "💡 Quick Start:"
	@echo "  1. make deps           # Install dependencies"
	@echo "  2. make docker-up      # Start services"
	@echo "  3. make dev-backend    # In terminal 2"
	@echo "  4. make dev-frontend   # In terminal 3"
	@echo ""

# Development
dev-backend:
	cd backend && uvicorn app.main:app --reload

dev-frontend:
	cd frontend && npm run dev

dev:
	@echo "Please run 'make dev-backend' and 'make dev-frontend' in separate terminals"

# Installation
deps:
	pip install -r backend/requirements.txt
	cd frontend && npm install

# Testing
test-backend:
	cd backend && pytest -v

test: test-backend

test-coverage:
	cd backend && pytest --cov=app --cov-report=html --cov-report=term

# Linting & Formatting
lint:
	cd backend && pylint app/ --disable=all --enable=E,F || true
	cd backend && black --check app/ tests/ || true

format:
	cd backend && black app/ tests/

# Docker
docker-up:
	docker-compose -f infra/docker/docker-compose.yml up -d
	@echo "✓ Docker services started"
	@echo "  MQTT: localhost:1883"
	@echo "  PostgreSQL: localhost:5432"
	@echo "  Backend: localhost:8000"

docker-down:
	docker-compose -f infra/docker/docker-compose.yml down
	@echo "✓ Docker services stopped"

docker-logs:
	docker-compose -f infra/docker/docker-compose.yml logs -f

# Clean
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Cache cleaned"
