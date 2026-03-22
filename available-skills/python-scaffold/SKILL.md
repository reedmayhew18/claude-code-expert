---
name: python-scaffold
description: Scaffold a new Python project with modern best practices. Use when the user says "new Python project", "create a Python app", "scaffold Python", "set up a Python package", or "Python starter".
argument-hint: "[project type] [framework preferences]"
disable-model-invocation: true
---

# Python Project Scaffolder

Create a properly structured Python project with modern tooling.

## Process

### Step 1: Gather Requirements
Ask about:
1. **Type**: CLI tool, web API, library/package, data pipeline, automation script?
2. **Framework**: FastAPI, Django, Flask, Click, Typer, plain Python?
3. **Database**: PostgreSQL, SQLite, MongoDB, none?
4. **Testing**: pytest (recommended), unittest?
5. **Package manager**: uv (recommended), poetry, pip?

### Step 2: Create Structure
Adapt to project type. Example for FastAPI:
```
project/
├── src/
│   └── project_name/
│       ├── __init__.py
│       ├── main.py          # App entrypoint
│       ├── config.py        # Settings via pydantic-settings
│       ├── models/          # Database models
│       ├── routes/          # API endpoints
│       ├── services/        # Business logic
│       └── schemas/         # Pydantic schemas
├── tests/
│   ├── conftest.py          # Shared fixtures
│   └── test_main.py
├── CLAUDE.md
├── pyproject.toml           # Modern Python packaging
├── .gitignore
└── README.md
```

### Step 3: Configure Tooling
In `pyproject.toml`:
- **ruff** for linting and formatting (replaces flake8, black, isort)
- **mypy** for type checking
- **pytest** for testing
- Modern build system (hatchling or setuptools)

### Step 4: Implement Foundation
- Entry point that runs
- Type hints on all functions
- Basic error handling
- One passing test
- Environment variable configuration (no secrets in code)

### Step 5: Create CLAUDE.md
Generate project-specific CLAUDE.md with:
- Python version, framework, key dependencies
- Build, test, lint commands
- Architecture conventions
- Hard rules (testing requirements, type hint expectations)

### Step 6: Verify
- `python -m project_name` or `uvicorn` starts successfully
- `pytest` passes
- `ruff check .` clean
- `mypy .` clean (or close to it)
