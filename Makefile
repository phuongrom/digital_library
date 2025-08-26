.PHONY: help install install-dev test test-coverage lint format clean docker-build docker-run deploy

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install production dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

test: ## Run tests
	pytest tests/ -v

test-coverage: ## Run tests with coverage report
	pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing --cov-fail-under=80

test-fast: ## Run only fast tests
	pytest tests/ -v -m "not slow"

test-unit: ## Run only unit tests
	pytest tests/ -v -m "unit"

test-integration: ## Run only integration tests
	pytest tests/ -v -m "integration"

lint: ## Run linting
	flake8 app/ tests/
	black --check app/ tests/
	isort --check-only app/ tests/

format: ## Format code
	black app/ tests/
	isort app/ tests/

clean: ## Clean up
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .coverage htmlcov/ .pytest_cache/ .mypy_cache/

docker-build: ## Build Docker image
	docker build -t digital-library .

docker-run: ## Run Docker container
	docker run -p 5000:5000 digital-library

deploy: ## Deploy to production
	kubectl apply -f k8s/

migrate: ## Run database migrations
	alembic upgrade head

seed: ## Seed database with sample data
	python scripts/seed_data.py

pre-commit: ## Run pre-commit hooks
	pre-commit run --all-files

security-check: ## Run security checks
	bandit -r app/
	safety check
