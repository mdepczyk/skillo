.PHONY: help install dev run build up down logs clean test lint format

# Default target
help:
	@echo "Available commands:"
	@echo "  install    - Install dependencies with Poetry"
	@echo "  dev        - Run in development mode"
	@echo "  run        - Run the application"
	@echo "  build      - Build Docker image"
	@echo "  up         - Start services with docker-compose"
	@echo "  down       - Stop services"
	@echo "  logs       - View application logs"
	@echo "  clean      - Clean up containers and images"
	@echo "  test       - Run tests"
	@echo "  lint       - Run linting"
	@echo "  format     - Format code"

# Poetry commands
install:
	poetry install

dev:
	poetry run streamlit run skillo/ui/app.py --server.runOnSave true

run:
	poetry run streamlit run skillo/ui/app.py

# Docker commands
build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

clean:
	docker-compose down --volumes --remove-orphans
	docker system prune -f

# Development tools
test:
	poetry run pytest

lint:
	poetry run flake8 .
	poetry run mypy . --strict

format:
	poetry run black .
	poetry run isort .

# Setup environment
setup:
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env file. Please edit it with your configuration."; fi