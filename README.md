# Agent Readiness Score

[![CI](https://github.com/yourusername/agent-readiness-score/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/agent-readiness-score/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

**Calculate how ready your repository is for AI agent-assisted development.**

Agent Readiness Score analyzes your codebase and produces a score from 0-100 based on 8 weighted categories that measure how well your repository supports autonomous AI development workflows.

## Why Agent Readiness?

AI coding agents work best when repositories have:
- **Clear validation rules** - Linters catch errors before agents commit them
- **Reproducible environments** - Containers ensure consistent behavior
- **Comprehensive tests** - Agents can verify their changes work
- **Strong typing** - Type hints help agents understand interfaces
- **Good documentation** - READMEs and docs provide context

This tool quantifies these qualities and shows you exactly where to improve.

## Quick Start

```bash
# Install
pip install agent-readiness-score

# Scan current directory
agent-ready scan .

# Scan with verbose output
agent-ready scan . --verbose

# Output JSON report
agent-ready scan . --json-file report.json
```

## Example Output

```
╭──────────────────── Agent Readiness Scan ────────────────────╮
│ Repository: /path/to/your/repo                               │
│ Languages: Python, TypeScript                                │
│ Scanned: 2024-12-25 10:30:00                                │
│ Duration: 45.2ms                                             │
╰──────────────────────────────────────────────────────────────╯

              Category Scores
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Category           ┃  Score ┃ Weight ┃ Weighted ┃ Progress   ┃  Found   ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━┩
│ Testing            │     85 │    20% │     17.0 │ ████████░░ │    12/14 │
│ Style Validation   │     90 │    15% │     13.5 │ █████████░ │    10/11 │
│ Dev Environments   │     70 │    15% │     10.5 │ ███████░░░ │     8/12 │
│ Build Systems      │     80 │    10% │      8.0 │ ████████░░ │     9/11 │
│ Observability      │     60 │    10% │      6.0 │ ██████░░░░ │     5/9  │
│ Dependencies       │     95 │    10% │      9.5 │ █████████░ │    10/11 │
│ Documentation      │     75 │    10% │      7.5 │ ███████░░░ │     8/11 │
│ Static Typing      │     88 │    10% │      8.8 │ ████████░░ │    11/13 │
└────────────────────┴────────┴────────┴──────────┴────────────┴──────────┘

╭────────────────── Agent Readiness Score ──────────────────╮
│                                                           │
│ Final Score: 80.8/100  Grade: B                          │
│ Good agent readiness - minor improvements recommended     │
╰───────────────────────────────────────────────────────────╯
```

## Scoring Categories

| Category | Weight | What It Measures |
|----------|--------|------------------|
| **Testing** | 20% | Test frameworks, coverage configs, test directories, E2E tests |
| **Style & Validation** | 15% | Linters (ESLint, Ruff), formatters (Prettier, Black), pre-commit hooks |
| **Dev Environments** | 15% | DevContainers, Docker Compose, Nix, reproducible setups |
| **Build Systems** | 10% | CI/CD pipelines, build tools, automation scripts |
| **Observability** | 10% | Logging configs, monitoring, APM integrations |
| **Dependencies** | 10% | Lockfiles, Dependabot/Renovate, security scanning |
| **Documentation** | 10% | README quality, docs directory, API specs, contribution guides |
| **Static Typing** | 10% | TypeScript configs, mypy, type stubs, py.typed markers |

## Grading Scale

| Grade | Score Range | Meaning |
|-------|-------------|---------|
| **A** | 90-100 | Excellent - Ready for autonomous development |
| **B** | 80-89 | Good - Minor improvements recommended |
| **C** | 70-79 | Moderate - Several areas need attention |
| **D** | 60-69 | Limited - Significant gaps exist |
| **F** | 0-59 | Poor - Major infrastructure missing |

## CLI Options

```bash
# Basic scan
agent-ready scan /path/to/repo

# Verbose mode (show all findings)
agent-ready scan . --verbose

# JSON output only
agent-ready scan . --output json

# Save JSON to file
agent-ready scan . --json-file results.json

# CI mode: fail if score below threshold
agent-ready scan . --min-score 80

# List all categories
agent-ready categories
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Agent Readiness Check

on: [push, pull_request]

jobs:
  readiness:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install agent-ready
        run: pip install agent-readiness-score

      - name: Check readiness score
        run: agent-ready scan . --min-score 70
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: agent-readiness
        name: Agent Readiness Check
        entry: agent-ready scan . --min-score 70
        language: system
        pass_filenames: false
        always_run: true
```

## Multi-Language Support

Agent Readiness Score automatically detects your project's languages and applies relevant checks:

- **Python**: mypy, pytest, poetry/pip lockfiles, py.typed markers
- **JavaScript/TypeScript**: ESLint, Jest/Vitest, tsconfig, npm/yarn/pnpm lockfiles
- **Go**: go.mod/go.sum, golangci-lint, Go interfaces
- **Rust**: Cargo.lock, clippy, rustfmt
- **Ruby**: RuboCop, Sorbet, Bundler lockfile
- **Java/Kotlin**: Gradle/Maven, JUnit, Checkstyle
- **Swift**: SwiftLint, XCTest, Package.resolved
- **C#**: .NET analyzers, NuGet lockfile, xUnit
- **And more**: PHP, Elixir, Dart, C++, Haskell, Scala, Zig

## Extending with Custom Scanners

Create custom scoring categories for your organization's needs:

```python
from agent_readiness_score.core.scanner import BaseScanner
from agent_readiness_score.core.models import Category
from agent_readiness_score.core.registry import ScannerRegistry

@ScannerRegistry.register
class SecurityScanner(BaseScanner):
    @property
    def category(self) -> Category:
        return Category.SECURITY  # Add to Category enum first

    @property
    def name(self) -> str:
        return "Security"

    def get_checks(self, lang_stats=None):
        return [
            ("SECURITY.md", ["SECURITY.md", ".github/SECURITY.md"], 1.5, None),
            ("Dependabot alerts", [".github/dependabot.yml"], 1.2, None),
            ("Secret scanning", [".gitleaks.toml", ".secretlintrc"], 1.0, None),
        ]
```

See [Extending Guide](docs/extending.md) for full documentation.

## Installation

### From PyPI (Recommended)

```bash
pip install agent-readiness-score
```

### With pipx (Isolated)

```bash
pipx install agent-readiness-score
```

### From Source

```bash
git clone https://github.com/yourusername/agent-readiness-score.git
cd agent-readiness-score
pip install -e .
```

## Requirements

- Python 3.10+
- No external dependencies required for scanning (pure Python)
- Rich (for console output)
- Typer (for CLI)

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
git clone https://github.com/yourusername/agent-readiness-score.git
cd agent-readiness-score
pip install -e ".[dev]"
pytest
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

Built for the AI agent era. Inspired by the need for repositories that work well with autonomous coding assistants like Claude, Cursor, and GitHub Copilot.

---

**Questions?** Open an issue or start a discussion.

**Found this useful?** Give it a star!
