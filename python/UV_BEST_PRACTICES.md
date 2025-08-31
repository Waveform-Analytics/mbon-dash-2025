# UV Best Practices for MBON Project

This guide covers how to use `uv` effectively for Python dependency management in the MBON Marine Biodiversity Dashboard project.

## 🚀 Quick Start

### Initial Setup
```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Navigate to Python directory
cd python/

# Install dependencies
uv sync --dev

# Install pre-commit hooks
uv run pre-commit install
```

### Daily Development
```bash
# Run scripts
uv run scripts/generate_all_views.py
uv run scripts/test_data_loading.py

# Run tests
uv run pytest

# Format code
uv run black .
uv run isort .

# Lint code
uv run ruff check .
```

## 📦 Dependency Management

### Adding Dependencies

#### Production Dependencies
```bash
# Add to main dependencies
uv add pandas numpy scikit-learn

# Add with specific version
uv add "pandas>=2.1.0"

# Add from specific source
uv add --index-url https://pypi.org/simple/ package-name
```

#### Development Dependencies
```bash
# Add to dev dependencies
uv add --dev pytest ruff mypy

# Add to specific optional dependency group
uv add --group docs sphinx sphinx-rtd-theme
uv add --group viz plotly bokeh
```

#### Optional Dependency Groups
```bash
# Install with specific groups
uv sync --group dev,docs
uv sync --group viz,notebooks

# Install all groups
uv sync --all-extras
```

### Removing Dependencies
```bash
# Remove from main dependencies
uv remove pandas

# Remove from dev dependencies
uv remove --dev pytest

# Remove from specific group
uv remove --group docs sphinx
```

### Updating Dependencies
```bash
# Update all dependencies
uv lock --upgrade

# Update specific package
uv lock --upgrade-package pandas

# Update to latest compatible versions
uv lock --upgrade
```

## 🔧 Project Configuration

### pyproject.toml Structure
```toml
[project]
name = "mbon-analysis"
version = "0.1.0"
description = "MBON Marine Biodiversity Dashboard"
requires-python = ">=3.12"
dependencies = [
    "pandas>=2.1.0",
    "numpy>=1.24.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "ruff>=0.0.290",
]
docs = [
    "sphinx>=7.0.0",
]
viz = [
    "plotly>=5.15.0",
]

[project.scripts]
mbon-process = "mbon_analysis.cli:main"
mbon-generate-views = "mbon_analysis.cli:generate_views_cli"
```

### Development Tools Configuration
```toml
[tool.ruff]
line-length = 88
target-version = "py312"
select = ["E", "F", "I", "N", "W", "UP", "B", "C4", "SIM"]

[tool.mypy]
python_version = "3.12"
disallow_untyped_defs = true
warn_return_any = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = ["--strict-markers", "--cov=mbon_analysis"]
```

## 🧪 Testing with UV

### Running Tests
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=mbon_analysis --cov-report=html

# Run specific test file
uv run pytest tests/test_data_loaders.py

# Run with specific markers
uv run pytest -m "not slow"
uv run pytest -m "integration"

# Run in watch mode (requires pytest-watch)
uv add --dev pytest-watch
uv run pytest-watch
```

### Test Configuration
```bash
# Run tests with verbose output
uv run pytest -v

# Run tests with parallel execution
uv run pytest -n auto

# Generate coverage report
uv run pytest --cov=mbon_analysis --cov-report=xml --cov-report=html
```

## 🎨 Code Quality

### Linting and Formatting
```bash
# Check code with ruff
uv run ruff check .

# Fix issues automatically
uv run ruff check --fix .

# Format with black
uv run black .

# Sort imports
uv run isort .

# Type checking
uv run mypy .
```

### Pre-commit Hooks
```bash
# Install pre-commit hooks
uv run pre-commit install

# Run pre-commit on all files
uv run pre-commit run --all-files

# Run specific hook
uv run pre-commit run ruff --all-files
```

## 📊 Project Scripts

### Using the CLI
```bash
# Generate all views
uv run mbon-generate-views

# Generate specific view
uv run mbon-generate-views --view stations

# Process data
uv run mbon-process process --data-root /path/to/data

# Show help
uv run mbon-process --help
```

### Custom Scripts
```bash
# Run any Python script
uv run scripts/generate_compiled_indices.py
uv run scripts/migrate_data_to_top_level.py
uv run scripts/test_dashboard_data_access.py

# Run with arguments
uv run scripts/compiled_indices_utils.py data/processed/compiled_indices.json --action summary
```

## 🔄 Workflow Integration

### NPM Scripts Integration
```json
{
  "scripts": {
    "setup:python": "cd python && uv sync --dev && uv run pre-commit install",
    "test:python": "cd python && uv run pytest",
    "lint:python": "cd python && uv run ruff check .",
    "format:python": "cd python && uv run black . && uv run isort ."
  }
}
```

### CI/CD Integration
```yaml
# GitHub Actions example
- name: Setup Python
  uses: astral-sh/setup-uv@v1
  with:
    version: "latest"

- name: Install dependencies
  run: |
    cd python
    uv sync --dev

- name: Run tests
  run: |
    cd python
    uv run pytest

- name: Lint code
  run: |
    cd python
    uv run ruff check .
    uv run black --check .
    uv run mypy .
```

## 🐛 Troubleshooting

### Common Issues

#### Lock File Conflicts
```bash
# Regenerate lock file
uv lock --reinstall

# Update lock file
uv lock --upgrade
```

#### Virtual Environment Issues
```bash
# Remove and recreate virtual environment
rm -rf .venv
uv sync --dev
```

#### Dependency Resolution Issues
```bash
# Check dependency tree
uv tree

# Check for conflicts
uv lock --check
```

#### Performance Issues
```bash
# Use faster index
uv add --index-url https://pypi.org/simple/ package-name

# Clear cache
uv cache clean
```

### Debugging Commands
```bash
# Show dependency tree
uv tree

# Show installed packages
uv pip list

# Show package info
uv pip show pandas

# Check Python version
uv run python --version
```

## 📚 Best Practices Summary

### ✅ Do's
- ✅ Use `uv sync --dev` for development setup
- ✅ Pin Python version in `.python-version`
- ✅ Use dependency groups for different environments
- ✅ Run pre-commit hooks before committing
- ✅ Use `uv run` for all Python commands
- ✅ Keep lock file in version control
- ✅ Use semantic versioning for dependencies

### ❌ Don'ts
- ❌ Don't manually edit `uv.lock`
- ❌ Don't use `pip` directly in the project
- ❌ Don't commit `.venv` directory
- ❌ Don't ignore lock file conflicts
- ❌ Don't use `requirements.txt` (use `pyproject.toml`)

### 🔧 Recommended Workflow
1. **Setup**: `uv sync --dev`
2. **Development**: `uv run <script>`
3. **Testing**: `uv run pytest`
4. **Linting**: `uv run ruff check .`
5. **Formatting**: `uv run black .`
6. **Pre-commit**: `uv run pre-commit run --all-files`

## 🎯 Project-Specific Commands

### MBON Data Processing
```bash
# Generate all views
uv run mbon-generate-views

# Generate compiled indices
uv run scripts/generate_compiled_indices.py

# Test data access
uv run scripts/test_dashboard_data_access.py

# Migrate data (if needed)
uv run scripts/migrate_data_to_top_level.py
```

### Development Tools
```bash
# Code quality checks
uv run ruff check .
uv run black --check .
uv run mypy .

# Auto-fix issues
uv run ruff check --fix .
uv run black .
uv run isort .

# Run tests with coverage
uv run pytest --cov=mbon_analysis --cov-report=html
```

This setup ensures consistent, fast, and reliable Python dependency management for the MBON project! 🚀
