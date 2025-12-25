"""Pytest fixtures for agent-readiness-score tests."""

import shutil
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def temp_repo(tmp_path: Path) -> Path:
    """Create a temporary directory for test repositories."""
    repo = tmp_path / "test_repo"
    repo.mkdir()
    return repo


@pytest.fixture
def python_repo(temp_repo: Path) -> Path:
    """Create a sample Python repository with typical files."""
    # Python files
    (temp_repo / "src").mkdir()
    (temp_repo / "src" / "main.py").write_text("def hello(): pass\n")
    (temp_repo / "src" / "utils.py").write_text("def util(): pass\n")

    # Tests
    (temp_repo / "tests").mkdir()
    (temp_repo / "tests" / "test_main.py").write_text("def test_hello(): pass\n")
    (temp_repo / "tests" / "conftest.py").write_text("import pytest\n")

    # Config files
    (temp_repo / "pyproject.toml").write_text("""
[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff]
line-length = 100

[tool.mypy]
strict = true

[tool.coverage.run]
source = ["src"]
""")

    (temp_repo / "pytest.ini").write_text("""
[pytest]
testpaths = tests
""")

    (temp_repo / "poetry.lock").write_text("# Poetry lockfile\n")

    (temp_repo / ".github" / "workflows").mkdir(parents=True)
    (temp_repo / ".github" / "workflows" / "ci.yml").write_text("""
name: CI
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pytest
""")

    # Docs
    (temp_repo / "README.md").write_text("# Test Project\n\nA test project.\n")
    (temp_repo / "docs").mkdir()
    (temp_repo / "docs" / "index.md").write_text("# Documentation\n")

    # DevContainer
    (temp_repo / ".devcontainer").mkdir()
    (temp_repo / ".devcontainer" / "devcontainer.json").write_text('{"name": "test"}\n')

    return temp_repo


@pytest.fixture
def typescript_repo(temp_repo: Path) -> Path:
    """Create a sample TypeScript repository."""
    # Source files
    (temp_repo / "src").mkdir()
    (temp_repo / "src" / "index.ts").write_text("export const hello = (): void => {}\n")
    (temp_repo / "src" / "utils.ts").write_text("export const util = (): void => {}\n")

    # Tests
    (temp_repo / "__tests__").mkdir()
    (temp_repo / "__tests__" / "index.test.ts").write_text("test('hello', () => {})\n")

    # Config files
    (temp_repo / "package.json").write_text("""
{
  "name": "test-project",
  "scripts": {
    "test": "jest",
    "build": "tsc"
  }
}
""")

    (temp_repo / "package-lock.json").write_text('{"lockfileVersion": 3}\n')

    (temp_repo / "tsconfig.json").write_text("""
{
  "compilerOptions": {
    "strict": true,
    "target": "ES2020"
  }
}
""")

    (temp_repo / "jest.config.js").write_text("""
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
};
""")

    (temp_repo / ".eslintrc.json").write_text("""
{
  "extends": ["eslint:recommended"],
  "parser": "@typescript-eslint/parser"
}
""")

    (temp_repo / ".prettierrc").write_text("""
{
  "semi": true,
  "singleQuote": true
}
""")

    (temp_repo / "README.md").write_text("# TypeScript Project\n")

    return temp_repo


@pytest.fixture
def go_repo(temp_repo: Path) -> Path:
    """Create a sample Go repository."""
    # Source files
    (temp_repo / "main.go").write_text("""
package main

func main() {
    println("Hello")
}
""")

    (temp_repo / "utils.go").write_text("""
package main

func Util() string {
    return "util"
}
""")

    # Test files
    (temp_repo / "main_test.go").write_text("""
package main

import "testing"

func TestMain(t *testing.T) {
    // test
}
""")

    # Config files
    (temp_repo / "go.mod").write_text("""
module github.com/test/project

go 1.21
""")

    (temp_repo / "go.sum").write_text("# Go dependencies\n")

    (temp_repo / ".golangci.yml").write_text("""
linters:
  enable:
    - gofmt
    - govet
""")

    (temp_repo / "Makefile").write_text("""
.PHONY: test build

test:
\tgo test ./...

build:
\tgo build -o bin/app
""")

    (temp_repo / "README.md").write_text("# Go Project\n")

    return temp_repo


@pytest.fixture
def minimal_repo(temp_repo: Path) -> Path:
    """Create a minimal repository with just a README."""
    (temp_repo / "README.md").write_text("# Minimal Project\n")
    (temp_repo / "main.py").write_text("print('hello')\n")
    return temp_repo


@pytest.fixture
def empty_repo(temp_repo: Path) -> Path:
    """Create an empty repository."""
    return temp_repo


@pytest.fixture
def multi_language_repo(temp_repo: Path) -> Path:
    """Create a repository with multiple languages."""
    # Python
    (temp_repo / "backend").mkdir()
    (temp_repo / "backend" / "app.py").write_text("def app(): pass\n")
    (temp_repo / "backend" / "test_app.py").write_text("def test(): pass\n")
    (temp_repo / "pyproject.toml").write_text("[tool.pytest.ini_options]\n")

    # TypeScript
    (temp_repo / "frontend").mkdir()
    (temp_repo / "frontend" / "index.ts").write_text("const x = 1;\n")
    (temp_repo / "frontend" / "index.test.ts").write_text("test('x', () => {})\n")
    (temp_repo / "package.json").write_text('{"name": "test"}\n')
    (temp_repo / "tsconfig.json").write_text('{"compilerOptions": {}}\n')

    # Rust
    (temp_repo / "Cargo.toml").write_text("[package]\nname = \"test\"\n")
    (temp_repo / "src" / "main.rs").write_text("fn main() {}\n")

    # Common files
    (temp_repo / "README.md").write_text("# Multi-language Project\n")
    (temp_repo / "Dockerfile").write_text("FROM ubuntu\n")
    (temp_repo / ".github" / "workflows" / "test.yml").write_text("name: Test\n")

    return temp_repo


@pytest.fixture
def complete_repo(temp_repo: Path) -> Path:
    """Create a repository with high agent readiness (all features)."""
    # Python source
    (temp_repo / "src" / "myapp").mkdir(parents=True)
    (temp_repo / "src" / "myapp" / "__init__.py").write_text("")
    (temp_repo / "src" / "myapp" / "main.py").write_text("def main() -> None: pass\n")
    (temp_repo / "src" / "myapp" / "py.typed").write_text("")

    # Tests
    (temp_repo / "tests").mkdir()
    (temp_repo / "tests" / "test_main.py").write_text("def test_main(): pass\n")
    (temp_repo / "tests" / "conftest.py").write_text("import pytest\n")

    # Comprehensive configs
    (temp_repo / "pyproject.toml").write_text("""
[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.poetry]
name = "myapp"
version = "0.1.0"

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=myapp"

[tool.ruff]
line-length = 100

[tool.mypy]
strict = true

[tool.coverage.run]
source = ["src"]
branch = true
""")

    (temp_repo / "poetry.lock").write_text("# Lock\n")
    (temp_repo / "pytest.ini").write_text("[pytest]\ntestpaths = tests\n")
    (temp_repo / ".coveragerc").write_text("[run]\nsource = src\n")

    # CI/CD
    (temp_repo / ".github" / "workflows").mkdir(parents=True)
    (temp_repo / ".github" / "workflows" / "ci.yml").write_text("""
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pytest
      - run: mypy .
      - run: ruff check .
""")

    (temp_repo / ".github" / "dependabot.yml").write_text("""
version: 2
updates:
  - package-ecosystem: pip
    directory: /
    schedule:
      interval: weekly
""")

    # DevContainer
    (temp_repo / ".devcontainer").mkdir()
    (temp_repo / ".devcontainer" / "devcontainer.json").write_text('{"name": "dev"}\n')
    (temp_repo / ".devcontainer" / "Dockerfile").write_text("FROM python:3.12\n")

    # Docker
    (temp_repo / "Dockerfile").write_text("FROM python:3.12\nCOPY . .\nRUN pip install .\n")
    (temp_repo / "docker-compose.yml").write_text("""
version: '3'
services:
  app:
    build: .
""")

    # Pre-commit
    (temp_repo / ".pre-commit-config.yaml").write_text("""
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    hooks:
      - id: ruff
""")

    # Documentation
    (temp_repo / "README.md").write_text("""
# MyApp

A complete project with high agent readiness.

## Installation

```bash
poetry install
```

## Testing

```bash
pytest
```
""")

    (temp_repo / "CONTRIBUTING.md").write_text("# Contributing\n\nThank you!\n")
    (temp_repo / "LICENSE").write_text("MIT License\n")
    (temp_repo / "CHANGELOG.md").write_text("# Changelog\n\n## 0.1.0\n")

    (temp_repo / "docs").mkdir()
    (temp_repo / "docs" / "index.md").write_text("# Documentation\n")
    (temp_repo / "docs" / "api" / "reference.md").mkdir(parents=True)
    (temp_repo / "docs" / "api" / "reference.md").write_text("# API Reference\n")
    (temp_repo / "mkdocs.yml").write_text("site_name: MyApp\n")

    # Observability
    (temp_repo / "logging.conf").write_text("""
[loggers]
keys=root
""")

    (temp_repo / ".sentryclirc").write_text("[auth]\ntoken=xxx\n")

    # Build tools
    (temp_repo / "Makefile").write_text("""
.PHONY: test install

test:
\tpoetry run pytest

install:
\tpoetry install
""")

    return temp_repo


@pytest.fixture(autouse=True)
def reset_registry() -> Generator[None, None, None]:
    """Reset the scanner registry before and after each test."""
    from agent_readiness_score.core.registry import ScannerRegistry

    # Clear before test
    ScannerRegistry.clear()

    # Re-import scanners to register them
    import agent_readiness_score.scanners  # noqa: F401

    yield

    # Clear after test
    ScannerRegistry.clear()
