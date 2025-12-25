# Agent Readiness Score Documentation

Welcome to the Agent Readiness Score documentation. This tool helps you measure and improve how well your repository supports AI agent-assisted development.

## What is Agent Readiness Score?

Agent Readiness Score is a CLI tool that analyzes your codebase and produces a score from 0-100 based on 8 weighted categories. These categories measure critical aspects of repository infrastructure that enable autonomous AI development workflows.

**Final Score Calculation:**
```
Score = Σ (Category Score × Category Weight)
```

## Why Does This Matter?

Modern AI coding agents (Claude, Cursor, GitHub Copilot, etc.) work best when repositories have:

- **Clear validation rules** - Linters and formatters catch errors before agents commit them
- **Reproducible environments** - Containers and dev environments ensure consistent behavior
- **Comprehensive tests** - Test suites let agents verify their changes work correctly
- **Strong typing** - Type hints and TypeScript configs help agents understand interfaces
- **Good documentation** - READMEs and docs provide essential context
- **Dependency management** - Lockfiles ensure reproducible builds
- **Build automation** - CI/CD pipelines validate changes automatically
- **Observability** - Logging and monitoring help debug agent-generated code

This tool quantifies these qualities and shows you exactly where to improve.

## Quick Navigation

### Getting Started
- [Installation](installation.md) - Install via pip, pipx, or from source
- [Usage](usage.md) - CLI commands and options
- [CI Integration](ci-integration.md) - GitHub Actions and pre-commit examples

### Understanding the Score
- [Scoring System](scoring-system.md) - How the algorithm works
- [Categories Overview](#category-breakdown) - What each category measures

### Categories (8 total)
1. [Testing (20%)](categories/testing.md) - Test frameworks, coverage, E2E tests
2. [Style & Validation (15%)](categories/style.md) - Linters, formatters, pre-commit
3. [Dev Environments (15%)](categories/devenv.md) - DevContainers, Docker, Nix
4. [Build Systems (10%)](categories/build.md) - CI/CD, build tools, automation
5. [Observability (10%)](categories/observability.md) - Logging, monitoring, APM
6. [Dependencies (10%)](categories/dependencies.md) - Lockfiles, security scanning
7. [Documentation (10%)](categories/documentation.md) - READMEs, docs, API specs
8. [Static Typing (10%)](categories/typing.md) - Type checkers, configs

### Advanced
- [Extending](extending.md) - Add custom scanners for your organization

## Category Breakdown

| Category | Weight | Focus Area | Why It Matters |
|----------|--------|------------|----------------|
| **Testing** | 20% | Test frameworks, coverage configs, test organization | Agents need tests to verify their changes work |
| **Style & Validation** | 15% | Linters, formatters, pre-commit hooks | Prevents agents from committing broken code |
| **Dev Environments** | 15% | DevContainers, Docker, reproducible setups | Ensures agents work in consistent environments |
| **Build Systems** | 10% | CI/CD pipelines, build automation | Validates agent changes automatically |
| **Observability** | 10% | Logging, monitoring, APM integrations | Helps debug agent-generated code |
| **Dependencies** | 10% | Lockfiles, security scanning, updates | Ensures reproducible builds |
| **Documentation** | 10% | READMEs, docs directories, API specs | Provides context for agents |
| **Static Typing** | 10% | Type checkers, TypeScript, type stubs | Helps agents understand interfaces |

## Grading Scale

Your final score is converted to a letter grade:

| Grade | Score Range | Interpretation |
|-------|-------------|----------------|
| **A** | 90-100 | **Excellent** - Ready for autonomous development. Repository has comprehensive infrastructure. |
| **B** | 80-89 | **Good** - Minor improvements recommended. Most best practices in place. |
| **C** | 70-79 | **Moderate** - Several areas need attention. Core infrastructure present but incomplete. |
| **D** | 60-69 | **Limited** - Significant gaps exist. Basic infrastructure missing. |
| **F** | 0-59 | **Poor** - Major infrastructure missing. Not suitable for agent-assisted development. |

## Multi-Language Support

Agent Readiness Score automatically detects your project's primary and secondary languages, then applies language-specific checks:

**Supported Languages:**
- Python, JavaScript, TypeScript, Go, Rust
- Ruby, Java, Kotlin, Swift, C#
- PHP, Elixir, Dart, C++, Haskell
- Scala, Zig, and more

**Language Detection:**
The tool analyzes your repository's file extensions and applies relevant scanners. For example:
- **Python projects** get checked for: mypy, pytest, poetry/pip lockfiles, py.typed markers
- **TypeScript projects** get checked for: tsconfig.json, ESLint, Jest/Vitest, npm lockfiles
- **Go projects** get checked for: go.mod/go.sum, golangci-lint, interfaces

## Quick Start Example

```bash
# Install
pip install agent-readiness-score

# Scan current directory
agent-ready scan .

# Get detailed output
agent-ready scan . --verbose

# Save JSON report
agent-ready scan . --json-file report.json

# Fail CI if score below 80
agent-ready scan . --min-score 80
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

## Common Use Cases

### 1. Pre-Development Assessment
Before starting AI agent-assisted development, scan your repository to identify gaps:
```bash
agent-ready scan . --verbose > readiness-report.txt
```

### 2. CI/CD Quality Gate
Enforce minimum readiness scores in your pipeline:
```bash
agent-ready scan . --min-score 70
```

### 3. Migration Tracking
Track progress as you improve your repository:
```bash
agent-ready scan . --json-file before.json
# Make improvements
agent-ready scan . --json-file after.json
# Compare scores
```

### 4. Organization Standards
Create custom scanners to enforce your organization's requirements:
```python
# See extending.md for details
@ScannerRegistry.register
class ComplianceScanner(BaseScanner):
    # ... custom checks
```

## Philosophy

Agent Readiness Score is based on three core principles:

1. **Measurable Quality** - Everything that matters can be quantified
2. **Actionable Feedback** - Results should tell you exactly what to improve
3. **Language Agnostic** - Good practices apply across all languages

The tool doesn't enforce a specific workflow or toolset. Instead, it recognizes that different ecosystems have different conventions (pytest vs Jest, mypy vs TypeScript, etc.) and scores you based on whether you're following best practices for your language.

## Next Steps

- **New Users**: Start with [Installation](installation.md)
- **Understanding Scores**: Read [Scoring System](scoring-system.md)
- **Improving Scores**: Review individual [Category Guides](categories/)
- **CI Integration**: Set up [automated checks](ci-integration.md)
- **Customization**: Learn about [extending the tool](extending.md)

## Support

- **Documentation**: You're reading it!
- **Issues**: [GitHub Issues](https://github.com/yourusername/agent-readiness-score/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/agent-readiness-score/discussions)
- **Contributing**: See [CONTRIBUTING.md](../CONTRIBUTING.md)

## License

MIT License - see [LICENSE](../LICENSE) for details.
