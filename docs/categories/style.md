# Style & Validation Category (15% Weight)

The Style & Validation category measures your project's code quality enforcement infrastructure. Linters, formatters, and validation tools prevent AI agents from committing broken or non-compliant code.

## Why Style & Validation Matters for Agents

AI coding agents benefit immensely from automated validation because:

1. **Immediate Feedback** - Linters catch errors before commit
2. **Consistent Style** - Formatters ensure uniform code style
3. **Bug Prevention** - Static analysis catches common mistakes
4. **Standards Enforcement** - Automated checks enforce team conventions
5. **Reduced Review Burden** - Machines handle style, humans focus on logic

**Without validation tools, agents may commit code that:**
- Has syntax errors
- Violates style guidelines
- Contains common bugs (unused variables, undefined names)
- Fails organizational standards

## What This Category Checks

### Linters (Weight: 1.5-2.0)

Linters analyze code for potential errors and style violations.

#### Python

**Primary linters:**
- **Ruff** (modern, fast) - `.ruff.toml`, `ruff.toml`, `pyproject.toml` with `[tool.ruff]`
- **Pylint** - `.pylintrc`, `pylintrc`, `pyproject.toml` with `[tool.pylint]`
- **Flake8** - `.flake8`, `setup.cfg`, `tox.ini`

**Example .ruff.toml:**
```toml
target-version = "py310"
line-length = 100

[lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "B",    # flake8-bugbear
    "C4",   # flake8-comprehensions
]

[lint.isort]
known-first-party = ["myproject"]
```

#### JavaScript/TypeScript

**Primary linters:**
- **ESLint** - `.eslintrc.js`, `.eslintrc.json`, `.eslintrc.yml`, `eslint.config.js`
- **TSLint** (deprecated, but still checked) - `tslint.json`

**Example .eslintrc.json:**
```json
{
  "extends": ["eslint:recommended", "plugin:@typescript-eslint/recommended"],
  "parser": "@typescript-eslint/parser",
  "plugins": ["@typescript-eslint"],
  "rules": {
    "no-unused-vars": "error",
    "no-console": "warn",
    "@typescript-eslint/explicit-function-return-type": "error"
  }
}
```

#### Go

- **golangci-lint** - `.golangci.yml`, `.golangci.yaml`
- Built-in: `go vet`, `go fmt`

**Example .golangci.yml:**
```yaml
linters:
  enable:
    - gofmt
    - golint
    - govet
    - errcheck
    - staticcheck
    - unused
```

#### Rust

- **Clippy** - `clippy.toml`, `Cargo.toml` with workspace lints
- **rustfmt** - `rustfmt.toml`, `.rustfmt.toml`

#### Ruby

- **RuboCop** - `.rubocop.yml`

**Example .rubocop.yml:**
```yaml
AllCops:
  TargetRubyVersion: 3.0
  NewCops: enable

Style/StringLiterals:
  EnforcedStyle: double_quotes

Metrics/MethodLength:
  Max: 20
```

#### Other Languages

- **Java**: Checkstyle (`.checkstyle.xml`), PMD
- **C#**: `.editorconfig` with Roslyn analyzers
- **Swift**: SwiftLint (`.swiftlint.yml`)
- **PHP**: PHPCS (`phpcs.xml`)

### Formatters (Weight: 1.5)

Formatters automatically fix code style issues.

#### Python

- **Black** - `pyproject.toml` with `[tool.black]`
- **Ruff format** - `.ruff.toml` (also a linter)
- **autopep8** - `setup.cfg`, `.autopep8`

**Example pyproject.toml:**
```toml
[tool.black]
line-length = 100
target-version = ['py310', 'py311', 'py312']
include = '\.pyi?$'

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

#### JavaScript/TypeScript

- **Prettier** - `.prettierrc`, `.prettierrc.json`, `prettier.config.js`

**Example .prettierrc:**
```json
{
  "semi": true,
  "trailingComma": "all",
  "singleQuote": false,
  "printWidth": 100,
  "tabWidth": 2
}
```

#### Go

- **gofmt** / **gofumpt** - Built-in, configuration in CI

#### Rust

- **rustfmt** - `rustfmt.toml`, `.rustfmt.toml`

#### Other

- **clang-format** (C/C++) - `.clang-format`
- **Terraform fmt** - Built-in

### Pre-commit Hooks (Weight: 2.0)

Pre-commit hooks run checks before allowing commits, ensuring agents never commit bad code.

**Configuration files:**
- `.pre-commit-config.yaml` (pre-commit framework)
- `.husky/` directory (JavaScript/Node)
- `.git/hooks/pre-commit` (custom scripts)

**Example .pre-commit-config.yaml:**
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-merge-conflict

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.8
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v3.1.0
    hooks:
      - id: prettier
        types_or: [javascript, jsx, ts, tsx, json, yaml, markdown]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

**JavaScript/Husky:**
```json
// package.json
{
  "scripts": {
    "prepare": "husky install"
  },
  "devDependencies": {
    "husky": "^8.0.0",
    "lint-staged": "^15.0.0"
  },
  "lint-staged": {
    "*.{js,jsx,ts,tsx}": ["eslint --fix", "prettier --write"],
    "*.{json,md}": ["prettier --write"]
  }
}
```

### EditorConfig (Weight: 1.0)

`.editorconfig` ensures consistent editor settings across team members and IDEs.

**Example .editorconfig:**
```ini
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
indent_style = space
indent_size = 2

[*.py]
indent_size = 4

[*.go]
indent_style = tab

[Makefile]
indent_style = tab

[*.md]
trim_trailing_whitespace = false
```

### Import Sorting (Weight: 1.0)

Automatic import organization improves code readability.

**Python:**
- **isort** - `.isort.cfg`, `pyproject.toml` with `[tool.isort]`
- **Ruff** (includes isort) - `.ruff.toml`

**Example pyproject.toml:**
```toml
[tool.isort]
profile = "black"
line_length = 100
known_first_party = ["myproject"]
sections = ["FUTURE", "STDLIB", "THIRDPARTY", "FIRSTPARTY", "LOCALFOLDER"]
```

**JavaScript/TypeScript:**
- Built into ESLint or Prettier
- `eslint-plugin-import`

### Code Quality Tools (Weight: 1.2)

Advanced static analysis tools.

**Python:**
- **bandit** - Security linter (`.bandit`)
- **vulture** - Dead code detector
- **radon** - Code complexity analyzer

**JavaScript/TypeScript:**
- **SonarQube** - `sonar-project.properties`
- **CodeClimate** - `.codeclimate.yml`

**Multi-language:**
- **SonarQube** - `sonar-project.properties`
- **CodeQL** - `.github/workflows/codeql.yml`

### Documentation Linters (Weight: 0.5)

Ensure documentation quality.

**Markdown:**
- **markdownlint** - `.markdownlint.json`, `.markdownlintrc`

**Example .markdownlint.json:**
```json
{
  "default": true,
  "MD013": false,
  "MD033": false
}
```

**API Documentation:**
- **openapi-lint** for OpenAPI specs
- **spectral** for API design

## Scoring Examples

### Example 1: No Validation (Score: 0/100)

```
repo/
├── README.md
└── src/
    └── app.py
```

**Detected:** Nothing

**Missing:** All validation infrastructure

**Score:** 0/100
**Contribution:** 0 × 0.15 = 0

### Example 2: Basic Linting (Score: 40/100)

```
repo/
├── .ruff.toml          # ✓ Linter (2.0)
├── pyproject.toml      # (contains ruff config)
└── src/
    └── app.py
```

**Detected:**
- Ruff configuration (2.0)

**Missing:**
- Formatter
- Pre-commit hooks
- EditorConfig

**Score:** ~40/100
**Contribution:** 40 × 0.15 = 6.0

### Example 3: Good Validation (Score: 75/100)

```
repo/
├── .ruff.toml                  # ✓ Linter (2.0)
├── pyproject.toml              # ✓ Black config (1.5)
│   └── [tool.black]
├── .pre-commit-config.yaml     # ✓ Pre-commit (2.0)
├── .editorconfig               # ✓ EditorConfig (1.0)
└── src/
```

**Detected:**
- Ruff (2.0)
- Black (1.5)
- Pre-commit (2.0)
- EditorConfig (1.0)

**Missing:**
- Import sorting (if not in Ruff)
- Documentation linting

**Score:** ~75/100
**Contribution:** 75 × 0.15 = 11.25

### Example 4: Excellent Validation (Score: 95/100)

```
repo/
├── .ruff.toml                  # ✓ Linter + formatter (2.0)
├── .pre-commit-config.yaml     # ✓ Pre-commit (2.0)
├── .editorconfig               # ✓ EditorConfig (1.0)
├── .bandit                     # ✓ Security linter (1.2)
├── .markdownlint.json          # ✓ Docs linting (0.5)
└── src/
```

**Detected:** Nearly everything

**Score:** 95/100
**Contribution:** 95 × 0.15 = 14.25

## Improvement Roadmap

### Level 1: Basic Linting (Target: 40/100)

**Step 1:** Choose and configure a linter

```bash
# Python
pip install ruff
cat > .ruff.toml << 'EOF'
target-version = "py310"
line-length = 100

[lint]
select = ["E", "F", "I"]
EOF

# JavaScript
npm install --save-dev eslint
npx eslint --init
```

**Result:** Score ~40/100

### Level 2: Add Formatting (Target: 60/100)

**Step 2:** Add a formatter

```bash
# Python (Black)
pip install black
cat > pyproject.toml << 'EOF'
[tool.black]
line-length = 100
target-version = ['py310', 'py311']
EOF

# JavaScript (Prettier)
npm install --save-dev prettier
cat > .prettierrc << 'EOF'
{
  "semi": true,
  "singleQuote": false,
  "printWidth": 100
}
EOF
```

**Step 3:** Add EditorConfig

```bash
cat > .editorconfig << 'EOF'
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
indent_style = space
indent_size = 2

[*.py]
indent_size = 4
EOF
```

**Result:** Score ~60/100

### Level 3: Pre-commit Hooks (Target: 85/100)

**Step 4:** Set up pre-commit

```bash
# Python
pip install pre-commit
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.8
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
EOF

pre-commit install
```

**JavaScript:**
```bash
npm install --save-dev husky lint-staged
npx husky install
npx husky add .husky/pre-commit "npx lint-staged"

# Add to package.json:
"lint-staged": {
  "*.{js,ts}": ["eslint --fix", "prettier --write"]
}
```

**Result:** Score ~85/100

### Level 4: Excellence (Target: 95/100)

**Step 5:** Add security and documentation linting

```bash
# Security (Python)
pip install bandit
cat > .bandit << 'EOF'
[bandit]
exclude: /test,/tests
tests: B201,B301,B302,B303,B304,B305,B306
EOF

# Documentation
npm install --save-dev markdownlint-cli
cat > .markdownlint.json << 'EOF'
{
  "default": true,
  "MD013": false
}
EOF
```

**Result:** Score 95+/100

## Best Practices

### 1. Run Validators in CI

```yaml
# .github/workflows/lint.yml
name: Lint

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: pip install ruff black mypy

      - name: Run ruff
        run: ruff check .

      - name: Run black
        run: black --check .

      - name: Run mypy
        run: mypy src/
```

### 2. Auto-fix on Save (IDE Setup)

**VS Code settings.json:**
```json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true,
    "source.organizeImports": true
  },
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true
  },
  "[javascript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

### 3. Gradual Adoption

If inheriting legacy code:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.8
    hooks:
      - id: ruff
        args: [--fix]
        # Only check files changed in this commit
        stages: [commit]
```

Or use `--diff` flags to only check new code:
```bash
ruff check --diff  # Only check uncommitted changes
```

### 4. Document Exceptions

When you must ignore a rule:

```python
# Inline suppression with explanation
result = eval(user_input)  # noqa: S307 - Safe, input is validated above

# File-level suppression
# ruff: noqa: E501
```

## Common Pitfalls

### Pitfall 1: Conflicting Tools

**Problem:** Black and Flake8 disagree on line length.

**Solution:** Configure both consistently:
```toml
[tool.black]
line-length = 100

[tool.ruff]
line-length = 100
```

### Pitfall 2: Pre-commit Not Installed

**Problem:** `.pre-commit-config.yaml` exists but hooks not installed.

**Solution:**
```bash
pre-commit install
```

Better: Add to setup instructions:
```bash
# After cloning
pip install -e ".[dev]"
pre-commit install
```

### Pitfall 3: Too Strict Initially

**Problem:** Enabling all rules on legacy code causes 10,000 errors.

**Solution:** Start lenient, tighten gradually:
```toml
# .ruff.toml
[lint]
# Start with just errors
select = ["E", "F"]

# Add more over time
# select = ["E", "F", "W", "I", "B", "C4"]
```

### Pitfall 4: Ignoring CI Failures

**Problem:** Linter fails in CI but gets merged anyway.

**Solution:** Make CI blocking:
```yaml
# GitHub branch protection rules
- Require status checks to pass before merging
  - lint
  - format-check
```

## Integration with Agents

### How Agents Use Validation

1. **Before committing:** Agent runs linters to check generated code
2. **On failure:** Agent reads error messages and fixes issues
3. **Iterative refinement:** Agent re-runs checks until passing
4. **Learning:** Error patterns inform future code generation

### Example Agent Workflow

```
Agent generates code
    ↓
Runs: ruff check src/
    ↓
Error: "Undefined name 'foo'"
    ↓
Agent fixes: Defines 'foo'
    ↓
Runs: ruff check src/
    ✓ Pass
    ↓
Runs: black src/
    ✓ Formatted
    ↓
Runs: pytest
    ✓ Tests pass
    ↓
Commits
```

## Quick Wins

**30-minute setup:**

1. Choose primary linter for your language
2. Create config file with basic rules
3. Install pre-commit framework
4. Add linter + formatter to pre-commit
5. Run on codebase and fix errors

**Result:** Score increases dramatically (0 → 70+)

## Tool Recommendations

### Python
- **Best all-in-one:** Ruff (linting + formatting + import sorting)
- **Alternative:** Black + Flake8 + isort
- **Pre-commit:** pre-commit framework

### JavaScript/TypeScript
- **Linter:** ESLint with TypeScript plugin
- **Formatter:** Prettier
- **Pre-commit:** Husky + lint-staged

### Go
- **All-in-one:** golangci-lint
- **Built-in:** go fmt, go vet

### Rust
- **Linter:** Clippy
- **Formatter:** rustfmt

## Further Reading

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [ESLint Guide](https://eslint.org/docs/latest/)
- [Pre-commit Framework](https://pre-commit.com/)
- [EditorConfig](https://editorconfig.org/)

## Next Steps

- Review [Testing](testing.md) category
- Set up [CI Integration](../ci-integration.md)
- Learn about [Dev Environments](devenv.md)
