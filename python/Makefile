.PHONY: help setup install test lint format clean docs

# Default target
help:
	@echo "MBON Python Development Commands"
	@echo "================================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  setup     - Install dependencies and setup pre-commit"
	@echo "  install   - Install dependencies only"
	@echo "  update    - Update all dependencies"
	@echo ""
	@echo "Development:"
	@echo "  test      - Run tests"
	@echo "  test-cov  - Run tests with coverage"
	@echo "  lint      - Run linting checks"
	@echo "  format    - Format code"
	@echo "  typecheck - Run type checking"
	@echo ""
	@echo "Data Processing:"
	@echo "  views     - Generate all view files"
	@echo "  indices   - Generate compiled indices"
	@echo "  migrate   - Migrate data to top-level"
	@echo "  test-data - Test data access"
	@echo ""
	@echo "Utilities:"
	@echo "  clean     - Clean build artifacts"
	@echo "  docs      - Build documentation"
	@echo "  tree      - Show dependency tree"

# Setup and installation
setup: install
	uv run pre-commit install
	@echo "✅ Setup complete! Pre-commit hooks installed."

install:
	uv sync --dev
	@echo "✅ Dependencies installed."

update:
	uv lock --upgrade
	uv sync --dev
	@echo "✅ Dependencies updated."

# Testing
test:
	uv run pytest

test-cov:
	uv run pytest --cov=mbon_analysis --cov-report=html --cov-report=term-missing

test-watch:
	uv run pytest-watch

# Code quality
lint:
	uv run ruff check .
	uv run black --check .
	uv run isort --check-only .

lint-fix:
	uv run ruff check --fix .
	uv run black .
	uv run isort .

format:
	uv run black .
	uv run isort .

typecheck:
	uv run mypy .

# Data processing
views:
	uv run mbon-generate-views

indices:
	uv run scripts/generate_compiled_indices.py

migrate:
	uv run scripts/migrate_data_to_top_level.py

test-data:
	uv run scripts/test_dashboard_data_access.py

# Utilities
clean:
	rm -rf .venv
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
	@echo "✅ Cleaned build artifacts."

docs:
	uv run sphinx-build -b html docs/ docs/_build/html
	@echo "✅ Documentation built in docs/_build/html/"

tree:
	uv tree

# Development workflow
dev-setup: setup
	@echo "🚀 Development environment ready!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Run 'make test' to verify everything works"
	@echo "  2. Run 'make views' to generate dashboard views"
	@echo "  3. Start developing!"

# Quick development cycle
dev-cycle: format lint test
	@echo "✅ Development cycle complete!"

# Full CI check
ci: lint typecheck test-cov
	@echo "✅ CI checks passed!"
