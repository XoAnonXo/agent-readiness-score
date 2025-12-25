# Contributing to Agent Readiness Score

Thank you for your interest in contributing to Agent Readiness Score! This document provides guidelines for contributing.

## Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/agent-readiness-score.git
cd agent-readiness-score

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Run tests to verify setup
pytest
```

## Code Quality

We use these tools for code quality:

- **Ruff** for linting and formatting
- **mypy** for type checking
- **pytest** for testing

Run all checks before submitting:

```bash
# Format code
ruff format .

# Check for issues
ruff check .

# Type check
mypy src/

# Run tests
pytest
```

## Making Changes

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following the code style
3. **Add tests** for new functionality
4. **Update documentation** if needed
5. **Ensure all checks pass**
6. **Submit a pull request**

## Pull Request Process

1. Update the README.md with details of changes if applicable
2. Update the CHANGELOG.md with your changes
3. Ensure CI passes
4. Request review from maintainers

## Adding a New Scanner

To add a new scanner for a category:

1. Create a new file in `src/agent_readiness_score/scanners/`
2. Inherit from `BaseScanner`
3. Use the `@ScannerRegistry.register` decorator
4. Define checks using helper functions (`universal()`, `py()`, `js()`, etc.)

Example:

```python
from agent_readiness_score.core.scanner import BaseScanner, Check, universal, py
from agent_readiness_score.core.models import Category, CategoryScore
from agent_readiness_score.core.registry import ScannerRegistry

@ScannerRegistry.register
class MyScanner(BaseScanner):
    @property
    def category(self) -> Category:
        return Category.MY_CATEGORY

    @property
    def name(self) -> str:
        return "My Scanner"

    def get_checks(self, lang_stats=None) -> list[Check]:
        return [
            universal("file.txt", name="My Check", weight=1.0),
        ]
```

## Adding Language Support

To add support for a new language:

1. Add the language to `Language` enum in `core/language.py`
2. Define detection patterns (file extensions, config files)
3. Add language-specific helper function to `core/scanner.py`
4. Update existing scanners with language-specific checks

## Reporting Bugs

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md) when filing issues.

Include:
- Python version
- OS and version
- Steps to reproduce
- Expected vs actual behavior

## Feature Requests

Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md).

Describe:
- The problem you're trying to solve
- Your proposed solution
- Alternatives you've considered

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## Questions?

Open a [discussion](https://github.com/yourusername/agent-readiness-score/discussions) for questions.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
