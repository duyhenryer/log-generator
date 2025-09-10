.PHONY: help install test lint format clean examples docker-build docker-build-dev docker-run docker-run-dev

help:  ## Show help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-10s %s\n", $$1, $$2}'

install:  ## Install package
	uv pip install --editable ".[dev,test]"

test:  ## Run tests
	pytest

lint:  ## Run linting
	ruff check loggen/
	mypy loggen/

format:  ## Format code
	ruff format loggen/

clean:  ## Clean up
	rm -rf build/ dist/ *.egg-info/
	find . -name __pycache__ -delete

examples:  ## Run examples
	@echo "Raw logs:"
	log-generator --sleep 0.5 --count 3
	@echo "\nJSON logs:"
	log-generator --format json --sleep 0.5 --count 3

docker-build:  ## Build Docker image (production)
	docker build --target production -t log-generator:prod .

docker-build-dev:  ## Build Docker image (development)
	docker build --target development -t log-generator:dev .

docker-run:  ## Run Docker container (production)
	docker run --rm log-generator:prod --sleep 1 --count 5

docker-run-dev:  ## Run Docker container (development)
	docker run --rm log-generator:dev --sleep 1 --count 5
