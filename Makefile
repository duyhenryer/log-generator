.PHONY: help install-dev install test lint format clean examples docker-build docker-build-dev docker-run docker-run-dev

help:  ## Show help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-10s %s\n", $$1, $$2}'

install-dev:  ## Install package with dev/test dependencies
	uv sync --extra dev --extra test

install:  ## Install package (production)
	uv sync

test:  ## Run tests
	pytest

lint:  ## Run linting
	ruff check loggen/
	mypy loggen/

format:  ## Format code
	ruff format loggen/

clean:  ## Clean up
	rm -rf build/ dist/ *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

docker-build:  ## Build Docker image (production)
	docker build --target production -t log-generator:prod .

docker-build-dev:  ## Build Docker image (development)
	docker build --target development -t log-generator:dev .

docker-run:  ## Run Docker container (production)
	docker run --rm log-generator:prod --sleep 1 --count 5

docker-run-dev:  ## Run Docker container (development)
	docker run --rm log-generator:dev --sleep 1 --count 5

examples:  ## Run examples
	@echo "Raw logs:"
	uv run log-generator --sleep 0.5 --count 3
	@echo "\nJSON logs:"
	uv run log-generator --format json --sleep 0.5 --count 3
